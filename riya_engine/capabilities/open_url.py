import webbrowser

from riya_engine.capabilities.base_response import CapabilityResponse


def execute(payload):

    url = payload.get("url")

    try:

        webbrowser.open(url)

        return CapabilityResponse(
            success=True,
            data={
                "url": url
            }
        )

    except Exception as e:

        return CapabilityResponse(
            success=False,
            error=str(e)
        )