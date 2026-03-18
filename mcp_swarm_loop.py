import argparse
import asyncio
import gc
import json
import sys
import os
from typing import List, Dict, Any

from mlx_lm import load, generate
from mcp_multi_server_loop import MCPAgenticLoop

class SwarmOrchestrator:
    def __init__(self, architect_model: str, engineer_model: str):
        self.architect_model_name = architect_model
        self.engineer_model_name = engineer_model
        
        # Cache the models in memory so we don't reload from disk
        self._architect = None
        self._architect_tokenizer = None
        
        self._engineer_agent = None
        
    def _get_architect(self):
        if self._architect is None:
            print(f"\n[SWARM] Loading Architect ({self.architect_model_name}) into RAM (Cached)...")
            self._architect, self._architect_tokenizer = load(self.architect_model_name)
        return self._architect, self._architect_tokenizer

    def _get_engineer_agent(self):
        if self._engineer_agent is None:
            print(f"\n[SWARM] Loading Engineer ({self.engineer_model_name}) into RAM (Cached)...")
            self._engineer_agent = MCPAgenticLoop(model_name=self.engineer_model_name, keep_in_memory=True)
            # Pre-load the engineer's model so it stays in RAM
            self._engineer_agent._load_model()
        return self._engineer_agent
        
    def _run_architect(self, prompt: str) -> List[str]:
        print(f"\n[SWARM PHASE 1] Architect is planning...")
        model, tokenizer = self._get_architect()
        
        # Load repo map to give the architect full context
        repo_map = ""
        if os.path.exists(".repo_map"):
            with open(".repo_map", "r") as f:
                repo_map = f.read()
                
        system_prompt = """You are the Lead System Architect.
Your job is to read the user's request and the current repository structure.
You do NOT write code. You have two responsibilities:
1. Write a detailed Technical Specification Document in Markdown format wrapped in ```markdown ... ``` tags.
2. Output a JSON array of exact execution steps for the Engineer wrapped in ```json ... ``` tags.

Example Output:
```markdown
# Technical Specification
## Goal
Fix the failing auth bug.
## Architecture
The issue resides in `src/auth.py`. We will update the token validation logic.
```
```json
["Use bash to run pytest", "Read src/auth.py", "Rewrite the function to fix the bug", "Run pytest again"]
```
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Repo Map:\n{repo_map}\n\nTask: {prompt}\n\nOutput the markdown spec block, followed by the JSON array block."}
        ]
        
        formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        print("Architect is thinking...")
        
        response = generate(model, tokenizer, prompt=formatted_prompt, max_tokens=4000, verbose=False)
        
        print("\n[SWARM PHASE 1 COMPLETE] Unloading Architect to free Unified Memory...")
        del model
        del tokenizer
        self._architect = None
        self._architect_tokenizer = None
        gc.collect()
        
        # 1. Extract and write the Markdown Specification
        md_match = re.search(r'```markdown\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
        if md_match:
            spec_content = md_match.group(1).strip()
            with open("AGENT_PLAN.md", "w") as f:
                f.write(spec_content)
            print("-> Successfully wrote Technical Specification to 'AGENT_PLAN.md'")
        else:
            print("-> Architect did not provide a markdown specification block.")
            # Fallback: just dump the raw response if tags failed
            with open("AGENT_PLAN.md", "w") as f:
                f.write(response)
        
        # 2. Extract and return the JSON array of steps
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Fallback if the agent forgot the code block
                json_str = response[response.find('['):response.rfind(']')+1]
                
            steps = json.loads(json_str)
            return steps
        except Exception as e:
            print(f"Failed to parse Architect JSON output: {e}\nRaw output: {response}")
            return [prompt] # Fallback to giving the engineer the raw prompt

    async def run(self, user_prompt: str):
        print(f"=== INITIALIZING AGENT SWARM ===")
        
        # Phase 1: Planning
        steps = self._run_architect(user_prompt)
        print(f"\nArchitect Plan:")
        for i, step in enumerate(steps):
            print(f"  {i+1}. {step}")
            
        # Phase 2: Execution
        print(f"\n[SWARM PHASE 2] Handing off to Engineer...")
        
        engineer = self._get_engineer_agent()
        
        # We loop through each step in the Architect's plan, starting a new agent loop for each
        for i, step in enumerate(steps):
            print(f"\n=== ENGINEER EXECUTING STEP {i+1}/{len(steps)}: {step} ===")
            await engineer.run(user_prompt=step)
            
        print("\n=== SWARM EXECUTION COMPLETE ===")
        
        # Optional: You could add a manual cleanup here, but for a CLI tool, 
        # the OS will reclaim the memory when the python script exits.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Multi-Agent Swarm.")
    parser.add_argument("--prompt", type=str, required=True, help="The overall task for the Swarm.")
    parser.add_argument("--architect", type=str, default="mlx-community/Qwen3-235B-8bit", help="The planning model.")
    parser.add_argument("--engineer", type=str, default="mlx-community/Qwen3-Coder-Next-80B-8bit", help="The executing model.")
    
    args = parser.parse_args()
    
    swarm = SwarmOrchestrator(architect_model=args.architect, engineer_model=args.engineer)
    
    try:
        asyncio.run(swarm.run(user_prompt=args.prompt))
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
