from enum import Enum

class ActionType(str, Enum):
    """
    Phase-2 V1 allowed actions.
    """

    # Deterministic info actions
    GET_TIME = "get_time"      # ✅ Lowercase, not "GET_TIME"
    GET_DATE = "get_date"      # ✅ Lowercase, not "GET_DATE"

    # Phase-2 execution actions
    OPEN_APP = "open_app"      # ✅ OPEN_APP, not LAUNCH_APP
    OPEN_FOLDER = "open_folder"
    OPEN_VIEW = "open_view"
    VOLUME_CONTROL = "volume_control"

    # Phase-3 ONLY (explicitly deferred)
    OPEN_FILE = "open_file"  # ❌ Phase-3 only