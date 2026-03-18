import argparse
import time
import gc
import json
import re
from typing import List, Dict, Any

from mlx_lm import load, generate

class AgenticLoop:
    def __init__(self, model_name: str = "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        # System prompt designed to force standard tool-calling output
        self.system_prompt = """You are an expert autonomous coding agent. 
You will be given a task and a list of available tools.
You must think step-by-step. 

To use a tool, output a JSON block wrapped in ```json ... ``` exactly like this:
```json
{
  "tool": "read_file",
  "kwargs": {"path": "src/main.py"}
}
```

If you do not need to use a tool, output your final answer.
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
        
        # Apply the chat template (Qwen format)
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
            max_tokens=1000,
            verbose=False
        )
        return response

    def parse_tool_call(self, response: str) -> Any:
        """Looks for a JSON block in the response."""
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def run(self, user_prompt: str):
        print(f"Starting Agentic Loop for task: '{user_prompt}'")
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Available tools: ['read_file']\n\nTask: {user_prompt}"}
        ]
        
        max_iterations = 5
        
        for i in range(max_iterations):
            print(f"\n--- Iteration {i+1} ---")
            
            # 1. Generate Model Output
            response = self.generate_response(messages)
            print(f"Agent Output:\n{response}")
            
            # Append agent response to history
            messages.append({"role": "assistant", "content": response})
            
            # 2. Parse for Tools
            tool_call = self.parse_tool_call(response)
            
            if tool_call:
                tool_name = tool_call.get("tool")
                print(f"\n[Executing Tool]: {tool_name} with args {tool_call.get('kwargs')}")
                
                # Mock Tool Execution
                if tool_name == "read_file":
                    mock_result = "def hello_world():\n    print('Hello World')\n"
                    print(f"[Tool Result]: {mock_result}")
                    messages.append({
                        "role": "user", 
                        "content": f"Tool '{tool_name}' result:\n{mock_result}"
                    })
                else:
                    messages.append({
                        "role": "user", 
                        "content": f"Error: Tool '{tool_name}' not found."
                    })
            else:
                print("\n[Finished]: No more tool calls. Task complete.")
                break
                
        # Clean up memory when done
        self._unload_model()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MLX Agentic Loop.")
    parser.add_argument("--prompt", type=str, default="Read the file 'src/main.py' and tell me what it does.",
                        help="The initial user prompt.")
    
    args = parser.parse_args()
    
    agent = AgenticLoop()
    agent.run(args.prompt)
