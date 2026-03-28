# Agentic AI Infrastructure: Master Specification (V6)
**Date:** March 2026
**Target Architecture:** Apple Silicon (M3 Ultra, 512GB Unified Memory)
**Framework:** MLX-LM + Model Context Protocol (MCP)

## 1. Executive Summary
This document outlines the final architectural state of the autonomous, offline Spec-Driven Development (SDD) Swarm. The system is designed to orchestrate state-of-the-art trillion-parameter Mixture-of-Experts (MoE) models entirely locally, rivaling proprietary systems like Claude Code and Devin.

## 2. The Cognitive Engine (MLX)
The infrastructure abandons `llama.cpp` in favor of Apple's native `mlx-lm`. 
*   **Zero-Overhead Swapping:** By utilizing `keep_in_memory=True`, models are mapped directly into macOS Unified Memory as arrays. Switching between the Architect and Engineer takes milliseconds via Python garbage collection (`del model; gc.collect()`).
*   **Metal Concurrency Lock:** The orchestrator utilizes a class-level `asyncio.Lock()` (`_generation_lock` in `MCPAgenticLoop`) to serialize GPU token generation. This allows the Swarm to process logical I/O and MCP tasks in parallel without crashing the Apple Metal drivers during simultaneous inference.

## 3. The Swarm Topology
The system utilizes a dual-model paradigm to separate reasoning from execution.

### 3.1 The Architect (System 2)
*   **Default Model:** `mlx-community/Kimi-K2.5-1T-4bit`
*   **Role:** Reads the `.repo_map` and the user's prompt. It generates the strict `SPEC.md` and outputs a JSON object containing the target `working_dir` and a massive array of sequential/parallel execution steps.

### 3.2 The Engineer (System 1)
*   **Default Model:** `mlx-community/Qwen3-235B-8bit`
*   **Role:** An execution engine that assumes over 40 distinct personas (Markdown files in the `agents/` directory) via system prompt hot-swapping. It executes the steps dictated by the Architect.

## 4. The Tooling Layer (Model Context Protocol)
The Swarm interacts with the host machine through 7 dynamically booted MCP servers via standard I/O:
1.  **Filesystem:** Safely reads and edits files within the designated sandbox.
2.  **Git:** Handles staging and repository state.
3.  **SQLite:** Executes SQL commands (`mcp-server-sqlite`).
4.  **Memory:** Cross-session context sharing.
5.  **Bash (`mcp_server_bash.py`):** A custom, highly restricted Python server that whitelists safe commands (`pytest`, `cargo build`, `make`) to close the CI/CD loop without risking OS destruction.
6.  **Diff (`mcp_server_diff.py`):** A custom server enabling Aider-style `<<<< SEARCH` and `==== REPLACE >>>>` blocks for surgical edits on massive files.
7.  **Web Search (`mcp_server_ddg.py`):** A custom, free DuckDuckGo web scraper that allows agents to autonomously research internet documentation and obscure error codes without API keys.

## 5. Security & Isolation
*   **Directory Sandboxing:** The Orchestrator accepts a `--dir` argument (or automatically deduces it from the Architect's JSON output). It explicitly injects a `CRITICAL SCOPE RESTRICTION` into every agent's prompt, confining their file reads/writes to that specific subdirectory.
*   **Virtual Environment Enforcement:** The Python orchestrator dynamically calculates `sys.executable` and passes it to all Python-based MCP servers. This guarantees the servers run inside the isolated `.venv`, protecting the global macOS Python environment.
*   **Language-Specific Isolation:** The specialized language agents (`python-engineer.md`, `c-engineer.md`, etc.) are hardcoded to never pollute the root directory. They force the use of `pyproject.toml`, CMake `build/` directories, and strict Makefiles.

## 6. The "Skills" Framework (SOPs)
The `skills/` directory contains enterprise-grade Standard Operating Procedures (e.g., `python-guidelines`, `assembler-guidelines`, `pentester-guidelines`).
*   **Proactive Initialization:** If the Architect detects a language that matches a Skill, it creates a "Stage 0" task directing the Engineer to physically generate the boilerplate defined in the Skill (e.g., `mypy.ini`, `tsconfig.json`) *before* writing any application code.

## 7. Memory & Context Management
1.  **Reversible Context Compaction:** If an agent's context window exceeds 100,000 tokens (e.g., due to a massive wildcard search), the orchestrator intercepts the array. It forcefully truncates the history to 40,000 characters and asks the LLM to summarize it into a dense JSON state object, preventing `Abort Trap 6` (OOM) crashes.
2.  **The Hive Mind (ChromaDB):** The `critical-reviewer` agent extracts a 1-sentence "Lesson Learned" after fixing any bug. This is embedded into a local Vector DB (`.hive_memory/`). Future Swarm initializations query this database to prevent repeating past mistakes.