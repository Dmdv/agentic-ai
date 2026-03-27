# Agentic AI Infrastructure

This repository contains the specifications and proof-of-concept orchestration scripts for a massive-scale, local AI coding agent. It is designed to act as a fully autonomous, offline alternative to tools like *Claude Code* or *Aider*.

This infrastructure is **specifically engineered for frontier-class Apple Silicon workstations** (e.g., Mac Studio M3 Ultra with 512GB Unified Memory). 

By bypassing traditional `llama.cpp`/GGUF limitations and utilizing **Apple MLX**, this setup allows for the high-speed orchestration of state-of-the-art **Mixture-of-Experts (MoE)** models in the trillion-parameter range.

---

## 📑 Table of Contents
1. [Architectural Paradigm](#-architectural-paradigm)
2. [Repository Contents](#-repository-contents)
3. [Quick Start & Setup](#-quick-start--setup)
4. [HuggingFace Authentication (For Qwen3)](#-huggingface-authentication-for-qwen3)
5. [Daily Interactive Development (VS Code / Cline)](#-daily-interactive-development-vs-code--cline)
6. [Spec-Driven Development (The Headless Swarm)](#-spec-driven-development-the-headless-swarm)
7. [The AGENT_PLAN.md Context Recovery System](#-the-agent_planmd-context-recovery-system)
8. [What's Next? (Further Capabilities)](#-whats-next-further-capabilities)

---

## 🏗 Architectural Paradigm

### 1. Apple MLX Native
Traditional local backends (LM Studio, Ollama) are CPU-first frameworks retrofitted for GPUs. They require slow, sequential loading of weights into VRAM. 

This infrastructure uses `mlx-lm`. MLX treats macOS Unified Memory as direct arrays. This allows the orchestrator script to instantly load, inference, and dump massive models (via Python garbage collection) with **zero-overhead memory swapping**.

### 2. Tier 2 Procedural Memory (The Hive Mind)
Stateless agents forget everything the moment they shut down. We have integrated **ChromaDB** as a persistent, local Vector Database (`hive_memory.py`). When the `critical-reviewer` agent encounters a complex bug and fixes it, it permanently saves the "Lesson Learned" to the Vector DB. Future swarms automatically retrieve these lessons during the planning phase, meaning your local AI gets permanently smarter the more you use it.

### 3. Reversible Context Compaction
A massive flaw in traditional single-agent LLM loops is "Context Rot." If an agent executes 10 complex file edits, its context window fills with thousands of lines of terminal logs. We implemented an auto-compaction algorithm in the `MCPAgenticLoop`. If the context history exceeds limits, older, massive tool outputs are physically scrubbed from the `messages` array and replaced with tiny pointers (e.g., `[Prior tool output compacted to prevent context rot]`), preventing memory overflow while preserving logic.

### 4. Multi-Agent Swarm Orchestration (Architect & Engineer)
We implement a "System 2 (Thinking)" and "System 1 (Doing)" loop using a swarm of open-weight MoE models (as of Q1 2026). MoEs are strictly superior for Apple Silicon because they provide the reasoning of massive models while keeping active parameters low, maximizing the Mac's ~800GB/s memory bandwidth.

Our `mcp_swarm_loop.py` script orchestrates two distinct personas:
*   **Phase 1: The Architect (e.g., DeepSeek-R1-70B or Kimi K2.5-1T)**
    *   *Role:* Ingests the entire repository map and user prompt. It is strictly forbidden from writing code. Instead, it outputs a pristine JSON array of sequential steps and writes a master Markdown specification (`AGENT_PLAN.md`). It is then instantly unloaded from RAM to free up compute. 
    *   *Why Kimi K2.5?* Here is why Kimi K2.5 (or DeepSeek-R1) is arguably a better Architect than Qwen3-235B:
        1. **Native Agent Swarm Orchestration:** Kimi K2.5 was explicitly trained to orchestrate massive swarms. It natively understands how to break a complex prompt into 100+ parallel sub-tasks and map them to specialized agents. 
        2. **AIME Reasoning Benchmark:** Kimi K2.5 scores a staggering 96.1% on the AIME Math/Logic benchmark, putting it in the same tier as DeepSeek-R1 and OpenAI o3. (Qwen3 scores ~89%). This allows Kimi to catch edge cases in the SPEC.md that other models miss.
        3. **Hardware Efficiency:** Kimi K2.5 is a 1-Trillion parameter MoE model, but it only activates 32 Billion parameters per token. This makes it incredibly fast on your M3 Ultra compared to running a dense model of equivalent intelligence.
*   **Phase 2: The Engineer (e.g., Qwen3-Coder-Next - 80B 8-bit)**
    *   *Role:* Loads into RAM, boots the MCP servers, and iteratively executes every step in the Architect's plan. At only 3B active parameters, it generates code and searches files at blistering speeds (150+ tokens/second).

#### VRAM Cost on M3 Ultra (512GB)
If you run Kimi K2.5 and Qwen3 simultaneously for your swarm:
*   **The Architect:** `Kimi-K2.5-1T-4bit` requires roughly ~500GB of total disk space, but due to quantization and MLX unified memory mapping, loading it safely consumes about **~260GB** of active VRAM.
*   **The Engineer:** `Qwen3-Coder-Next-80B-8bit` consumes about **~85GB** of VRAM.
*   **Total:** **~345GB of VRAM** (Well within your machine's ~400GB safe allocation limit!).

### 3. Tree-Sitter Polyglot Repo Mapping
Dumping raw code into a context window wastes compute and invites hallucinations. We use **Tree-Sitter** to build semantic "Skeleton Maps" of the repository.
*   **Multi-Language:** Natively parses Python, JavaScript, TypeScript, Rust, Go, C++, etc.
*   **DevOps Support:** Natively parses Dockerfiles, Makefiles, YAML, TOML, and Terraform (.tf).
*   **Result:** The Architect model sees the exact signatures, classes, and infrastructure topologies of the entire workspace in under 5,000 tokens via the `.repo_map` file.

### 4. Model Context Protocol (MCP) + Secure Bash
Instead of hardcoding custom Python tools, the Engineer model interacts with your machine through **6 distinct MCP Servers**:
1.  **Filesystem:** Safely reads and edits files.
2.  **Git:** Handles staging, committing, and branching.
3.  **SQLite:** Executes direct SQL migrations and queries.
4.  **Fetch:** Downloads and parses web pages to raw markdown (Direct RAG).
5.  **Memory:** A Knowledge Graph server for the Swarm to share context across sessions.
6.  **Secure Bash (`mcp_server_bash.py`):** A custom-built, highly constrained Python server that allows the agent to run linters and tests (`pytest`, `npm run test`, `cargo build`) to close the Autonomous CI/CD Loop, without the security risk of giving an AI raw terminal access.

---

## 📂 Repository Contents (The Orchestrator Scripts)

You do not need to use all of the Python scripts in this repository. They exist as a historical record of how the architecture evolved from a basic "Proof of Concept" into a massive "Enterprise Swarm".

### The "Historical" Scripts (Proof of Concepts)
These scripts were stepping stones to prove the Apple MLX and MCP technology worked before we built the massive swarm. You can ignore these for daily use:
1. `agentic_loop.py`: The very first script we wrote. It doesn't connect to the real file system. It was just a proof-of-concept to see if the Qwen model was smart enough to output a JSON tool call instead of just chatting.
2. `mcp_agentic_loop.py`: Our second iteration. It successfully hooked Qwen up to a single MCP Server (the filesystem).
3. `mcp_multi_server_loop.py`: The third iteration. This proved we could connect the agent to 6 different MCP servers at once (Git, Bash, SQLite, etc.). *This is the foundational engine that powers the Swarms.*

### The "Production" Scripts (The ones you actually use)
These are the two scripts you will actually use depending on how complex your task is.

#### 1. The Quick Fixer (`mcp_swarm_loop.py`)
*   **What it is:** The basic Multi-Agent Swarm.
*   **How it works:** It uses two models (Architect and Engineer). It generates a quick plan and then executes it sequentially.
*   **When to use it:** Use this for fast, single-domain tasks. It is fast and gets straight to the point without generating massive documentation.
*   **How to start it:**
    ```bash
    python mcp_swarm_loop.py --prompt "Fix the bug on line 45 of auth.py and run the tests."
    ```

#### 2. The Enterprise Builder (`mcp_sdd_swarm.py`)
*   **What it is:** The **Spec-Driven Development (SDD)** Swarm. This is the crown jewel of the repository.
*   **How it works:** It enforces a rigorous 3-phase pipeline. It forces the `spec-writer` to write a huge Markdown document, forces the `researcher` to critique it, pulls your corporate SOPs from the `skills/` directory, and runs the actual coding tasks in parallel.
*   **When to use it:** Use this when you are building a feature from scratch or doing a massive refactor. You run this script, walk away for 30 minutes, and come back to a fully documented, tested, and containerized project.
*   **How to start it:**
    ```bash
    python mcp_sdd_swarm.py --prompt "Build me a new Python microservice that connects to SQLite and uses JWT auth."
    ```

---

## 🚀 Quick Start & Setup

### Prerequisites
*   Apple Silicon Mac (M-series).
*   High unified memory (32GB+ required for smaller models; 128GB+ recommended for MoEs).
*   Python 3.11+
*   Node.js (for npx/MCP servers).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Dmdv/agentic-ai.git
   cd agentic-ai
   ```
2. Set up the Python virtual environment and install the MLX/MCP/Tree-Sitter dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install mlx-lm mcp pydantic-ai mcp-server-git mcp-server-sqlite mcp-server-fetch tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript tree-sitter-rust tree-sitter-go tree-sitter-dockerfile tree-sitter-yaml tree-sitter-toml tree-sitter-bash tree-sitter-make
   ```
3. Install the required Node.js MCP servers globally:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @modelcontextprotocol/server-memory
   ```

---

## 🔑 HuggingFace Authentication (For Qwen3)

The most powerful models in this repository (like `Qwen3-235B` or `Qwen3-Coder-Next-80B`) are "gated" by HuggingFace. You must accept their license agreement online before downloading them.

To allow the Apple MLX engine to securely download these massive weights into your unified memory, you must provide your HuggingFace Access Token.

1.  Create a `.env` file in the root of your project.
2.  Add your HuggingFace token:
    ```env
    HF_TOKEN=hf_YourActualTokenStringHere
    ```
The Python orchestrator will automatically load this `.env` file into memory, instantly bypassing the `401 Unauthorized` block and initializing the massive download on the first run.

---

## ⚓ The `AGENT_PLAN.md` Context Recovery System

A massive flaw in traditional single-agent LLM loops is "Context Degradation." If an agent executes 10 complex file edits, its context window fills with thousands of lines of terminal logs and code diffs. By step 8, it forgets the original architecture it was trying to build.

**The Swarm solves this using the `AGENT_PLAN.md` anchor file.**

1.  **Creation:** During Phase 1, the Architect model writes a highly detailed Markdown specification containing the master goal, the chosen architecture, and the required logic. The Python script physically saves this to `AGENT_PLAN.md`.
2.  **Recovery:** The Engineer's system prompt contains a strict directive: *"If you ever lose context of the overall goal or architecture, you should use your file tools to read `AGENT_PLAN.md`."*
3.  **Result:** If the Engineer gets confused deep into a debugging loop, it will autonomously pause, read the master specification file off the local disk, re-align itself with the Architect's original vision, and continue coding without hallucinating.

---

## 🛠 Daily Interactive Development (VS Code / Cline)

Is the Python CLI the only way to develop? **Absolutely not.** The Python orchestrator scripts we built (`mcp_sdd_swarm.py`) are known as **"Headless Orchestrators."** They are designed for fire-and-forget automation (e.g., "Here is a massive refactor, run overnight, fix your own bugs, and leave a report when I wake up").

For your daily, interactive coding, you should use a visual IDE extension (like **Cline** or **Roo Code**) inside VS Code. 

Here is how you develop interactively with your local MLX LLM:

### 1. Start the Brain
In a terminal, lock the model into your M3 Ultra's RAM and create a local API:
```bash
source .venv/bin/activate
python -m mlx_lm.server --model mlx-community/Qwen3-235B-8bit --port 8080
```

### 2. Configure the GUI
Open VS Code and install the **Cline** extension. In its settings, configure the custom provider:
*   **Provider/API Type:** `OpenAI Compatible`
*   **Base URL:** `http://localhost:8080/v1`
*   **API Key:** `sk-mock-key`
*   **Model ID:** `mlx-community/Qwen3-235B-8bit`
*   **Context Length:** `128000`

### 3. Connect the Hands (MCP)
In the extension settings, attach your MCP servers (Filesystem, Bash, SQLite) via the UI:
```json
{
  "mcpServers": {
    "local-filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/YourName/YourProject"]
    },
    "local-sqlite": {
      "command": "python3",
      "args": ["-m", "mcp_server_sqlite", "--db-path", "/Users/YourName/YourProject/agent.db"]
    }
  }
}
```
*Now, you have a beautiful chat window in VS Code. When the agent wants to run a Bash command or edit a file, it pops up a clean GUI prompt asking for your approval. You can see the diffs visually, watch it think, and interrupt it instantly.*

---

## 🚀 Spec-Driven Development (The Headless Swarm)

Jumping straight into coding ("vibe coding") fails on large projects. This repository features a completely autonomous, Headless Orchestrator (`mcp_sdd_swarm.py`) inspired by the **Claude Superpowers** plugin methodology.

It utilizes 4 highly specialized agents from the `agents/` folder:
*   `spec-writer.md`
*   `researcher.md` (uses web tools to read modern documentation)
*   `planning-agent.md`
*   `requirement-validator.md`

### How the SDD Swarm Works:

**Phase 1: Spec Generation & Critique Loop**
1. The `spec-writer` takes your initial prompt and creates a `SPEC.md` document detailing the architecture, edge cases, and requirements.
2. The `researcher` reads `SPEC.md`, uses its web-fetch tool to check documentation, and writes critiques to `RESEARCH_REPORT.md`.
3. The `critical-reviewer` rigorously reads the spec to ensure there are no logical gaps.
4. If issues are found, the orchestrator sends it back to the `spec-writer`. **It loops this process until the Reviewer outputs exactly "REVIEW PASSED".**

**Phase 2: Structured Planning**
Once `SPEC.md` is perfect, the Swarm loads the `planning-agent`. It breaks the Spec down into a JSON array of micro-tasks and assigns specific agents to them. 

**Phase 3: Execution with Mandatory TDD Validations**
The Orchestrator loops through the plan. For *every single task* the Engineer completes, the Python script forcefully interrupts and injects two steps:
1. **Validation:** It hot-swaps to the `requirement-validator.md` to ensure the new code actually fulfills the `SPEC.md`. 
2. **Review:** It hot-swaps to `critical-reviewer.md` to run the tests via bash. If the tests fail, the Engineer is forced to fix them before moving to the next task on the list.

### Running the SDD Swarm

1. Generate your `.repo_map`:
```bash
python generate_repo_map.py
```

2. Unleash the Swarm:
```bash
python mcp_sdd_swarm.py --prompt "I need a complete Python FastAPI backend for a library management system with JWT authentication and SQLite."
```
*(The Swarm will run autonomously for hours, generating the specs, breaking down the tasks, and writing the test-driven code. Read the resulting `SWARM_EXECUTION_REPORT.md` when it finishes).*

---

## 🔮 What's Next? (Further Capabilities)

The integration of **Apple MLX + Model Context Protocol (MCP)** creates a practically limitless ceiling for what this local AI can do. Here are the advanced workflows this infrastructure is capable of supporting next:

### 1. "Vibe Coding" & Vision-to-Code
By swapping the Engineer model to a natively multimodal model (like the `Kimi K2.5` or `Qwen3.5-VL` families) and installing `mlx-vlm`, you can feed the agent screenshots of UI designs.
*   **Workflow:** You drop a Figma screenshot into the folder and type: `"Build a React component that looks exactly like layout.png"`.

### 2. Structured Diff Editing (Aider Style)
*   **Improvement:** Implement a custom Python tool that accepts `SEARCH` and `REPLACE` blocks instead of replacing entire files via `write_file`. The Python script would use `difflib` to find the exact 5 lines of code and splice them in, saving massive generation time on 2000+ line files.