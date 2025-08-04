from mcp.server.fastmcp import FastMCP
from logger import logger_config
from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass
from typing import Optional, Any, Dict, List
import requests
import time
import json
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
    limit: int = 100
    start: Optional[int] = None
    end: Optional[int] = None
    interval: Optional[str] = None # Log queries or queries that return a stream response
    step: Optional[str] = None # Metric queries or queries that return a matrix response
    direction: Optional[str] = "backward"

@mcp.tool(description="Query a range of logs from Loki")
def query_range(request: LokiRequest) -> List[Dict[Any, Any]]:
    """
    Query a range of logs from Loki.

    :param query: The Loki query string.
    :param limit: Maximum number of log entries to return.
    :param start: Start time in nanoseconds since epoch.
    :param end: End time in nanoseconds since epoch.
    :param interval: Interval for log queries (e.g., "5m", "1h"). Mutually exclusive with step.
    :param step: Step for metric queries (e.g., "1m"). Mutually exclusive with interval.
    :param direction: Direction of the query, either "forward" or "backward".
    :return: A list of dictionaries containing the query result.
    """
    # Get the Loki URL from the environment variables
    loki_url = getenv("LOKI_URL")

    try:
        # Handling timestamps (nanoseconds since epoch)
        end_timestamp = int(time.time() * 1_000_000_000)
        start_timestamp = int(end_timestamp - parse_interval(request.interval or request.step).total_seconds() * 1_000_000_000)

        # Construct the request using params
        params = {
            "query": request.query,
            "limit": request.limit,
            "start": request.start if request.start else start_timestamp,
            "end": request.end if request.end else end_timestamp,
            "direction": request.direction
        }
        if request.interval:
            params["interval"] = request.interval
        if request.step:
            params["step"] = request.step

        # Make the request to Loki
        logger.info(f"Querying Loki at {loki_url} with request: {request}")
        response = session.get(f"{loki_url}/loki/api/v1/query_range", params=params)
        response.raise_for_status() # Raise an error for bad responses

        # Return the result as a list of dictionaries
        result = response.json().get("data", {}).get("result", [])
        logger.info(f"Response from Loki: {json.dumps(result)}") # Log the response in json format
        return result
    except requests.RequestException as e:
        logger.error(f"Error querying Loki: {e}")
        return []