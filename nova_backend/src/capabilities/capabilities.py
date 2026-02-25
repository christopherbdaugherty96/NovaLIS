"""
NovaLIS capability declarations.

This module contains static capability identifiers used as declarative metadata.
These constants do not grant permission and do not enable execution by themselves.
"""

# File system capabilities
CAN_OPEN_FILE = "can_open_file"
CAN_OPEN_FOLDER = "can_open_folder"

# Application control
CAN_LAUNCH_APP = "can_launch_app"

# Web / information
CAN_WEB_LOOKUP = "can_web_lookup"

# Media routing
CAN_ROUTE_MEDIA = "can_route_media"
CAN_STOP_MEDIA = "can_stop_media"

# Task / reminder introspection
CAN_LIST_REMINDERS = "can_list_reminders"
CAN_CANCEL_REMINDER = "can_cancel_reminder"

# Device / system control (declared only)
CAN_CONTROL_DEVICE = "can_control_device"

# Voice I/O (declared only)
CAN_VOICE_INPUT = "can_voice_input"
CAN_VOICE_OUTPUT = "can_voice_output"
