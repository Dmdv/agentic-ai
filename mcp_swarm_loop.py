import argparse
import asyncio
import gc
import json
import sys
import os
import re
from typing import List, Dict, Any

from dotenv import load_dotenv
from mlx_lm import load, generate
from mcp_multi_server_loop import MCPAgenticLoop

# Load environment variables (e.g. HF_TOKEN) from .env file
load_dotenv()

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
        
    def _run_architect(self, prompt: str) -> List[Dict[str, str]]:
        print(f"\n[SWARM PHASE 1] Architect is planning...")
        model, tokenizer = self._get_architect()
        
        # Load repo map to give the architect full context
        repo_map = ""
        if os.path.exists(".repo_map"):
            with open(".repo_map", "r") as f:
                repo_map = f.read()
                
        # Load available personas dynamically from all subdirectories
        available_agents = []
        if os.path.exists("agents"):
            for root, dirs, files in os.walk("agents"):
                for file in files:
                    if file.endswith(".md") and file != "architect.md":
                        # We store the relative path (e.g. qa/test-fixer.md) so the Engineer knows exactly where to load it from
                        rel_path = os.path.relpath(os.path.join(root, file), "agents")
                        available_agents.append(rel_path)
        
        agents_list = ", ".join(available_agents) if available_agents else "None (Use default engineer)"
                
        # Load Architect Persona dynamically
        system_prompt = ""
        architect_file = "agents/core/architect.md"
        if os.path.exists(architect_file):
            with open(architect_file, 'r') as f:
                content = f.read()
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        system_prompt = parts[2].strip()
        
        # Fallback if file missing
        if not system_prompt:
            system_prompt = f"""You are the Lead System Architect.
Your job is to read the user's request and the current repository structure.
You do NOT write code. You have two responsibilities:
1. Write a detailed Technical Specification Document in Markdown format wrapped in ```markdown ... ``` tags.
2. Output a JSON array of exact execution steps for the Engineering Swarm. Crucially, for each step, you must select the best specialized agent from the available agents list to execute it. Wrap this array in ```json ... ``` tags.

Example Output:
```markdown
# Technical Specification
## Goal
Fix the failing auth bug.
```
```json
[
  {{"task": "Read src/auth.py and rewrite the function to fix the bug", "agent": "devops-automation-engineer.md"}}
]
```
"""
        
        # Inject the dynamic agents list into the prompt
        system_prompt = system_prompt.replace("{agents_list}", agents_list)
        
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
            with open("AGENT_PLAN.md", "w") as f:
                f.write(response)
        
        # 2. Extract and return the JSON array of steps
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                json_str = response[response.find('['):response.rfind(']')+1]
                
            steps = json.loads(json_str)
            if isinstance(steps, list) and len(steps) > 0 and isinstance(steps[0], str):
                steps = [{"task": s, "agent": None} for s in steps]
                
            # MANDATORY CRITICAL REVIEW PHASE
            # We automatically inject the Critical Reviewer at the end of every plan
            steps.append({
                "task": "Review all changes made during this run against the AGENT_PLAN.md. Run any tests or linters. If flawed, provide fix instructions. If perfect, output 'REVIEW PASSED'.",
                "agent": "core/critical-reviewer.md"
            })
            
            return steps
        except Exception as e:
            print(f"Failed to parse Architect JSON output: {e}\nRaw output: {response}")
            return [
                {"task": prompt, "agent": None},
                {"task": "Review the previous execution against requirements.", "agent": "core/critical-reviewer.md"}
            ]

    async def run(self, user_prompt: str):
        print(f"=== INITIALIZING AGENT SWARM ===")
        
        # Automatically generate the repo map first!
        print("\n[SWARM] Auto-generating Repository Map...")
        import generate_repo_map
        full_map = generate_repo_map.generate_repo_map(".")
        with open(".repo_map", "w") as f:
            f.write(full_map)
        print("[SWARM] Repository Map generated and saved.")
        
        # Phase 1: Planning
        steps = self._run_architect(user_prompt)
        print(f"\nArchitect Plan:")
        
        # Initialize the Execution Report
        import datetime
        report_lines = [
            f"# Swarm Execution Report",
            f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Task Prompt:** {user_prompt}",
            f"\n## Architect's Execution Plan",
        ]
        
        for i, step in enumerate(steps):
            task = step.get("task", "")
            agent = step.get("agent", "Default Engineer")
            print(f"  {i+1}. [{agent}] -> {task}")
            report_lines.append(f"{i+1}. **Agent:** `{agent}` -> **Task:** {task}")
            
        # Phase 2: Execution
        print(f"\n[SWARM PHASE 2] Handing off to Engineering Swarm...")
        report_lines.append("\n## Engineering Phase")
        
        engineer = self._get_engineer_agent()
        
        # We loop through each step in the Architect's plan, starting a new agent loop for each
        for i, step in enumerate(steps):
            task = step.get("task", "")
            agent_file = step.get("agent")
            
            report_lines.append(f"\n### Step {i+1}: {task}")
            
            # Hot-swap the persona if specified
            found_persona_path = None
            if agent_file:
                # First try exact path
                exact_path = os.path.join("agents", agent_file)
                if os.path.exists(exact_path):
                    found_persona_path = exact_path
                else:
                    # Fallback: search through the agents directory for the filename
                    for root, dirs, files in os.walk("agents"):
                        if os.path.basename(agent_file) in files:
                            found_persona_path = os.path.join(root, os.path.basename(agent_file))
                            break
                            
            if found_persona_path:
                print(f"\n=== SWARM HOT-SWAP: Loading '{found_persona_path}' Persona ===")
                report_lines.append(f"- **Persona Loaded:** `{found_persona_path}`")
                engineer.set_persona(found_persona_path)
            else:
                print(f"\n=== SWARM HOT-SWAP: Reverting to Default Engineer Persona ===")
                report_lines.append("- **Persona Loaded:** `Default Engineer`")
                engineer.set_persona(None)
                
            print(f"\n=== EXECUTING STEP {i+1}/{len(steps)}: {task} ===")
            
            # Record the start of the task
            report_lines.append(f"- **Status:** Executed")
            await engineer.run(user_prompt=task)
            
        print("\n=== SWARM EXECUTION COMPLETE ===")
        report_lines.append("\n## Swarm Execution Complete")
        
        # Write the final report
        report_content = "\n".join(report_lines)
        with open("SWARM_EXECUTION_REPORT.md", "w") as f:
            f.write(report_content)
        print("-> Saved execution flow details to 'SWARM_EXECUTION_REPORT.md'")
        
        # Optional: You could add a manual cleanup here, but for a CLI tool, 
        # the OS will reclaim the memory when the python script exits.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Multi-Agent Swarm.")
    parser.add_argument("--prompt", type=str, required=True, help="The overall task for the Swarm.")
    parser.add_argument("--architect", type=str, default="mlx-community/Kimi-K2.5-1T-4bit", help="The planning model.")
    parser.add_argument("--engineer", type=str, default="mlx-community/Qwen3-235B-8bit", help="The executing model.")
    
    args = parser.parse_args()
    
    swarm = SwarmOrchestrator(architect_model=args.architect, engineer_model=args.engineer)
    
    try:
        asyncio.run(swarm.run(user_prompt=args.prompt))
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
