# Local Agentic Coding Infrastructure Specifications (V4: Kimi & Qwen3 on M3 Ultra)

## 1. Executive Summary & Acknowledgments
This V4 specification is custom-engineered for your **Mac Studio M3 Ultra (512GB Unified Memory)**. It corrects previous oversights by integrating exact instructions for your installed **LM Studio CLI (`lms`)**, and pivots the model architecture entirely towards the current bleeding edge of open-weight coding models: **Qwen3/Qwen3.5-Coder** and Moonshot AI's **Kimi-Dev / Kimi K2.5**.

Because you possess 512GB of Unified Memory, you bypass the limitations of standard local AI (which relies on 8B router models). You have the capability to run massive Mixture-of-Expert (MoE) models and trillion-parameter architectures locally.

---

## 2. The AI Roster: Kimi & Qwen3

To build an agentic infrastructure akin to Claude Code, we employ a dual-model Cognitive Architecture using the absolute latest open-weights.

### 2.1 The Architect (System 2): Kimi K2.5 or Kimi-Dev-72B
Moonshot AI's Kimi series currently dominates the SWE-bench Verified leaderboards for open-source models.
*   **Model Options:** 
    *   `Kimi-Dev-72B` (Intensely trained via RL for bug-fixing and repository patching).
    *   `Kimi K2.5` (Trillion-parameter MoE, heavily quantized for local execution).
*   **Role:** The Architect. You feed it the entire repository context (up to 128k+ tokens). It outputs a complex, step-by-step implementation plan and architectural diagram.
*   **Memory Footprint:** A 4-bit GGUF of Kimi-Dev-72B takes ~45GB. K2.5 requires ~240GB. Both fit comfortably in your 512GB RAM, utilizing the M3 Ultra's ~800GB/s bandwidth.

### 2.2 The Engineer (System 1): Qwen3.5-Coder (or Qwen3-Coder-Next)
Alibaba’s Qwen3 series introduces highly efficient MoEs with dedicated "Thinking Modes."
*   **Model Options:** `Qwen3.5-Coder-35B-A3B` or the flagship `Qwen3-Coder-Next (80B MoE)`.
*   **Role:** The Executer. It takes Kimi's exact plan and rapidly executes file edits, issues bash commands, and outputs `SEARCH/REPLACE` blocks. Because it's an MoE with a smaller *active* parameter count (e.g., 3B active out of 35B), it runs at blistering speeds (100+ tokens/second) on Apple Silicon, making it the perfect loop-driven engineer.

---

## 3. Orchestration Engine: LM Studio CLI (`lms`)

I confirmed that you have the LM Studio CLI installed at `/Users/dima/.lmstudio/bin/lms`. Instead of relying on Ollama or the LM Studio GUI, your infrastructure will be programmatically orchestrated via `lms`.

### 3.1 Why `lms` for Agentic Loops?
`lms` allows a Python or Node.js orchestrator script to dynamically load and unload models into VRAM via bash, ensuring you aren't permanently locking up memory.

### 3.2 Dynamic Infrastructure Workflow
Your orchestration script (e.g., in Python) can execute these commands sequentially:

1.  **Start the Local Server:**
    ```bash
    lms server start
    ```
2.  **Load the Architect (Kimi) for Planning:**
    ```bash
    lms load "MoonshotAI/Kimi-Dev-72B-GGUF" --gpu "max" --context-length 128000
    ```
    *The Python script makes an OpenAI-compatible API call to `http://localhost:1234/v1` to get the plan.*
3.  **Unload Architect & Load Engineer (Qwen3):**
    ```bash
    lms unload --all
    lms load "Qwen/Qwen3.5-Coder-35B-GGUF" --gpu "max" --context-length 64000
    ```
    *The Python script now enters the rapid read/write/test loop with Qwen3.*

---

## 4. Agentic Loop & Tooling (Model Context Protocol)

With the models selected and `lms` handling VRAM orchestration, the actual agentic loop relies on **Model Context Protocol (MCP)**.

### 4.1 "Context Stuffing" vs. Chunking
Because your M3 Ultra can handle 128k+ tokens with ease:
*   **No more Grep:** You do not need restrictive search tools.
*   **Massive Reads:** The agent will use `mcp-server-filesystem` to dump entire directories (`src/`, `components/`) directly into Qwen3's prompt. 
*   **Zero Hallucinated Imports:** Supplying massive context ensures the models know exactly which functions exist.

### 4.2 The Loop Execution
1.  **Initialize:** User runs the CLI (e.g., `agentic-code --task "Migrate DB to PostgreSQL"`).
2.  **Context Pull:** MCP pulls a Tree-Sitter repository map and the full text of relevant schema files.
3.  **Architect (Kimi):** `lms` loads Kimi-Dev. Kimi outputs the `PLAN`.
4.  **Engineer (Qwen3):** `lms` swaps to Qwen3. Qwen3 begins emitting `SEARCH/REPLACE` diffs.
5.  **Verification Engine:**
    *   The Python orchestrator applies the diff locally.
    *   It uses `mcp-server-bash` to run `npm test` or `cargo test`.
    *   If a test fails, the stdout/stderr is immediately fed back to Qwen3. (Loop limit: 5).

---

## 5. Next Steps for Building

To construct this locally:

1.  **Download the GGUFs via `lms`:**
    ```bash
    lms get "MoonshotAI/Kimi-Dev-72B-GGUF"
    lms get "Qwen/Qwen3.5-Coder-35B-GGUF"
    ```
2.  **Configure Memory Limits:**
    Ensure macOS allows the GPU to utilize the vast majority of your 512GB RAM:
    ```bash
    sudo sysctl iogpu.wired_limit_mb=409600
    ```
3.  **Build the Orchestrator:**
    Use a lightweight framework like **HuggingFace SmolAgents** or **PydanticAI** to write the CLI. Point the framework's API base URL to `http://localhost:1234/v1` (LM Studio's default port) and wrap the `lms load/unload` bash commands inside the agent's initialization phase.