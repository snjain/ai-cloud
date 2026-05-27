"""Web search tool using Brave Search API."""
from httpx import AsyncClient


async def web_search_tool(query: str, http_client: AsyncClient, brave_api_key: str | None) -> str:
    """Search the web with Brave Search API.

    Args:
        query: The search query.
        http_client: Async HTTP client.
        brave_api_key: Brave Search API key.

    Returns:
        A formatted summary of the top search results.
    """
    if not brave_api_key:
        return "Error: Brave Search API key is not configured."

    headers = {
        "X-Subscription-Token": brave_api_key,
        "Accept": "application/json",
    }

    try:
        response = await http_client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={
                "q": query,
                "count": 5,
                "text_decorations": True,
                "search_lang": "en",
            },
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        web_results = data.get("web", {}).get("results", [])
        for item in web_results[:3]:
            title = item.get("title", "")
            description = item.get("description", "")
            url = item.get("url", "")
            if title and description:
                results.append(f"Title: {title}\nSummary: {description}\nSource: {url}\n")

        return "\n".join(results) if results else "No results found for the query."
    except Exception as e:
        return f"Error during web search: {e}"
