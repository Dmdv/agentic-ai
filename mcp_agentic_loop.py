import argparse
import asyncio
import gc
import json
import re
import sys
from typing import List, Dict, Any, Optional

from mlx_lm import load, generate
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

class MCPAgenticLoop:
    def __init__(self, model_name: str = "mlx-community/Qwen3-Coder-Next-80B-4bit"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        # We will populate this from the MCP server
        self.available_tools = []
        
        self.system_prompt_template = """You are an expert autonomous coding agent.
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
        
        # Apply the chat template
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
        """Looks for a JSON block in the response."""
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def _format_tools(self) -> str:
        descriptions = []
        for tool in self.available_tools:
            # MCP tools have a name, description, and inputSchema
            desc = f"- **{tool.name}**: {tool.description}\n  Schema: {json.dumps(tool.inputSchema)}"
            descriptions.append(desc)
        return "\n".join(descriptions)

    async def run(self, user_prompt: str, mcp_server_cmd: str, mcp_server_args: List[str]):
        print(f"Starting MCP Agentic Loop...")
        print(f"Connecting to MCP Server: {mcp_server_cmd} {' '.join(mcp_server_args)}")
        
        server_params = StdioServerParameters(
            command=mcp_server_cmd,
            args=mcp_server_args,
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Fetch available tools from the MCP server
                tools_response = await session.list_tools()
                self.available_tools = tools_response.tools
                
                print(f"Successfully connected to MCP Server.")
                print(f"Discovered Tools: {[t.name for t in self.available_tools]}")

                # Format system prompt with actual tools
                system_prompt = self.system_prompt_template.format(
                    tool_descriptions=self._format_tools()
                )
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Task: {user_prompt}"}
                ]
                
                max_iterations = 8
                
                for i in range(max_iterations):
                    print(f"\n--- Iteration {i+1} ---")
                    
                    # 1. Generate Model Output
                    # Note: mlx_lm generation is synchronous. For a robust async app, 
                    # this would be run in an executor, but it's fine for this loop.
                    response = self.generate_response(messages)
                    print(f"Agent Output:\n{response}")
                    
                    # Append agent response to history
                    messages.append({"role": "assistant", "content": response})
                    
                    # 2. Parse for Tools
                    tool_call = self.parse_tool_call(response)
                    
                    if tool_call:
                        tool_name = tool_call.get("tool")
                        tool_kwargs = tool_call.get("kwargs", {})
                        print(f"\n[Executing Tool via MCP]: {tool_name} with args {tool_kwargs}")
                        
                        try:
                            # 3. Execute Tool via MCP
                            result = await session.call_tool(tool_name, arguments=tool_kwargs)
                            
                            # Format the MCP result back to text for the LLM
                            result_text = "\n".join([c.text for c in result.content if hasattr(c, 'text')])
                            
                            print(f"[Tool Result]:\n{result_text[:500]}... (truncated if long)")
                            
                            messages.append({
                                "role": "user", 
                                "content": f"Tool '{tool_name}' result:\n{result_text}"
                            })
                            
                        except Exception as e:
                            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                            print(f"[Tool Error]: {error_msg}")
                            messages.append({
                                "role": "user", 
                                "content": error_msg
                            })
                    else:
                        print("\n[Finished]: No more tool calls. Task complete.")
                        break
                        
                # Clean up memory when done
                self._unload_model()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MLX Agentic Loop with an MCP Server.")
    parser.add_argument("--prompt", type=str, default="List the files in the current directory and read the contents of 'agentic_loop.py' to summarize it.",
                        help="The initial user prompt.")
    parser.add_argument("--model", type=str, default="mlx-community/Qwen3-Coder-Next-80B-4bit",
                        help="HuggingFace model ID (must be an MLX format model).")
    
    args = parser.parse_args()
    
    agent = MCPAgenticLoop(model_name=args.model)
    
    # Define the MCP server to start. We will use the official filesystem server via npx.
    # It requires an absolute path to the allowed directory.
    import os
    allowed_dir = os.path.abspath(".")
    
    try:
        asyncio.run(agent.run(
            user_prompt=args.prompt,
            mcp_server_cmd="npx",
            mcp_server_args=["-y", "@modelcontextprotocol/server-filesystem", allowed_dir]
        ))
    except KeyboardInterrupt:
        print("\nExiting...")
        agent._unload_model()
        sys.exit(0)
