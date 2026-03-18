# Agentic AI Infrastructure

This repository contains the specifications and proof-of-concept orchestration scripts for a massive-scale, local AI coding agent. It is designed to act as a fully autonomous, offline alternative to tools like *Claude Code* or *Aider*.

This infrastructure is **specifically engineered for frontier-class Apple Silicon workstations** (e.g., Mac Studio M3 Ultra with 512GB Unified Memory). 

By bypassing traditional `llama.cpp`/GGUF limitations and utilizing **Apple MLX**, this setup allows for the high-speed orchestration of state-of-the-art **Mixture-of-Experts (MoE)** models in the trillion-parameter range.

---

## 🏗 Architectural Paradigm

### 1. Apple MLX Native
Traditional local backends (LM Studio, Ollama) are CPU-first frameworks retrofitted for GPUs. They require slow, sequential loading of weights into VRAM. 

This infrastructure uses `mlx-lm`. MLX treats macOS Unified Memory as direct arrays. This allows the orchestrator script to instantly load, inference, and dump massive models (via Python garbage collection) with **zero-overhead memory swapping**.

### 2. The Dual-Model MoE Cognitive Loop
We implement a "System 2 (Thinking)" and "System 1 (Doing)" loop using the latest open-weight MoE models (as of Q1 2026). MoEs are strictly superior for Apple Silicon because they provide the reasoning of massive models while keeping active parameters low, maximizing the Mac's ~800GB/s memory bandwidth.

*   **The Architect (System 2): Kimi K2.5 (1 Trillion Parameter MoE)**
    *   *Active Parameters:* 32B
    *   *Role:* Ingests the entire repository (up to 256k tokens), processes complex multi-step prompts, and outputs an architectural blueprint.
*   **The Engineer (System 1): Qwen3-Coder-Next (80B MoE)**
    *   *Active Parameters:* 3B
    *   *Role:* Takes the Architect's plan and rapidly executes `SEARCH/REPLACE` diffs. At only 3B active parameters, it generates code at blistering speeds (150+ tokens/second).

### 3. Model Context Protocol (MCP)
Instead of hardcoding custom Python tools for file reading or bash execution, the loop utilizes the **Model Context Protocol**. 
The Python orchestrator spins up multiple background MCP Servers (`@modelcontextprotocol/server-filesystem`, `mcp-server-git`, `mcp-server-sqlite`, and `@modelcontextprotocol/server-puppeteer`), aggregates their JSON schemas, and dynamically injects them into the Qwen Engineer model to grant it physical access to the local machine.

---

## 📂 Repository Contents

### Specifications
*   `AGENTIC_INFRASTRUCTURE_SPECS_V5_MLX.md`: The final, definitive architectural blueprint detailing the MLX + MoE + MCP strategy. *(Read this first).*
*   *(V1 - V4 specs are preserved for historical context on the pivot from REST APIs to MLX).*

### Proof-of-Concept Scripts
*   `test_mlx.py`: A basic script to verify Apple MLX is installed and can rapidly load, generate, and dump an Instruct model from memory.
*   `agentic_loop.py`: A foundational mock loop demonstrating how Qwen outputs JSON tool-calls when prompted.
*   `mcp_agentic_loop.py`: A functional loop wired to a single MCP Server (Filesystem) to allow the agent to read and write real files.
*   `mcp_multi_server_loop.py`: The advanced orchestrator. It boots **four distinct MCP servers** (Filesystem, Git, SQLite, and Puppeteer), aggregates all available tools into a massive schema, and intelligently routes the agent's tool calls to the correct background process.

---

## 🚀 Quick Start & Usage Guide

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
2. Set up the Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install mlx-lm mcp pydantic-ai mcp-server-git mcp-server-sqlite
   ```
3. Install the required Node.js MCP servers globally:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @modelcontextprotocol/server-puppeteer
   ```

### Using the Agent
The main orchestrator is `mcp_multi_server_loop.py`. You can interact with it by passing a natural language `--prompt` describing the task you want the agent to accomplish.

**Example 1: Basic File System Inspection**
```bash
source .venv/bin/activate
python mcp_multi_server_loop.py --prompt "List all the files in the current directory and read the contents of 'README.md' to give me a summary."
```

**Example 2: Bug Fixing & Autonomous Coding**
```bash
python mcp_multi_server_loop.py --prompt "The code in 'src/main.py' is throwing a KeyError. Please read it, identify the issue, and rewrite the file to fix it."
```

**Example 3: Git Operations**
```bash
python mcp_multi_server_loop.py --prompt "Check the git status. If there are untracked files, create a new branch called 'feat/updates', stage them, and commit with a descriptive message."
```

**Example 4: Database Engineering (SQLite)**
```bash
python mcp_multi_server_loop.py --prompt "Connect to 'agent.db'. Create a 'users' table with id, name, and email. Then insert 3 mock users into it and read them back."
```

**Example 5: Web Scraping & RAG (Puppeteer)**
```bash
python mcp_multi_server_loop.py --prompt "Use your web browsing tools to navigate to 'https://news.ycombinator.com' and list the top 3 headlines."
```

### Changing the Underling Model
By default, the script uses `Qwen2.5-Coder-32B-Instruct-4bit` for a fast balance of speed and intelligence. To utilize massive 2026 MoE models (assuming you have 128GB+ of Unified Memory), pass the HuggingFace MLX community string:
```bash
python mcp_multi_server_loop.py \
  --model "mlx-community/Qwen3-Coder-Next-80B-4bit" \
  --prompt "Refactor the authentication module."
```
*(Note: The model will download from HuggingFace directly into unified memory on the first run).*

---

## 🔮 What's Next? (Further Capabilities)

The integration of **Apple MLX + Model Context Protocol (MCP)** creates a practically limitless ceiling for what this local AI can do. Because MCP standardizes tool use, you can expand this agent without writing custom Python parsing code. 

Here are the advanced workflows this infrastructure is capable of supporting next:

### 1. "Vibe Coding" & Vision-to-Code
By swapping the Engineer model to a natively multimodal model (like the `Kimi K2.5` or `Qwen3.5-VL` families) and using `mlx-vlm`, you can feed the agent screenshots of UI designs.
*   **Workflow:** You drop a Figma screenshot into the folder and type: `"Build a React component that looks exactly like layout.png"`. The agent sees the image, writes the code, and uses the filesystem MCP to save it.

### 2. Autonomous Testing & CI/CD Loops
By adding an MCP Bash execution server (or creating a secure wrapper for one), you close the iteration loop.
*   **Workflow:** The agent writes code -> The agent autonomously runs `npm run test` or `cargo build` -> The agent catches its own compiler errors or failed assertions from `stderr` -> The agent edits the code to fix them *before* returning control to you.

### 3. Multi-Agent Swarms
Since model loading via MLX is near-instantaneous:
*   **Workflow:** The orchestrator script can be upgraded to boot **Kimi (The Architect)** to write a 10-step plan, and then loop **Qwen3 (The Engineer)** 10 times to execute each step, effectively acting as an entire local development team running concurrently on your M3 Ultra.
