# riya_engine/capabilities/open_app.py

import subprocess

from riya_engine.capabilities.base_response import CapabilityResponse



APP_PATHS = {

    "chrome": r"C:\Users\dell\AppData\Local\Google\Chrome\Application\chrome.exe"

}


def execute(payload):

    app_name = payload.get("app_name")

    app_path = APP_PATHS.get(app_name)

    if not app_path:

        return CapabilityResponse(
            success=False,
            error=f"No path configured for app: {app_name}"
        )

    try:

        subprocess.Popen(app_path)

        # Return success — memory updates are handled by the
        # TASK_COMPLETED subscriber after the orchestrator confirms success.
        return CapabilityResponse(
            success=True,
            data={"app": app_name}
        )

    except Exception as e:

        return CapabilityResponse(
            success=False,
            error=str(e)
        )
