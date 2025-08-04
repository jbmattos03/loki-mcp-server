from mcp.server.fastmcp import FastMCP
from logger import logger_config
from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass
from typing import Optional, Any, Dict, List
import requests
import time
from parse_interval import parse_interval

load_dotenv()

# Check if the env variables are set
if not getenv("LOKI_URL"):
    raise ValueError("Missing environment variable: LOKI_URL")

# Initialize the logger
logger = logger_config(process="server")

# Initialize the FastMCP server
mcp = FastMCP("Loki MCP Server")

# Initialize requests session
session = requests.Session()

@dataclass
class LokiRequest:
    query: str
    start: Optional[int] = None
    end: Optional[int] = None
    interval: Optional[str] = None

@mcp.tool(description="Query a range of logs from Loki")
def query_range(request: LokiRequest) -> List[Dict[Any, Any]]:
    """
    Query a range of logs from Loki.

    :param query: The Loki query string.
    :param start: Start time in milliseconds since epoch.
    :param end: End time in milliseconds since epoch.
    :return: A dictionary containing the query result "values".
    """
    # Get the Loki URL from the environment variables
    loki_url = getenv("LOKI_URL")

    try:
        # Handling timestamps (nanoseconds since epoch)
        end_timestamp = int(time.time() * 1_000_000_000)
        start_timestamp = int(end_timestamp - parse_interval(request.interval).total_seconds() * 1_000_000_000)
        logger.info(f"Querying Loki at {loki_url} with request: {request}")

        # Construct the request using params
        params = {
            "query": request.query,
            "start": request.start if request.start else start_timestamp,
            "end": request.end if request.end else end_timestamp,
            "step": request.interval if request.interval else "1m"
        }
        response = session.get(f"{loki_url}/loki/api/v1/query_range", params=params)
        response.raise_for_status() # Raise an error for bad responses

        # Return the result as a list of dictionaries
        result = response.json().get("data", {}).get("result", [])
        logger.info(f"Response from Loki: {result}")
        return result
    except requests.RequestException as e:
        logger.error(f"Error querying Loki: {e}")
        return []