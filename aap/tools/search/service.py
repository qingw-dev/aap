import os
import traceback
from typing import Any

import httpx
from aworld.tools import FunctionTools
from dotenv import load_dotenv
from httpx._models import Response
from pydantic import Field
from pydantic.fields import FieldInfo

from aap.tools.search.views import GoogleSearchResult

from .views import Document, GoogleSearchResult

load_dotenv()

search_tools: FunctionTools = FunctionTools(
    name="search",
    description=(
        "Google Search API tools for fetching relevant documents given a user query."
    ),
)


@search_tools.tool(
    description=(
        "Search the web using Google Custom Search API "
        "and return a list of documents with url and summary."
    )
)
async def google_search(
    query: str = Field(..., description="The user query to search for"),
    num_results: int = Field(10, description="Number of search results to return"),
) -> GoogleSearchResult:
    """
    Use Google Custom Search API to fetch relevant documents for the user query.
    Returns a GoogleSearchResult with a list of documents (url, summary).
    """

    api_key: str | None = os.getenv("GOOGLE_API_KEY")
    cse_id: str | None = os.getenv("GOOGLE_CSE_ID")
    result: GoogleSearchResult = GoogleSearchResult(query=query)
    if not api_key or not cse_id:
        result.errors = ["Missing GOOGLE_API_KEY or GOOGLE_CSE_ID in environment."]
        return result

    try:
        params: dict[str, Any] = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": num_results.default if isinstance(num_results, FieldInfo) else 10,
            "language": "en",
            "country": "us",
        }
        response: Response = httpx.get(
            url="https://www.googleapis.com/customsearch/v1", params=params, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        result.execution_successful = True
        result.documents = [
            Document(url=item.get("link"), summary=item.get("snippet"))
            for item in data.get("items", [])
        ]
    except Exception:
        result.errors = [traceback.format_exc()]
        result.execution_successful = False
    return result
