from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.execution.execute_action import execute_action


def run(name, fn):
    print(f"\n=== {name} ===")
    try:
        result = fn()
        print(result)
    except Exception as e:
        print("EXCEPTION:", e)


# 1) Invalid input (boundary test)
run(
    "Invalid request type",
    lambda: execute_action("bad")
)

# 2) Unsupported ActionType (exists but not mapped)
run(
    "Unsupported ActionType (OPEN_FILE)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FILE,
            title="Open file",
            payload={"path": "C:\\temp\\x.txt"},
        )
    )
)

# 3) LAUNCH_APP with disallowed app_id (safe)
run(
    "LAUNCH_APP disallowed app_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.LAUNCH_APP,
            title="Launch app",
            payload={"app_id": "not_allowed"},
        )
    )
)

# 4) OPEN_FOLDER with disallowed folder_id (safe)
run(
    "OPEN_FOLDER disallowed folder_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open folder",
            payload={"folder_id": "not_allowed"},
        )
    )
)

# 5) GET_TIME
run(
    "GET_TIME",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.GET_TIME,
            title="Get time",
            payload={},
        )
    )
)

# 6) GET_DATE
run(
    "GET_DATE",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.GET_DATE,
            title="Get date",
            payload={},
        )
    )
)

# 7) VOLUME_CONTROL — valid absolute level
run(
    "VOLUME_CONTROL set level",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.VOLUME_CONTROL,
            title="Set volume",
            payload={"level": 30},
        )
    )
)

# 8) VOLUME_CONTROL — valid delta
run(
    "VOLUME_CONTROL adjust delta",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.VOLUME_CONTROL,
            title="Adjust volume",
            payload={"delta": -5},
        )
    )
)

# 9) VOLUME_CONTROL — invalid payload (both provided)
run(
    "VOLUME_CONTROL invalid payload (level + delta)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.VOLUME_CONTROL,
            title="Invalid volume payload",
            payload={"level": 30, "delta": -5},
        )
    )
)

# 10) VOLUME_CONTROL — out-of-bounds level
run(
    "VOLUME_CONTROL out-of-bounds level",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.VOLUME_CONTROL,
            title="Too loud",
            payload={"level": 150},
        )
    )
)
# 11) LAUNCH_APP — allowed app (happy path)
run(
    "LAUNCH_APP allowed app (notepad)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.LAUNCH_APP,
            title="Launch notepad",
            payload={"app_id": "notepad"},
        )
    )
)
# 12) OPEN_FOLDER — allowed folder (documents)
run(
    "OPEN_FOLDER allowed folder (documents)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open documents",
            payload={"folder_id": "documents"},
        )
    )
)

from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.execution.execute_action import execute_action


def run(name, fn):
    print(f"\n=== {name} ===")
    try:
        result = fn()
        print(result)
    except Exception as e:
        print("EXCEPTION:", e)


# --------------------------------------------------
# OPEN_FOLDER — Phase-2 V1 (happy path)
# --------------------------------------------------

run(
    "OPEN_FOLDER allowed folder (documents)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open documents",
            payload={"folder_id": "documents"},
        )
    )
)

# --------------------------------------------------
# OPEN_VIEW — Phase-2 V1 tests
# --------------------------------------------------

# 1) Missing payload
run(
    "OPEN_VIEW missing view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open view",
            payload={},
        )
    )
)

# 2) Disallowed view_id
run(
    "OPEN_VIEW disallowed view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open unknown view",
            payload={"view_id": "not_allowed"},
        )
    )
)

# 3) Allowed view (happy path)
run(
    "OPEN_VIEW allowed view (dashboard)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open dashboard",
            payload={"view_id": "dashboard"},
        )
    )
)

# 4) Payload sent to wrong ActionType (routing guard)
run(
    "OPEN_VIEW payload sent to wrong ActionType",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Wrong type",
            payload={"view_id": "dashboard"},
        )
    )
)

