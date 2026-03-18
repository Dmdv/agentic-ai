# Local Agentic Coding Infrastructure Specifications

## 1. Executive Summary
This document outlines the specifications for building a local, CLI-based agentic coding assistant (similar to Claude Code or Aider), leveraging local Large Language Models (LLMs) via **Ollama** and **LM Studio**. The goal is a highly capable, autonomous, and private coding assistant that runs entirely on the developer's machine.

## 2. Architecture Overview
The system consists of four primary layers:
1. **User Interface (CLI/TUI):** Terminal-based interaction.
2. **Orchestration Layer:** The state machine / agent framework that manages context, tool execution, and LLM sequencing.
3. **Tool Execution Environment:** Safely executes system commands, reads/writes files, and parses ASTs.
4. **LLM Provider (Local):** The local inference engines (Ollama & LM Studio) providing OpenAI-compatible APIs.

## 3. Technology Stack Options

### 3.1 LLM Providers (The "Brains")
Both tools expose an OpenAI-compatible REST API, allowing seamless swapping of models.
*   **LM Studio:** 
    *   **Pros:** Excellent GUI for discovering and downloading GGUF models. Great for experimenting with prompt formats and system prompts before hardcoding them.
    *   **Endpoint:** `http://127.0.0.1:1234/v1`
*   **Ollama:** 
    *   **Pros:** Headless, highly scriptable. Can load models dynamically via API or CLI. Ideal for the actual agentic workflow.
    *   **Endpoint:** `http://127.0.0.1:11434/v1`

### 3.2 Orchestration Framework
*   **Option A: Custom Python/Node State Machine (Recommended)**
    *   *Why:* Frameworks like LangChain can be overly abstract and bloat the context window. A custom loop allows precise token management (crucial for local, lower-context models).
*   **Option B: CrewAI / LangGraph (Python)**
    *   *Why:* Built-in support for cyclical graphs and multi-agent roles. Excellent if you want a distinct "Senior Dev" and "QA Tester" agent.
*   **Option C: AutoGen (Python)**
    *   *Why:* Specifically designed for agents that write and execute code.

### 3.3 User Interface
*   **Python:** `Typer` or `Click` for CLI commands; `Rich` or `Textual` for beautiful terminal output (syntax highlighting, markdown rendering, spinners).
*   **Node.js:** `Commander.js` + `Inquirer.js` + `chalk`.

## 4. Sequencing & Chaining Local LLMs
Running local models allows for creative multi-model sequences without incurring API costs. Here are the strategies for starting a sequence of LLMs:

### Strategy 1: The "Fast-Slow" Router (Efficiency)
1.  **Intent Classifier (Small/Fast Model):** E.g., *Llama-3-8B*. Quickly determines if the user is asking a general question, searching the codebase, or requesting a code change.
2.  **Specialist (Large/Slow Model):** E.g., *DeepSeek-Coder-33B* or *Codestral*. Invoked only when complex code generation is required.

### Strategy 2: Actor-Critic Loop (Quality Control)
1.  **The Coder:** Generates code and implements changes based on user prompts and file context.
2.  **The Critic (Reviewer):** A separate LLM call (potentially a different model fine-tuned for code review) that evaluates the Coder's output against best practices, security flaws, and the original prompt. If the Critic rejects it, the Coder is re-prompted.

### Strategy 3: Multi-Agent Delegation (Complex Tasks)
1.  **The Planner Agent:** Receives the user request and breaks it down into a JSON array of specific tasks (e.g., `[{"task": "read file A"}, {"task": "write function B"}, {"task": "add test C"}]`).
2.  **The Executor Agent:** Iterates through the Planner's list, executing tool calls (search, read, write, bash).

## 5. Tooling Capabilities (Action Space)
To mimic Claude Code, the local agent must have access to specific local tools. The LLMs must be prompted to output standard tool-call JSON (or XML if the local model struggles with JSON).

*   **FileSystem Tools:**
    *   `read_file(path, start_line, end_line)`
    *   `write_file(path, content)`
    *   `replace_in_file(path, search_string, replace_string)`
*   **Search Tools:**
    *   `grep_search(pattern, dir)` - Powered by `ripgrep` (rg) for speed.
    *   `find_files(pattern)`
*   **Execution Tools:**
    *   `run_bash(command)` - Crucial for running tests, linters, and type-checkers locally to verify changes before completing a task.

## 6. Infrastructure Setup for Current Machine (Darwin/macOS)

### 6.1 Prerequisites
1.  **Install Ollama:** `brew install ollama`
2.  **Install LM Studio:** Download from lmstudio.ai
3.  **Install ripgrep:** `brew install ripgrep` (for fast codebase searching)

### 6.2 Recommended Local Models for Coding
*   **Fast/Routing/Tool-Calling:** `llama3.1:8b-instruct` or `qwen2.5-coder:7b`
*   **Heavy Coding/Reasoning:** `deepseek-coder-v2` or `codestral` (Requires Apple Silicon with >= 32GB Unified Memory for reasonable speeds).

## 7. Implementation Roadmap

### Phase 1: Core Loop & Connectors
*   Setup a basic Python script.
*   Create API connector functions pointing to `localhost:11434` (Ollama) and `localhost:1234` (LM Studio).
*   Implement basic chat loop with memory.

### Phase 2: Tool Integration
*   Implement `read_file`, `write_file`, and `run_shell` Python functions.
*   Prompt engineer the local model to understand how to output specific XML/JSON tags to trigger these tools.
*   Write the parser that intercepts tool calls, executes them locally, and feeds the `stdout`/`stderr` back to the LLM.

### Phase 3: Agentic Sequencing
*   Implement the **Actor-Critic** loop: After the main agent writes code, automatically trigger a test run via `run_shell`. If tests fail, feed the error back to the agent for a fix (up to max 3 iterations).

### Phase 4: CLI Polish
*   Add `Rich` for markdown rendering in the terminal.
*   Implement streaming responses so the user sees the model "thinking" in real-time.
