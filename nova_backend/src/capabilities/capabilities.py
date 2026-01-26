"""
NovaLIS Capability Declarations

This file defines static capability names used to describe what an
executor *could* support in the future.

IMPORTANT:
- Capabilities do NOT grant permission
- Capabilities do NOT enable execution
- Capabilities are declarative metadata only

Phase-2 status:
- Used for documentation and future matching
- No runtime logic depends on this file
"""

# File system capabilities
CAN_OPEN_FILE = "can_open_file"
CAN_OPEN_FOLDER = "can_open_folder"

# Application control
CAN_LAUNCH_APP = "can_launch_app"

# Web / information
CAN_WEB_LOOKUP = "can_web_lookup"

# Media routing (where, not what)
CAN_ROUTE_MEDIA = "can_route_media"
CAN_STOP_MEDIA = "can_stop_media"

# Task / reminder introspection
CAN_LIST_REMINDERS = "can_list_reminders"
CAN_CANCEL_REMINDER = "can_cancel_reminder"

# Device / system control (DECLARED ONLY — NOT ENABLED)
CAN_CONTROL_DEVICE = "can_control_device"

# Voice I/O (DECLARED ONLY — NOT ENABLED)
CAN_VOICE_INPUT = "can_voice_input"
CAN_VOICE_OUTPUT = "can_voice_output"
