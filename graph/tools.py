from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper

from mock.mock_order_api import get_order_status

# "wt-wt" (langchain default) is parsed as lang=wt by ddgs and breaks Wikipedia lookups.
# Use a real region and the duckduckgo backend only.
_search = DuckDuckGoSearchRun(
    api_wrapper=DuckDuckGoSearchAPIWrapper(region="us-en", backend="duckduckgo"),
)


@tool
def search_on_duckduckgo(query: str) -> str:
    """Search the web using DuckDuckGo and return relevant results for the query."""
    try:
        return _search.invoke(query)
    except Exception as exc:
        return f"Web search is temporarily unavailable: {exc}"


@tool
def get_order_tracking(order_id: str) -> dict:
    """Return delivery status and estimated delivery for a FarmFresh order ID."""
    return get_order_status(order_id=order_id)


TOOL_LIST = [
    search_on_duckduckgo,
    get_order_tracking,
]