from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.execution.execute_action import execute_action


def run(name, fn):
    print(f"\n=== {name} ===")
    try:
        result = fn()
        print(result)
    except Exception as e:
        print("EXCEPTION:", e)


# --------------------------------------------------
# OPEN_FOLDER — Phase-2 V1 (happy path)
# --------------------------------------------------

run(
    "OPEN_FOLDER allowed folder (documents)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open documents",
            payload={"folder_id": "documents"},
        )
    )
)

# --------------------------------------------------
# OPEN_VIEW — Phase-2 V1 tests
# --------------------------------------------------

# 1) Missing payload
run(
    "OPEN_VIEW missing view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open view",
            payload={},
        )
    )
)

# 2) Disallowed view_id
run(
    "OPEN_VIEW disallowed view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open unknown view",
            payload={"view_id": "not_allowed"},
        )
    )
)

# 3) Allowed view (happy path)
run(
    "OPEN_VIEW allowed view (dashboard)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open dashboard",
            payload={"view_id": "dashboard"},
        )
    )
)

# 4) Payload sent to wrong ActionType (routing guard)
run(
    "OPEN_VIEW payload sent to wrong ActionType",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Wrong type",
            payload={"view_id": "dashboard"},
        )
    )
)

from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.execution.execute_action import execute_action


def run(name, fn):
    print(f"\n=== {name} ===")
    try:
        result = fn()
        print(result)
    except Exception as e:
        print("EXCEPTION:", e)


# --------------------------------------------------
# OPEN_FOLDER — Phase-2 V1 (happy path)
# --------------------------------------------------

run(
    "OPEN_FOLDER allowed folder (documents)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open documents",
            payload={"folder_id": "documents"},
        )
    )
)

# --------------------------------------------------
# OPEN_VIEW — Phase-2 V1 tests
# --------------------------------------------------

# 1) Missing payload
run(
    "OPEN_VIEW missing view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open view",
            payload={},
        )
    )
)

# 2) Disallowed view_id
run(
    "OPEN_VIEW disallowed view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open unknown view",
            payload={"view_id": "not_allowed"},
        )
    )
)

# 3) Allowed view (happy path)
run(
    "OPEN_VIEW allowed view (dashboard)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open dashboard",
            payload={"view_id": "dashboard"},
        )
    )
)

# 4) Payload sent to wrong ActionType (routing guard)
run(
    "OPEN_VIEW payload sent to wrong ActionType",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Wrong type",
            payload={"view_id": "dashboard"},
        )
    )
)

from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.execution.execute_action import execute_action


def run(name, fn):
    print(f"\n=== {name} ===")
    try:
        result = fn()
        print(result)
    except Exception as e:
        print("EXCEPTION:", e)


# --------------------------------------------------
# OPEN_FOLDER — Phase-2 V1 (happy path)
# --------------------------------------------------

run(
    "OPEN_FOLDER allowed folder (documents)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open documents",
            payload={"folder_id": "documents"},
        )
    )
)

# --------------------------------------------------
# OPEN_VIEW — Phase-2 V1 tests
# --------------------------------------------------

# 1) Missing payload
run(
    "OPEN_VIEW missing view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open view",
            payload={},
        )
    )
)

# 2) Disallowed view_id
run(
    "OPEN_VIEW disallowed view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open unknown view",
            payload={"view_id": "not_allowed"},
        )
    )
)

# 3) Allowed view (happy path)
run(
    "OPEN_VIEW allowed view (dashboard)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open dashboard",
            payload={"view_id": "dashboard"},
        )
    )
)

# 4) Payload sent to wrong ActionType (routing guard)
run(
    "OPEN_VIEW payload sent to wrong ActionType",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Wrong type",
            payload={"view_id": "dashboard"},
        )
    )
)

print("\nDone.")
from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.execution.execute_action import execute_action


