# @file constants.py
# Copyright (C) 2015  Metaswitch Networks Ltd

"""
Externally visible constants
"""

# This client uses interface version 3
INTERFACE_VERSION = 3

# The protocol version is fixed
PROTOCOL_VERSION = "v0.1"

# Message types
MESSAGE_INITIALISATION = 1
MESSAGE_TRAIL_ASSOCIATION = 2
MESSAGE_EVENT = 3
MESSAGE_MARKER = 4
MESSAGE_HEARTBEAT = 5
MESSAGE_STRINGS = {
    MESSAGE_INITIALISATION: "Init",
    MESSAGE_TRAIL_ASSOCIATION: "Trail association",
    MESSAGE_EVENT: "Event",
    MESSAGE_MARKER: "Marker",
    MESSAGE_HEARTBEAT: "Heartbeat",
}

# Scopes for Marker objects
SCOPE_NONE = 0
SCOPE_BRANCH = 1
SCOPE_TRACE = 2

# Flags for Marker objects
FLAG_ASSOCIATE = 1
FLAG_NO_REACTIVATE = 2

# Marker IDs
MARKER_ID_PROTOCOL_ERROR = 0x01000001
MARKER_ID_START = 0x01000003
MARKER_ID_END = 0x01000004
MARKER_ID_DIALED_DIGITS = 0x01000005
MARKER_ID_CALLING_DN = 0x01000006
MARKER_ID_CALLED_DN = 0x01000007

MARKER_ID_PRIMARY_DEVICE = 0x01000008  # Sometimes referred to as "subscriber number"

MARKER_ID_MVD_MOVABLE_BLOCK = 0x01000015
MARKER_ID_GENERIC_CORRELATOR = 0x01000016
MARKER_ID_FLUSH = 0x01000017

MARKER_ID_SIP_REGISTRATION = 0x010B0004
MARKER_ID_SIP_ALL_REGISTER = 0x010B0005
MARKER_ID_SIP_SUBSCRIBE_NOTIFY = 0x010B0006
MARKER_ID_SIP_CALL_ID = 0x010C0001
MARKER_ID_IMS_CHARGING_ID = 0x010C0002
MARKER_ID_VIA_BRANCH_PARAM = 0x010C0003

MARKER_ID_OUTBOUND_CALLING_URI = 0x05000003
MARKER_ID_INBOUND_CALLING_URI = 0x05000004
MARKER_ID_OUTBOUND_CALLED_URI = 0x05000005
MARKER_ID_INBOUND_CALLED_URI = 0x05000006

# For event IDs, see your resource bundle

# HTTP header for use in correlating HTTP requests
HTTP_BRANCH_HEADER_NAME = "X-SAS-HTTP-Branch-ID"
