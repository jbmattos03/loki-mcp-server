from server import mcp
from mcp.server.fastmcp import FastMCP
from logger import logger_config

def main():
    """
    Main entry point for the MCP server.
    Initializes the server and starts listening for requests.
    """
    logger = logger_config(process="main")
    
    logger.info("Starting Loki MCP server")
    mcp.run(transport="stdio")
    logger.info("Loki MCP server is running")

if __name__ == "__main__":
    main()
