# riya_engine/capabilities/registry.py

from riya_engine.capabilities import open_app

from riya_engine.capabilities import close_app

from riya_engine.capabilities import open_url

from riya_engine.capabilities import search_youtube


CAPABILITY_REGISTRY = {

    "open_app": open_app.execute,

    "close_app": close_app.execute,

    "open_url": open_url.execute,

    "search_youtube": search_youtube.execute,

}