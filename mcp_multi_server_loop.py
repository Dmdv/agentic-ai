import argparse
import asyncio
import gc
import json
import re
import sys
import os
from typing import List, Dict, Any, Optional

from mlx_lm import load, generate
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

class MCPAgenticLoop:
    def __init__(self, model_name: str = "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        # Dictionary to store sessions for multiple servers
        self.sessions = {}
        self.available_tools = {}
        
        self.system_prompt_template = """You are an expert autonomous coding agent running locally on an M3 Ultra via Apple MLX.
You have access to the following tools:
{tool_descriptions}

You must think step-by-step. 
To use a tool, output a JSON block wrapped in ```json ... ``` exactly like this:
```json
{{
  "tool": "tool_name",
  "kwargs": {{"param_name": "param_value"}}
}}
```

Wait for the tool result to be provided to you before continuing.
If you do not need to use a tool, output your final answer and explanation.
"""

    def _load_model(self):
        if self.model is None:
            print(f"Loading {self.model_name} into unified memory...")
            self.model, self.tokenizer = load(self.model_name)
            
    def _unload_model(self):
        if self.model is not None:
            print(f"Unloading {self.model_name} to free unified memory...")
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            gc.collect()

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        self._load_model()
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        print("\nThinking...")
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=2000,
            verbose=False
        )
        return response

    def parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def _format_tools(self) -> str:
        descriptions = []
        for server_name, tools in self.available_tools.items():
            descriptions.append(f"\n--- Tools from {server_name} ---")
            for tool in tools:
                desc = f"- **{tool.name}**: {tool.description}\n  Schema: {json.dumps(tool.inputSchema)}"
                descriptions.append(desc)
        return "\n".join(descriptions)

    async def setup_mcp_servers(self):
        """Initializes all required MCP servers."""
        allowed_dir = os.path.abspath(".")
        db_path = os.path.join(allowed_dir, "agent.db")
        
        # 1. Filesystem Server (Node/npx)
        fs_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", allowed_dir],
        )
        
        # 2. Git Server (Python/pip)
        git_params = StdioServerParameters(
            command="python3",
            args=["-m", "mcp_server_git", "--repository", allowed_dir],
        )
        
        # 3. SQLite Server (Python/pip)
        sqlite_params = StdioServerParameters(
            command="mcp-server-sqlite",
            args=["--db-path", db_path],
        )
        
        # 4. Fetch Server (Python/pip) - Better for direct RAG than Puppeteer
        fetch_params = StdioServerParameters(
            command="mcp-server-fetch",
            args=[],
        )
        
        # 5. Memory Server (Node/npx) - For multi-agent context sharing
        memory_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
        )

        servers = {
            "Filesystem": fs_params,
            "Git": git_params,
            "SQLite": sqlite_params,
            "Fetch": fetch_params,
            "Memory": memory_params
        }

        self.server_configs = servers

    async def execute_tool_call(self, tool_name: str, tool_kwargs: dict) -> str:
        target_server_name = None
        
        for server_name, tools in self.available_tools.items():
            if any(t.name == tool_name for t in tools):
                target_server_name = server_name
                break
                
        if not target_server_name:
            raise ValueError(f"Tool '{tool_name}' not found in any connected server.")

        params = self.server_configs[target_server_name]
        
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=tool_kwargs)
                return "\n".join([c.text for c in result.content if hasattr(c, 'text')])

    async def run(self, user_prompt: str):
        print(f"Starting Multi-Server MCP Agentic Loop...")
        
        await self.setup_mcp_servers()
        
        print("Discovering tools from servers...")
        for name, params in self.server_configs.items():
            try:
                async with stdio_client(params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools_response = await session.list_tools()
                        self.available_tools[name] = tools_response.tools
                        print(f"[{name}] discovered {len(tools_response.tools)} tools.")
            except Exception as e:
                print(f"Failed to connect to {name} server: {e}")

        system_prompt = self.system_prompt_template.format(
            tool_descriptions=self._format_tools()
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {user_prompt}"}
        ]
        
        max_iterations = 10
        
        for i in range(max_iterations):
            print(f"\n--- Iteration {i+1} ---")
            
            response = self.generate_response(messages)
            print(f"Agent Output:\n{response}")
            messages.append({"role": "assistant", "content": response})
            
            tool_call = self.parse_tool_call(response)
            
            if tool_call:
                tool_name = tool_call.get("tool")
                tool_kwargs = tool_call.get("kwargs", {})
                print(f"\n[Executing Tool via MCP]: {tool_name} with args {tool_kwargs}")
                
                try:
                    result_text = await self.execute_tool_call(tool_name, tool_kwargs)
                    print(f"[Tool Result]:\n{result_text[:1000]}... (truncated if long)")
                    messages.append({"role": "user", "content": f"Tool '{tool_name}' result:\n{result_text}"})
                except Exception as e:
                    error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                    print(f"[Tool Error]: {error_msg}")
                    messages.append({"role": "user", "content": error_msg})
            else:
                print("\n[Finished]: No more tool calls. Task complete.")
                break
                
        self._unload_model()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MLX Multi-Server Agentic Loop.")
    parser.add_argument("--prompt", type=str, default="Use the 'fetch' tool to read https://example.com and summarize it.",
                        help="The initial user prompt.")
    parser.add_argument("--model", type=str, default="mlx-community/Qwen2.5-Coder-32B-Instruct-4bit",
                        help="HuggingFace model ID (must be an MLX format model).")
    
    args = parser.parse_args()
    agent = MCPAgenticLoop(model_name=args.model)
    
    try:
        asyncio.run(agent.run(user_prompt=args.prompt))
    except KeyboardInterrupt:
        print("\nExiting...")
        agent._unload_model()
        sys.exit(0)
