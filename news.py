from typing import Any
from datetime import datetime, timezone
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("news")

# Constants
NEWS_API_BASE = "https://newsapi.org/v2/everything"
USER_AGENT = "news-app/1.0"
NEWS_API_KEY = "64e3fb961bcc462289f8ee6edebe31f8"

async def make_news_request(params: dict[str, Any]) -> dict[str, Any] | None:
    """Make a request to the News API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {NEWS_API_KEY}",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(NEWS_API_BASE, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_article(article: dict) -> str:
    """Format a news article into a readable string."""
    return f"""
Title: {article.get('title', 'No Title')}
Description: {article.get('description', 'No Description')}
URL: {article.get('url', 'No URL')}
Published At: {article.get('publishedAt', 'Unknown')}
"""


@mcp.tool()
async def get_news(q: str = None, from_date: str = None, to_date: str = None, sources: str = "abc-news", page_size: int = 5) -> str:
    """Search news articles based on keyword, date range, and source.

    Args:
        q: Search query keyword
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        sources: News source identifier (default: "abc-news")
        page_size: Number of articles to retrieve (max 100)
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    from_date = from_date or today_str
    to_date = to_date or today_str
    sources = sources

    params = {
        "q": q,
        "from": from_date,
        "to": to_date,
        "sources": sources,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "language": "en",
    }

    data = await make_news_request(params)

    if not data or "articles" not in data:
        return "Unable to fetch news articles."

    if not data["articles"]:
        return "No news articles found for the given query and dates."

    articles = [format_article(article) for article in data["articles"]]
    return "\n---\n".join(articles)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')