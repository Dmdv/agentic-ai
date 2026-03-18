# Agentic AI Infrastructure

This repository contains the specifications and proof-of-concept orchestration scripts for a massive-scale, local AI coding agent. It is designed to act as a fully autonomous, offline alternative to tools like *Claude Code* or *Aider*.

This infrastructure is **specifically engineered for frontier-class Apple Silicon workstations** (e.g., Mac Studio M3 Ultra with 512GB Unified Memory). 

By bypassing traditional `llama.cpp`/GGUF limitations and utilizing **Apple MLX**, this setup allows for the high-speed orchestration of state-of-the-art **Mixture-of-Experts (MoE)** models in the trillion-parameter range.

---

## 🏗 Architectural Paradigm

### 1. Apple MLX Native
Traditional local backends (LM Studio, Ollama) are CPU-first frameworks retrofitted for GPUs. They require slow, sequential loading of weights into VRAM. 

This infrastructure uses `mlx-lm`. MLX treats macOS Unified Memory as direct arrays. This allows the orchestrator script to instantly load, inference, and dump massive models (via Python garbage collection) with **zero-overhead memory swapping**.

### 2. Multi-Agent Swarm Orchestration (Architect & Engineer)
We implement a "System 2 (Thinking)" and "System 1 (Doing)" loop using a swarm of open-weight MoE models (as of Q1 2026). MoEs are strictly superior for Apple Silicon because they provide the reasoning of massive models while keeping active parameters low, maximizing the Mac's ~800GB/s memory bandwidth.

Our `mcp_swarm_loop.py` script orchestrates two distinct personas:
*   **Phase 1: The Architect (e.g., Kimi K2.5 - 1T MoE)**
    *   *Role:* Ingests the entire repository map and user prompt. It is strictly forbidden from writing code. Instead, it outputs a pristine JSON array of sequential steps (The Plan). It is then instantly unloaded from RAM.
*   **Phase 2: The Engineer (e.g., Qwen3-Coder-Next - 80B MoE)**
    *   *Role:* Loads into RAM, boots the MCP servers, and iteratively executes every step in the Architect's plan. At only 3B active parameters, it generates code and searches files at blistering speeds (150+ tokens/second).

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

## 📂 Repository Contents

### Specifications
*   `AGENTIC_INFRASTRUCTURE_SPECS_V5_MLX.md`: The final architectural blueprint.
*   *(V1 - V4 specs are preserved for historical context).*

### The Agents & Tools
*   `generate_repo_map.py`: The Tree-Sitter script that generates the `.repo_map` context file.
*   `mcp_server_bash.py`: The custom, secure Bash execution MCP server.
*   `mcp_multi_server_loop.py`: The base single-model orchestrator (boots all 6 MCP servers).
*   `mcp_swarm_loop.py`: The advanced Multi-Agent Swarm orchestrator (Architect -> Engineer pipeline).

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

### 1. Generating the Repository Map
Before starting the agent, build the Tree-Sitter map of your project:
```bash
source .venv/bin/activate
python generate_repo_map.py
```
*(This creates a `.repo_map` file that the Architect will ingest).*

### 2. Running the Agent Swarm via CLI
To unleash the dual-model Swarm on a complex task:

```bash
python mcp_swarm_loop.py --prompt "I need to deploy this repository. Read the repo map, write a multi-stage Dockerfile, and generate an AWS Terraform configuration to host it via ECS and an ALB."
```

### Changing the Underling Models
By default, the script uses `Qwen2.5-Coder-32B-Instruct-4bit` for both roles for testing. To utilize massive MoE models (assuming you have 128GB+ of Unified Memory), pass the HuggingFace MLX strings:
```bash
python mcp_swarm_loop.py \
  --architect "mlx-community/Kimi-K2.5-1T-4bit" \
  --engineer "mlx-community/Qwen3-Coder-Next-80B-4bit" \
  --prompt "Refactor the authentication module."
```

---

## 🖥 IDE & UI Integration (VS Code / Cursor / Roo Code)

While the Python Swarm CLI is powerful for fully autonomous, background tasks, you can use this incredible local intelligence directly inside your IDE (Visual Studio Code, Cursor, or Cline/Roo Code).

### 1. Start the MLX Local Server
Use the `mlx_lm.server` command to lock the model into your unified memory and expose an API at `http://localhost:8080/v1`.

```bash
source .venv/bin/activate
python -m mlx_lm.server --model mlx-community/Qwen3-Coder-Next-80B-4bit --port 8080
```

### 2. Configure Your IDE Extension (Cline, Roo Code, or Continue.dev)
In their settings UI, configure a new Custom / OpenAI-Compatible provider:

*   **Provider/API Type:** `OpenAI Compatible`
*   **Base URL:** `http://localhost:8080/v1`
*   **API Key:** `sk-mock-key`
*   **Model ID:** `mlx-community/Qwen3-Coder-Next-80B-4bit`
*   **Context Length:** `128000`

### 3. Connect the MCP Servers to your IDE
Extensions like **Cline** and **Roo Code** natively support the Model Context Protocol. Open the extension settings and edit the MCP configuration:
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
    },
    "local-secure-bash": {
      "command": "python3",
      "args": ["/Users/YourName/YourProject/mcp_server_bash.py"]
    }
  }
}
```
*Now, the AI agent inside VS Code will use your 512GB M3 Ultra to "think", and use the MCP servers defined in VS Code to act on your files and run secure bash tests.*

---

## 🔮 What's Next? (Further Capabilities)

The integration of **Apple MLX + Model Context Protocol (MCP)** creates a practically limitless ceiling for what this local AI can do. Here are the advanced workflows this infrastructure is capable of supporting next:

### 1. "Vibe Coding" & Vision-to-Code
By swapping the Engineer model to a natively multimodal model (like the `Kimi K2.5` or `Qwen3.5-VL` families) and installing `mlx-vlm`, you can feed the agent screenshots of UI designs.
*   **Workflow:** You drop a Figma screenshot into the folder and type: `"Build a React component that looks exactly like layout.png"`.

### 2. Structured Diff Editing (Aider Style)
*   **Improvement:** Implement a custom Python tool that accepts `SEARCH` and `REPLACE` blocks instead of replacing entire files via `write_file`. The Python script would use `difflib` to find the exact 5 lines of code and splice them in, saving massive generation time on 2000+ line files.
