import webbrowser
import urllib.parse

from riya_engine.capabilities.base_response import CapabilityResponse


def execute(payload):

    query = payload.get("query")

    encoded_query = urllib.parse.quote(query)

    url = f"https://www.youtube.com/results?search_query={encoded_query}"

    try:

        webbrowser.open(url)

        return CapabilityResponse(
            success=True,
            data={
                "query": query
            }
        )

    except Exception as e:

        return CapabilityResponse(
            success=False,
            error=str(e)
        )