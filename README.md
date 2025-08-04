# loki-mcp-server
A Python implementation an MCP server for Grafana Loki.

# How to add to Cursor
Add the following json to `mcp.json`:
```json
{
    "loki-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "<full-path-to>/loki-mcp-server",
        "run",
        "src/main.py"
      ]
    }
}
```