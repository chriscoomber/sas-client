import struct
import time
from metaswitch.sasclient.constants import *

RESOURCE_BUNDLE_BASE = 0x0F000000


class Message(object):
    """
    Message that can be sent to SAS. All messages are made of two parts, a header and a body, the format of which are
    specified by the VPED protocol. Strings are encoded as length + data, denoted by "1+n".

    The header is of the form:
    2 bytes - length of message (including header)
    1 byte - the protocol version
    1 byte - the message type
    8 bytes - the timestamp of the message (in ms) <- not present in heartbeat message

    The body varies depending on the message type - see implementations.
    """

    def __init__(self):
        self.timestamp = int(time.time() * 1000)
        self.msg_type = None

    def serialize_header(self, body_length):
        return struct.  pack('!hbbq', body_length + 12, INTERFACE_VERSION, self.msg_type, self.timestamp)

    def serialize_body(self):
        """
        Default implementation for messages with no body (e.g. heartbeat).
        """
        return struct.pack('')

    def serialize(self):
        """
        Convert the python message into a serialized string conforming to the VPED protocol.
        """
        body = self.serialize_body()
        header = self.serialize_header(len(body))
        return header + body


class Init(Message):
    """
    Message used when connecting to SAS. Not exposed to the user app.
    The body is of the form:
    1+n bytes - system name
    4 bytes - number 1 in native endian
    1+n bytes - protocol version
    1+n bytes - system type (e.g. sprout)
    1+n bytes - resource bundle ID
    1+n bytes - resource version (currently not implemented)
    """
    msg_type = MESSAGE_INITIALISATION

    def __init__(self, system_name, system_type, resource_identifier, resource_version=''):
        super(Init, self).__init__()
        self.system_name = system_name
        self.system_type = system_type
        self.resource_identifier = resource_identifier
        self.resource_version = resource_version
        self.msg_type = Init.msg_type

    def serialize_body(self):
        return ''.join([
                pack_string(self.system_name),
                struct.pack('=i', 1),
                pack_string(PROTOCOL_VERSION),
                pack_string(self.system_type),
                pack_string(self.resource_identifier),
                pack_string(self.resource_version)])


def pack_string(string):
    """
    Pack a string with its length.
    """
    data = string.encode('UTF-8') if isinstance(string, unicode) else str(string)
    return struct.pack('b', len(data)) + data


class TrailAssoc(Message):
    """
    Message used to associate trails manually.
    The body is of the form:
    8 bytes - trail A
    8 bytes - trail B
    1 byte - scope
    """
    msg_type = MESSAGE_TRAIL_ASSOCIATION

    def __init__(self, trail_a, trail_b, scope):
        super(TrailAssoc, self).__init__()
        self.trail_a_id = trail_a.get_trail_id()
        self.trail_b_id = trail_b.get_trail_id()
        self.scope = scope
        self.msg_type = TrailAssoc.msg_type

    def serialize_body(self):
        return struct.pack(
                '!qqb',
                self.trail_a_id,
                self.trail_b_id,
                self.scope)


class DataMessage(Message):
    """
    Message with included variable and static parameters. These consist of a header, the message-type-specific variables
    (in a fixed order) - see implementations, and then:
    2 bytes - length of static parameters
    4 bytes - static parameter 1
    4 bytes - static parameter 2
    ...etc.
    2 + n bytes - variable length parameter 1 (+ length)
    2 + n bytes - variable length parameter 2 (+ length)
    ...etc.
    """
    def __init__(self, static_params, var_params):
        super(DataMessage, self).__init__()
        self.static_params = static_params
        self.var_params = [var_param.encode('UTF-8') if isinstance(var_param, unicode) else str(var_param)
                           for var_param in var_params]

    def serialize_params(self):
        static_data = ''.join([struct.pack('=i', static_param) for static_param in self.static_params])
        static_data = struct.pack('!h', len(static_data)) + static_data

        var_data = ''.join([struct.pack('!h', len(var_param)) + str(var_param) for var_param in self.var_params])

        return static_data + var_data

    def add_static_params(self, static_params):
        """
        Appends provided params to event's static-length params.
        :param static_params: list of static params
        :return: self, for fluent interface
        """
        self.static_params += static_params
        return self

    def add_variable_params(self, var_params):
        """
        Appends provided params to event's variable-length params.
        :param variable: list of variable params
        :return: self, for fluent interface
        """
        self.var_params += var_params
        return self


