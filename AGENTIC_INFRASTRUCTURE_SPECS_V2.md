# Local Agentic Coding Infrastructure Specifications (V2: State-of-the-Art)

## 1. Executive Summary
This document outlines the cutting-edge specifications for building a local, CLI-based agentic coding assistant. This V2 specification moves beyond basic REST API integrations and naive string matching, incorporating the latest advancements in AI coding: **Model Context Protocol (MCP)**, **Reasoning Models (System 2)**, **Tree-Sitter based Repository Maps**, and **Structured Diff Editing**.

## 2. Critical Critique of V1 vs. Recent Advancements

*   **Critique 1: Naive Tooling (The MCP Revolution)**
    *   *V1 Issue:* Hardcoded Python functions for `read_file` or `run_bash`.
    *   *V2 Advancement:* **Model Context Protocol (MCP)**. Instead of building bespoke tools, the infrastructure should act as an MCP Client. It connects to standardized local MCP servers (e.g., `mcp-server-sqlite`, `mcp-server-filesystem`, `mcp-server-git`). This allows the agent to plug-and-play hundreds of community-built tools without writing new integration code.
*   **Critique 2: Model Architecture (The Rise of Reasoning Models)**
    *   *V1 Issue:* Relying on a single "Smart Model" or a basic "Router".
    *   *V2 Advancement:* **Dual-Model Cognitive Architecture**. We now split tasks into "Thinking" and "Doing". We use a local reasoning model (like `DeepSeek-R1-Distill`) to generate a complex plan via Chain-of-Thought (System 2), and pass that plan to a highly optimized, fast tool-calling model (like `Qwen2.5-Coder`) for execution (System 1).
*   **Critique 3: Context Retrieval (Grep is Dead)**
    *   *V1 Issue:* Relying heavily on `grep` and raw file reads, which destroys context windows and misses logical connections.
    *   *V2 Advancement:* **Tree-Sitter Repository Maps**. Inspired by tools like Aider, the system must parse the AST (Abstract Syntax Tree) of the codebase using `tree-sitter`. It generates a compact "skeleton" of the repository (classes, methods, signatures without the implementation bodies) so the LLM understands the whole project in < 10k tokens.
*   **Critique 4: File Editing (The Replace String Flaw)**
    *   *V1 Issue:* `replace_in_file` is notoriously brittle if the LLM hallucinates whitespace or indentation.
    *   *V2 Advancement:* **Search/Replace Blocks (SEARCH/REPLACE format)**. The agent outputs specific `<<<< SEARCH` and `==== REPLACE >>>>` blocks. The client uses fuzzy matching (like `difflib` in Python) to apply edits safely even if the LLM messes up indentation.

## 3. Architecture Overview (The SOTA Stack)

### 3.1 Orchestration Framework
*   **Recommendation:** **PydanticAI** or **HuggingFace SmolAgents**.
*   *Why:* LangChain and CrewAI are too heavy and abstract. PydanticAI forces type-safe tool calls and schema enforcement, which is critical when dealing with local, quantized models that might hallucinate JSON structures. SmolAgents is incredibly lightweight and optimized for code-first agentic loops.

### 3.2 Cognitive Sequencing (Dual-Model Setup)
1.  **The Architect (Reasoning Model):** 
    *   *Model:* `deepseek-r1:8b` or `14b` (via Ollama).
    *   *Role:* Receives the user prompt and the Repo Map. Outputs intense `<think>` blocks to plan the architecture, identify edge cases, and determine exactly which files need to change. *It does not write the code or call tools.*
2.  **The Engineer (Tool/Action Model):**
    *   *Model:* `qwen2.5-coder:7b-instruct` or `32b` (via Ollama/LM Studio).
    *   *Role:* Takes the Architect's exact plan. Has access to all MCP tools. Executes search, reads specific lines, and outputs `SEARCH/REPLACE` blocks.

### 3.3 Context Engine
*   **Repository Map Generator:** A local module utilizing `tree-sitter` (e.g., via the Python `tree-sitter` bindings or `grep-ast`). It updates dynamically whenever the Engineer model writes a file.
*   **Language Server Protocol (LSP) Hooks:** Optional but recommended. Running a headless LSP (like `pyright` or `tsserver`) allows the agent to call tools like `get_definition()` or `find_references()` rather than guessing via text search.

### 3.4 Tooling via MCP (Model Context Protocol)
The agent operates as an MCP client. Local MCP servers run as background processes:
1.  `filesystem-mcp`: Handles safe read/write/edit operations.
2.  `shell-mcp`: Executes tests and linting.
3.  `github-mcp`: For creating branches, reading diffs, and staging commits.

## 4. The Agentic Loop (Test-Driven Self-Correction)

1.  **User Input:** User requests a feature.
2.  **Context Injection:** System pre-pends the latest `Tree-Sitter Repo Map` to the prompt.
3.  **Reasoning Phase:** *Architect Model* creates a step-by-step implementation plan.
4.  **Execution Loop:** *Engineer Model* begins working.
    *   Calls `mcp_read_file` to inspect exact lines.
    *   Outputs Search/Replace blocks.
    *   Client applies diffs locally.
5.  **Verification (Crucial):**
    *   Before returning to the user, the agent automatically triggers the project's test suite via `mcp_run_shell` (e.g., `npm run test` or `pytest`).
    *   If tests fail, the stderr is fed back to the *Engineer Model* to generate a new diff.
    *   Loop caps at 3 retries to prevent infinite token burn.

## 5. Hardware & Setup Requirements (Local Machine)

*   **Inference Backend:** **Ollama** remains the best for headless CLI operation due to its fast loading of models into VRAM and concurrency support. LM Studio is excellent for testing models but less ideal for automated CLI scripts.
*   **Hardware (macOS/Darwin):** 
    *   M1/M2/M3/M4 Series with >= 32GB Unified Memory is highly recommended to run a 32B model (Engineer) and an 8B/14B model (Architect) simultaneously, or swapping them rapidly.
    *   For 16GB Macs: Stick to 7B/8B models for both (e.g., `qwen2.5-coder:7b` and `deepseek-r1:8b`).

## 6. Implementation Roadmap (Modernized)

*   **Phase 1: Foundation (PydanticAI & MCP)**
    *   Set up a Python CLI using `Typer`.
    *   Implement an MCP Client. Connect it to local open-source MCP filesystem and bash servers.
*   **Phase 2: Context mapping (Tree-sitter)**
    *   Integrate `grep-ast` or a custom tree-sitter script to automatically generate the `.repo_map` on startup.
*   **Phase 3: The Edit Engine (Aider-style Diffs)**
    *   Implement a fuzzy diff matcher. Prompt the LLM strictly to use `<<<< SEARCH` and `==== REPLACE >>>>` blocks.
*   **Phase 4: Dual-Model Loop**
    *   Wire the Orchestrator to route the initial prompt to the R1 model, extract the output (ignoring the `<think>` tags for context size if needed, or keeping them for the Engineer), and pass the instruction to the Qwen model.