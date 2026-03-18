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
The Python orchestrator spins up multiple background MCP Servers (e.g., `@modelcontextprotocol/server-filesystem` and `mcp-server-git`), aggregates their JSON schemas, and dynamically injects them into the Qwen Engineer model to grant it physical access to the local machine.

---

## 📂 Repository Contents

### Specifications
*   `AGENTIC_INFRASTRUCTURE_SPECS_V5_MLX.md`: The final, definitive architectural blueprint detailing the MLX + MoE + MCP strategy. *(Read this first).*
*   *(V1 - V4 specs are preserved for historical context on the pivot from REST APIs to MLX).*

### Proof-of-Concept Scripts
*   `test_mlx.py`: A basic script to verify Apple MLX is installed and can rapidly load, generate, and dump an Instruct model from memory.
*   `agentic_loop.py`: A foundational mock loop demonstrating how Qwen outputs JSON tool-calls when prompted.
*   `mcp_agentic_loop.py`: A functional loop wired to a single MCP Server (Filesystem) to allow the agent to read and write real files.
*   `mcp_multi_server_loop.py`: The advanced orchestrator. It boots multiple distinct MCP servers (Filesystem + Git), aggregates all available tools into a massive schema, and intelligently routes the agent's tool calls to the correct background process.

---

## 🚀 Quick Start Guide

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
   pip install mlx-lm mcp pydantic-ai mcp-server-git
   ```

### Running the Agent
By default, the script uses a smaller 32B model for testing. You can run the multi-server MCP loop to see the agent interact with your filesystem and git repository:

```bash
python mcp_multi_server_loop.py --prompt "Check the git status of this repository."
```

To run the massive 2026 MoE models (assuming you have 128GB+ of Unified Memory), pass the HuggingFace MLX community string:
```bash
python mcp_multi_server_loop.py --model "mlx-community/Qwen3-Coder-Next-80B-4bit"
```
*(Note: The model will download from HuggingFace on the first run).*
