import asyncio
import json
import sys
from duckduckgo_search import DDGS
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

app = Server("duckduckgo-search-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="web_search",
            description="Perform a free web search using DuckDuckGo to find recent information, documentation, or answers to errors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)."
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "web_search":
        query = arguments.get("query")
        max_results = arguments.get("max_results", 5)
        
        if not query:
            return [TextContent(type="text", text="Error: Query is required.")]
            
        try:
            results = DDGS().text(query, max_results=max_results)
            if not results:
                return [TextContent(type="text", text="No results found.")]
                
            formatted_results = "Search Results:\n\n"
            for i, res in enumerate(results):
                formatted_results += f"{i+1}. {res.get('title', 'No Title')}\n"
                formatted_results += f"URL: {res.get('href', 'No URL')}\n"
                formatted_results += f"Summary: {res.get('body', 'No Summary')}\n\n"
                
            return [TextContent(type="text", text=formatted_results)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error performing search: {str(e)}")]
            
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())