class Event(DataMessage):
    """
    Message used to indicate that something has happened.
    The body is of the form:
    8 bytes - trail ID
    4 bytes - event ID - because we use interface version 3, we need to bitwise OR this with RESOURCE_BUNDLE_BASE
    4 bytes - instance ID (unique in codebase, to see from where this event was called)
    static and variable params (see above)
    """
    msg_type = MESSAGE_EVENT

    def __init__(self, trail, event_id, instance_id=0, static_params=None, var_params=None):
        if not var_params:
            var_params = []
        if not static_params:
            static_params = []
        super(Event, self).__init__(static_params, var_params)
        self.trail_id = trail.get_trail_id()
        self.event_id = event_id
        self.instance_id = instance_id
        self.msg_type = Event.msg_type

    def serialize_body(self):
        return struct.pack('!qii', self.trail_id, self.event_id | RESOURCE_BUNDLE_BASE, self.instance_id) + self.serialize_params()

    def set_instance_id(self, instance_id):
        """
        :param instance_id: instance id for identifying this SAS message from within the NE code
        :return: self, for fluent interface
        """
        self.instance_id = instance_id
        return self


class Marker(DataMessage):
    """
    Message used to provide metadata about the trails.
    The body is of the form:
    8 bytes - trail ID
    4 bytes - marker ID
    4 bytes - instance ID
    1 byte - flags, where FLAG_ASSOCIATE should be set if scope is not SCOPE_NONE, and if this is the case
             FLAG_NO_REACTIVATE may also be set
    1 byte - scope
    """
    msg_type = MESSAGE_MARKER

    def __init__(self, trail, marker_id, instance_id=0, reactivate=True, scope=SCOPE_NONE, static_params=None, var_params=None):
        if not var_params:
            var_params = []
        if not static_params:
            static_params = []
        super(Marker, self).__init__(static_params, var_params)
        self.trail_id = trail.get_trail_id()
        self.marker_id = marker_id
        self.instance_id = instance_id
        self.reactivate = reactivate
        self.scope = scope
        self.msg_type = Marker.msg_type

    def serialize_body(self):
        flags = 0
        if self.scope != SCOPE_NONE:
            flags |= FLAG_ASSOCIATE
            if not self.reactivate:
                flags |= FLAG_NO_REACTIVATE
        return struct.pack('!qiibb', self.trail_id, self.marker_id, self.instance_id, flags, self.scope) + self.serialize_params()

    def set_association_scope(self, scope):
        """
        :param scope: association scope
        :return: self, for fluent interface
        """
        self.scope = scope
        return self

    def set_reactivate(self, reactivate):
        """
        :param reactivate: reactivate flag (boolean)
        :return: self, for fluent interface
        """
        self.reactivate = reactivate
        return self

    def set_instance_id(self, instance_id):
        """
        :param instance_id: instance id for identifying this SAS message from within the NE code
        :return: self, for fluent interface
        """
        self.instance_id = instance_id
        return self


class Heartbeat(Message):
    """
    Message used to keep the connection alive. Consists of just the message header, without the timestamp.
    """
    msg_type = MESSAGE_HEARTBEAT

    def __init__(self):
        super(Heartbeat, self).__init__()
        self.msg_type = Heartbeat.msg_type

    def serialize_header(self, body_length):
        return struct.pack('!hbb', body_length + 4, INTERFACE_VERSION, self.msg_type)
