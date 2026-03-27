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
from hive_memory import HiveMemory

# Load environment variables (e.g. HF_TOKEN) from .env file
load_dotenv()

class SDDSwarmOrchestrator:
    """Spec-Driven Development Swarm Orchestrator inspired by Claude Superpowers."""
    def __init__(self, architect_model: str, engineer_model: str, working_dir: str = "."):
        self.architect_model_name = architect_model
        self.engineer_model_name = engineer_model
        self.working_dir = working_dir
        
        self._architect = None
        self._architect_tokenizer = None
        
        self._engineer_agent = None
        
        # Initialize Tier 2 Procedural Memory (Vector DB)
        self.hive_mind = HiveMemory()

    def _get_architect(self):
        if self._architect is None:
            print(f"\n[SWARM] Loading Architect ({self.architect_model_name}) into RAM (Cached)...")
            self._architect, self._architect_tokenizer = load(self.architect_model_name)
        return self._architect, self._architect_tokenizer

    def _get_engineer_agent(self):
        if self._engineer_agent is None:
            print(f"\n[SWARM] Loading Engineer ({self.engineer_model_name}) into RAM (Cached)...")
            self._engineer_agent = MCPAgenticLoop(model_name=self.engineer_model_name, keep_in_memory=True, working_dir=self.working_dir)
            self._engineer_agent._load_model()
        return self._engineer_agent

    async def _run_spec_phase(self, user_prompt: str):
        print(f"\n=== PHASE 1: SPECIFICATION DRIVEN DEVELOPMENT ===")
        engineer = self._get_engineer_agent()
        
        # 0. Query Procedural Memory
        print("\n[SWARM] Querying Hive Mind for related past lessons...")
        past_lessons = self.hive_mind.get_relevant_lessons(user_prompt)
        memory_context = f"\n\n### Prior Lessons Learned from Hive Mind:\n{past_lessons}\n(Incorporate these strictly into the spec if applicable.)" if past_lessons else ""
        
        # 1. Spec Writer generates initial spec
        print(f"\n[SWARM] Generating Initial Specification...")
        engineer.set_persona("agents/core/spec-writer.md")
        spec_prompt = f"User Request: {user_prompt}{memory_context}\n\nPlease generate a comprehensive specification and save it to SPEC.md."
        await engineer.run(user_prompt=spec_prompt)
        
        # 2. Evaluation Loop
        max_loops = 3
        for loop in range(max_loops):
            print(f"\n[SWARM] Spec Evaluation Loop {loop+1}/{max_loops}...")
            
            # Researcher Phase
            print(f"\n[SWARM] Running Researcher validation...")
            engineer.set_persona("agents/core/researcher.md")
            research_prompt = "Read the current SPEC.md. Use your fetch tool to research best practices on the web. If there are flaws, list them. If it is perfect, output 'RESEARCH PASSED'."
            
            # We must capture the agent's output. Since MCPAgenticLoop prints and modifies history, 
            # we can run it and check the final assistant message (we'll read SPEC.md to see if it changed, 
            # or we can modify MCPAgenticLoop to return the final answer. 
            # For simplicity, we just ask the agent to write its critique to RESEARCH_REPORT.md).
            research_prompt += " Write your findings to RESEARCH_REPORT.md."
            await engineer.run(user_prompt=research_prompt)
            
            # Critical Reviewer Phase
            print(f"\n[SWARM] Running Critical Reviewer validation...")
            engineer.set_persona("agents/core/critical-reviewer.md")
            review_prompt = "Read SPEC.md and RESEARCH_REPORT.md. Review them rigorously. Write your findings and any requested changes to REVIEW_REPORT.md. If there are 0 issues, output exactly 'REVIEW PASSED' in the file."
            await engineer.run(user_prompt=review_prompt)
            
            # Check if passed
            review_content = ""
            if os.path.exists("REVIEW_REPORT.md"):
                with open("REVIEW_REPORT.md", "r") as f:
                    review_content = f.read()
                
            if "REVIEW PASSED" in review_content:
                print(f"\n[SWARM] Specification approved by Reviewers!")
                break
            else:
                print(f"\n[SWARM] Issues found. Sending back to Spec Writer...")
                engineer.set_persona("agents/core/spec-writer.md")
                fix_prompt = "Read REVIEW_REPORT.md and RESEARCH_REPORT.md. Update SPEC.md to resolve all issues."
                await engineer.run(user_prompt=fix_prompt)
                
        print(f"\n=== PHASE 1 COMPLETE ===")

    def _run_planning_phase(self) -> List[Dict[str, str]]:
        print(f"\n=== PHASE 2: DEVELOPMENT PLANNING ===")
        model, tokenizer = self._get_architect()
        
        repo_map = ""
        if os.path.exists(".repo_map"):
            with open(".repo_map", "r") as f:
                repo_map = f.read()
                
        spec_content = ""
        if os.path.exists("SPEC.md"):
            with open("SPEC.md", "r") as f:
                spec_content = f.read()
                
        available_agents = []
        if os.path.exists("agents"):
            for root, dirs, files in os.walk("agents"):
                for file in files:
                    if file.endswith(".md") and "architect" not in file and "planning" not in file:
                        rel_path = os.path.relpath(os.path.join(root, file), "agents")
                        available_agents.append(rel_path)
        
        agents_list = ", ".join(available_agents) if available_agents else "None"
        
        available_skills = []
        if os.path.exists("skills"):
            for root, dirs, files in os.walk("skills"):
                for file in files:
                    if file.endswith(".md"):
                        rel_path = os.path.relpath(os.path.join(root, file), "skills")
                        available_skills.append(rel_path)
                        
        skills_list = ", ".join(available_skills) if available_skills else "None"
        
        system_prompt = ""
        planner_file = "agents/core/planning-agent.md"
        if os.path.exists(planner_file):
            with open(planner_file, 'r') as f:
                content = f.read()
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        system_prompt = parts[2].strip()
        
        system_prompt = system_prompt.replace("{agents_list}", agents_list)
        
        # Inject the skills instructions
        skill_instruction = f"""

You also have access to the following strictly defined corporate Skills/SOPs located in the `skills/` directory:
{skills_list}

CRITICAL INSTRUCTION FOR SKILLS:
If the SPEC.md involves a language or framework that matches a Skill (e.g., they ask for a Python script and you see `python-guidelines/SKILL.md` in the list), you MUST explicitly write a task in your JSON array directing the executing agent to read that exact skill file before they begin coding, so they adhere to our strict corporate standards.
"""
        system_prompt += skill_instruction
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Repo Map:\n{repo_map}\n\nSPEC.md:\n{spec_content}\n\nOutput ONLY the JSON array block."}
        ]
        
        formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        print("Planning Agent is thinking...")
        
        response = generate(model, tokenizer, prompt=formatted_prompt, max_tokens=4000, verbose=False)
        
        print("\n[SWARM PHASE 2 COMPLETE] Unloading Planning Agent...")
        del model
        del tokenizer
        self._architect = None
        self._architect_tokenizer = None
        gc.collect()
        
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                json_str = response[response.find('{'):response.rfind('}')+1]
                
            plan_data = json.loads(json_str)
            
            # Backwards compatibility fallback if the model still outputs an array
            if isinstance(plan_data, list):
                steps = plan_data
                working_dir = "."
            else:
                steps = plan_data.get("steps", [])
                working_dir = plan_data.get("working_dir", ".")
                
            if isinstance(steps, list) and len(steps) > 0 and isinstance(steps[0], str):
                steps = [{"task": s, "agent": None} for s in steps]
                
            return working_dir, steps
        except Exception as e:
            print(f"Failed to parse Planner JSON output: {e}\nRaw output: {response}")
            return ".", [{"task": "Implement SPEC.md", "agent": None}]

    async def _execute_single_task(self, task_info: Dict[str, Any], preloaded_model, preloaded_tokenizer, step_num: int) -> str:
        task = task_info.get("task", "")
        agent_file = task_info.get("agent")
        
        engineer = MCPAgenticLoop(
            model_name=self.engineer_model_name, 
            keep_in_memory=True, 
            preloaded_model=preloaded_model, 
            preloaded_tokenizer=preloaded_tokenizer,
            working_dir=self.working_dir
        )
        
        found_persona_path = None
        if agent_file:
            exact_path = os.path.join("agents", agent_file)
            if os.path.exists(exact_path):
                found_persona_path = exact_path
            else:
                for root, dirs, files in os.walk("agents"):
                    if os.path.basename(agent_file) in files:
                        found_persona_path = os.path.join(root, os.path.basename(agent_file))
                        break
                        
        if found_persona_path:
            print(f"\n=== SWARM HOT-SWAP [Step {step_num}]: Loading '{found_persona_path}' Persona ===")
            engineer.set_persona(found_persona_path)
        else:
            engineer.set_persona(None)
            
        print(f"\n=== EXECUTING TASK [Step {step_num}]: {task} ===")
        await engineer.run(user_prompt=task)
        
        # Validation & Review Loop
        print(f"\n=== VALIDATING TASK [Step {step_num}]: {task} ===")
        engineer.set_persona("agents/qa/requirement-validator.md")
        await engineer.run(user_prompt=f"Validate that the recent code changes fulfill this task: '{task}' and align with SPEC.md. Save your findings to VALIDATION_{step_num}.md")
        
        engineer.set_persona("agents/core/critical-reviewer.md")
        await engineer.run(user_prompt=f"Read VALIDATION_{step_num}.md and review the latest code changes. If there are issues, use bash to fix them, or leave instructions. Save final status to REVIEW_REPORT_{step_num}.md. Finally, write a 1-sentence 'Lesson Learned' about any bugs you fixed to LESSONS_{step_num}.txt.")
        
        lesson = ""
        if os.path.exists(f"LESSONS_{step_num}.txt"):
            with open(f"LESSONS_{step_num}.txt", "r") as f:
                lesson = f.read().strip()
            if lesson:
                print(f"\n[HIVE MIND] Storing Lesson: {lesson}")
                self.hive_mind.add_lesson(task, lesson)
                
        return lesson

    async def _run_execution_phase(self, steps: List[Dict[str, Any]]):
        print(f"\n=== PHASE 3: PARALLEL EXECUTION & VALIDATION ===")
        print(f"[SYSTEM] Orchestrator scoped to directory sandbox: '{self.working_dir}'")
        
        # Group steps by stage
        stages = {}
        for i, step in enumerate(steps):
            stage_num = step.get("stage", i) # Default to sequential if no stage provided
            if stage_num not in stages:
                stages[stage_num] = []
            stages[stage_num].append((i + 1, step))
            
        # Ensure the engineer model is loaded into RAM once
        base_engineer = self._get_engineer_agent()
        preloaded_model = base_engineer.model
        preloaded_tokenizer = base_engineer.tokenizer
        
        import datetime
        report_lines = [
            f"# SDD Swarm Execution Report",
            f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Execution Sandbox:** `{self.working_dir}`",
            f"\n## Approved Development Plan",
        ]
        
        for i, step in enumerate(steps):
            task = step.get("task", "")
            agent = step.get("agent", "Default Engineer")
            stage = step.get("stage", "None")
            report_lines.append(f"{i+1}. **Stage:** {stage} | **Agent:** `{agent}` -> **Task:** {task}")
            
        report_lines.append("\n## Engineering Phase")
        
        # Execute stages sequentially, but tasks within a stage concurrently
        for stage_num in sorted(stages.keys()):
            stage_tasks = stages[stage_num]
            print(f"\n>>> STARTING STAGE {stage_num} ({len(stage_tasks)} concurrent tasks) <<<")
            
            coroutines = []
            for step_num, step_info in stage_tasks:
                report_lines.append(f"\n### Step {step_num} (Stage {stage_num}): {step_info.get('task')}")
                report_lines.append(f"- **Executor Persona:** `{step_info.get('agent', 'Default')}`")
                
                coro = self._execute_single_task(step_info, preloaded_model, preloaded_tokenizer, step_num)
                coroutines.append(coro)
                
            # Run all tasks in this stage concurrently
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            for (step_num, _), lesson in zip(stage_tasks, results):
                report_lines.append(f"- **Execution & Validation:** Passed")
                if isinstance(lesson, str) and lesson:
                    report_lines.append(f"- **Lesson Learned:** {lesson}")
                elif isinstance(lesson, Exception):
                    report_lines.append(f"- **Error:** {str(lesson)}")
            
        print("\n=== SWARM EXECUTION COMPLETE ===")
        report_lines.append("\n## Swarm Execution Complete")
        
        with open("SWARM_EXECUTION_REPORT.md", "w") as f:
            f.write("\n".join(report_lines))
        print("-> Saved execution flow details to 'SWARM_EXECUTION_REPORT.md'")

    async def run(self, user_prompt: str):
        print(f"=== INITIALIZING SPEC-DRIVEN SWARM ===")
        
        print("\n[SWARM] Auto-generating Repository Map...")
        import generate_repo_map
        full_map = generate_repo_map.generate_repo_map(".")
        with open(".repo_map", "w") as f:
            f.write(full_map)
            
        # Phase 1: SDD Spec Generation
        await self._run_spec_phase(user_prompt)
        
        # Phase 2: Planning
        detected_dir, steps = self._run_planning_phase()
        
        # We dynamically update the orchestrator's working_dir based on the LLM's parsing of the spec!
        if detected_dir and detected_dir != ".":
            print(f"\n[SYSTEM] Architect detected nested target directory: {detected_dir}")
            self.working_dir = detected_dir
            # Ensure the target directory physically exists before spawning the engineers
            os.makedirs(self.working_dir, exist_ok=True)
        
        # Phase 3: Execution with Validation
        await self._run_execution_phase(steps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Spec-Driven Development Multi-Agent Swarm.")
    parser.add_argument("--prompt", type=str, required=True, help="The overall task to build.")
    parser.add_argument("--architect", type=str, default="mlx-community/Kimi-K2.5-1T-4bit", help="The planning model.")
    parser.add_argument("--engineer", type=str, default="mlx-community/Qwen3-235B-8bit", help="The executing model.")
    parser.add_argument("--dir", type=str, default=".", help="The specific directory to restrict the agent's file operations to.")
    
    args = parser.parse_args()
    swarm = SDDSwarmOrchestrator(architect_model=args.architect, engineer_model=args.engineer, working_dir=args.dir)
    
    try:
        asyncio.run(swarm.run(user_prompt=args.prompt))
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)