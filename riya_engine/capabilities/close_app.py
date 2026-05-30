# riya_engine/capabilities/close_app.py

import subprocess

from riya_engine.capabilities.base_response import CapabilityResponse


PROCESS_NAMES = {

    "chrome": "chrome.exe"

}


def execute(payload):

    app_name = payload.get("app_name")

    process_name = PROCESS_NAMES.get(app_name)

    if not process_name:

        return CapabilityResponse(
            success=False,
            error=f"No process configured for app: {app_name}"
        )

    try:

        subprocess.run(
            ["taskkill", "/F", "/IM", process_name],
            capture_output=True,
            text=True
        )

        return CapabilityResponse(
            success=True,
            data={
                "closed_app": app_name
            }
        )

    except Exception as e:

        return CapabilityResponse(
            success=False,
            error=str(e)
        )