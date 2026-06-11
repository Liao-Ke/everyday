import os

_JINSHAN_CACHE = None
_SEARCH_CACHE = None


def get_jinshan_cached():
    global _JINSHAN_CACHE
    if _JINSHAN_CACHE is None:
        from utils.web_search import get_jinshan

        _JINSHAN_CACHE = get_jinshan()
    return _JINSHAN_CACHE


def get_search_cached():
    global _SEARCH_CACHE
    if _SEARCH_CACHE is None:
        from utils.web_search import web_search

        jinshan = get_jinshan_cached()
        if jinshan and jinshan.get("note"):
            _SEARCH_CACHE = web_search(
                api_key=os.getenv("API_KEY"),
                search_query=jinshan["note"],
                search_engine="search_pro",
                content_size="high",
                search_intent=True,
            )
        else:
            _SEARCH_CACHE = {}
    return _SEARCH_CACHE
