from mcp.server.fastmcp import FastMCP
from logger import logger_config
from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass
from typing import Optional, Any
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
def query_range(request: LokiRequest) -> dict:
    """
    Query a range of logs from Loki.

    :param query: The Loki query string.
    :param start: Start time in milliseconds since epoch.
    :param end: End time in milliseconds since epoch.
    :return: A dictionary containing the query result "values".
    """
    # Get the Loki URL from the environment variables
    loki_url = getenv("LOKI_URL")

    # Handling timestamps
    end_timestamp = int(time.time() * 1_000_000_000)
    start_timestamp = int((end_timestamp - parse_interval(request.interval)) * 1_000_000_000)
    loki_request = LokiRequest(
        query=request.query,
        start=request.start if request.start is not None else start_timestamp,
        end=request.end if request.end is not None else end_timestamp
    )
    logger.info(f"Querying Loki at {loki_url} with request: {loki_request}")

    # Construct the request
    response = session.post(f"{loki_url}/loki/api/v1/query_range", 
                            json=loki_request.query,
                            data={"start": loki_request.start, "end": loki_request.end}
                            )
    logger.info(f"Loki response: {response.status_code} - {response.text}")

    return response.json().get("data", {}).get("result", [])