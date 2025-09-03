from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
API_BASE = "https://api.hevyapp.com/v1"
USER_AGENT = "hevy-app/1.0"

async def make_hevy_request(url: str, payload: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Make a request to the Hevy API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, data=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_workouts(page: int, pageSize: int) -> str:
    """Get workouts for a user.

    Payload:
        page: Page number
        pageSize: Number of workouts per page
    """
    url = f"{API_BASE}/workouts"
    payload = {
        "page": page,
        "pageSize": pageSize
    }
    data = await make_hevy_request(url, payload)

    if not data or "workouts" not in data:
        return "Unable to fetch workouts or no workouts found."

    if not data["workouts"]:
        return "No workouts for this user."

    return "\n---\n".join(data["workouts"])

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')