def run(name, fn):
    print(f"\n=== {name} ===")
    try:
        result = fn()
        print(result)
    except Exception as e:
        print("EXCEPTION:", e)


# --------------------------------------------------
# OPEN_FOLDER — Phase-2 V1 (happy path)
# --------------------------------------------------

run(
    "OPEN_FOLDER allowed folder (documents)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open documents",
            payload={"folder_id": "documents"},
        )
    )
)

# --------------------------------------------------
# OPEN_VIEW — Phase-2 V1 tests
# --------------------------------------------------

# 1) Missing payload
run(
    "OPEN_VIEW missing view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open view",
            payload={},
        )
    )
)

# 2) Disallowed view_id
run(
    "OPEN_VIEW disallowed view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open unknown view",
            payload={"view_id": "not_allowed"},
        )
    )
)

# 3) Allowed view (happy path)
run(
    "OPEN_VIEW allowed view (dashboard)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open dashboard",
            payload={"view_id": "dashboard"},
        )
    )
)

# 4) Payload sent to wrong ActionType (routing guard)
run(
    "OPEN_VIEW payload sent to wrong ActionType",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Wrong type",
            payload={"view_id": "dashboard"},
        )
    )
)

print("\nDone.")
from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.execution.execute_action import execute_action


def run(name, fn):
    print(f"\n=== {name} ===")
    try:
        result = fn()
        print(result)
    except Exception as e:
        print("EXCEPTION:", e)


# --------------------------------------------------
# OPEN_FOLDER — Phase-2 V1 (happy path)
# --------------------------------------------------

run(
    "OPEN_FOLDER allowed folder (documents)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open documents",
            payload={"folder_id": "documents"},
        )
    )
)

# --------------------------------------------------
# OPEN_VIEW — Phase-2 V1 tests
# --------------------------------------------------

# 1) Missing payload
run(
    "OPEN_VIEW missing view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open view",
            payload={},
        )
    )
)

# 2) Disallowed view_id
run(
    "OPEN_VIEW disallowed view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open unknown view",
            payload={"view_id": "not_allowed"},
        )
    )
)

# 3) Allowed view (happy path)
run(
    "OPEN_VIEW allowed view (dashboard)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open dashboard",
            payload={"view_id": "dashboard"},
        )
    )
)

# 4) Payload sent to wrong ActionType (routing guard)
run(
    "OPEN_VIEW payload sent to wrong ActionType",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Wrong type",
            payload={"view_id": "dashboard"},
        )
    )
)

from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.execution.execute_action import execute_action


def run(name, fn):
    print(f"\n=== {name} ===")
    try:
        result = fn()
        print(result)
    except Exception as e:
        print("EXCEPTION:", e)


# --------------------------------------------------
# OPEN_FOLDER — Phase-2 V1 (happy path)
# --------------------------------------------------

run(
    "OPEN_FOLDER allowed folder (documents)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Open documents",
            payload={"folder_id": "documents"},
        )
    )
)

# --------------------------------------------------
# OPEN_VIEW — Phase-2 V1 tests
# --------------------------------------------------

# 1) Missing payload
run(
    "OPEN_VIEW missing view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open view",
            payload={},
        )
    )
)

# 2) Disallowed view_id
run(
    "OPEN_VIEW disallowed view_id",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open unknown view",
            payload={"view_id": "not_allowed"},
        )
    )
)

# 3) Allowed view (happy path)
run(
    "OPEN_VIEW allowed view (dashboard)",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_VIEW,
            title="Open dashboard",
            payload={"view_id": "dashboard"},
        )
    )
)

# 4) Payload sent to wrong ActionType (routing guard)
run(
    "OPEN_VIEW payload sent to wrong ActionType",
    lambda: execute_action(
        ActionRequest(
            action_type=ActionType.OPEN_FOLDER,
            title="Wrong type",
            payload={"view_id": "dashboard"},
        )
    )
)


print("\nDone.")