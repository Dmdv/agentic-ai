# Local Agentic Coding Infrastructure Specifications (V5: Apple MLX Native)

## 1. Executive Summary & The MLX Paradigm Shift
This specification fully embraces **Apple MLX**, the machine learning framework specifically engineered by Apple for Apple Silicon. 

For a workstation like the **Mac Studio M3 Ultra (512GB Unified Memory)**, using `llama.cpp`-based backends leaves massive performance on the table. MLX is built from the ground up for the Apple GPU (Metal) and unified memory architecture. 

By pivoting to MLX, you achieve:
1.  **Massively higher Tokens/Second:** Native Metal acceleration perfectly maps matrix multiplications across the 76 GPU cores.
2.  **Zero-Overhead Memory Swapping:** MLX uses unified memory directly. Loading and swapping massive models happens almost instantaneously via standard Python garbage collection (`gc.collect()`), unlike the slow disk-to-VRAM loading of traditional backends.
3.  **Optimal MoE Execution:** Mixture-of-Experts (MoE) models thrive on Apple Silicon because the primary bottleneck for MoE is memory bandwidth, not compute. The M3 Ultra's ~800GB/s bandwidth allows rapid fetching of sparse expert weights, making MoEs incredibly fast locally.

---

## 2. The AI Roster: State-of-the-Art MoE Models (March 2026)

You are absolutely correct: **MoE (Mixture of Experts) is strictly superior for local agentic workflows.** MoEs give you the reasoning capability of a massive model (hundreds of billions of parameters) but only activate a fraction of them (e.g., 3B or 32B) per token. This means you get GPT-4o level intelligence at the speed of a tiny 8B model.

We use a dual-model Cognitive Architecture:

### 2.1 The Architect (System 2): Kimi K2.5 (1 Trillion Parameter MoE)
*   **Model:** `mlx-community/Kimi-K2.5-1T-4bit`
*   **Architecture:** 1 Trillion total parameters, **32B active parameters**.
*   **Role:** The Architect. Ingests the entire repository, processes complex multi-step user prompts, and outputs the architectural plan. 
*   **Why K2.5?:** Released in Jan 2026, it is natively multimodal and features "Agent Swarm" capabilities. Even at 1T parameters, a 4-bit quant takes ~500GB, fitting *exactly* within your maxed-out M3 Ultra (though you may opt for the slightly smaller `Kimi-Dev-72B` if you want to leave more RAM for the OS and Docker).

### 2.2 The Engineer (System 1): Qwen3-Coder-Next (80B MoE)
*   **Model:** `mlx-community/Qwen3-Coder-Next-80B-4bit` (or 8-bit).
*   **Architecture:** 80B total parameters, **only 3B active parameters**.
*   **Role:** The Executer. Takes Kimi's plan and rapidly executes `SEARCH/REPLACE` diffs.
*   **Why Qwen3-Coder-Next?:** Released in Feb 2026 specifically for agentic coding. Because only 3B parameters are active per token, this model will generate code at blistering speeds (150+ tokens/second) on your machine, making the iterative read/write/test loop feel instantaneous.

---

## 3. Orchestration Engine: Pure Python + `mlx-lm`

Instead of relying on an external server like `lms server` or Ollama, your infrastructure will be a **pure Python script** utilizing the `mlx-lm` library.

### 3.1 Setup
```bash
# Create a dedicated virtual environment
python3 -m venv agentic-env
source agentic-env/bin/activate

# Install Apple MLX and Model Context Protocol SDK
pip install mlx-lm mcp pydantic-ai
```

### 3.2 Dynamic MLX Orchestration (Python Pseudocode)
Swapping models in MLX is instantaneous. You can have Kimi plan, then swap to Qwen3 to execute.

```python
from mlx_lm import load, generate
import gc

def run_architect_phase(prompt, context):
    print("Loading Kimi K2.5 (Architect)...")
    model, tokenizer = load("mlx-community/Kimi-K2.5-1T-4bit")
    
    plan = generate(model, tokenizer, prompt=f"{context}\n\n{prompt}", max_tokens=8000)
    
    # Free memory instantly so Qwen3 can load
    del model
    del tokenizer
    gc.collect() 
    
    return plan

def run_engineer_phase(plan):
    print("Loading Qwen3-Coder-Next (Engineer)...")
    model, tokenizer = load("mlx-community/Qwen3-Coder-Next-80B-8bit")
    
    # Start loop for generating SEARCH/REPLACE blocks
    diffs = generate(model, tokenizer, prompt=plan, max_tokens=2000)
    return diffs
```

---

## 4. Tooling & Context (Model Context Protocol)

The actual loop utilizes the **Model Context Protocol (MCP)** to interact with your filesystem, tightly integrated into the MLX generation loop.

1.  **Initialization:** Use `mcp-server-filesystem` to dump the necessary `src/` files into Kimi K2.5's massive context window.
2.  **Architecting:** `mlx_lm.generate` runs Kimi.
3.  **Engineering:** The script unloads Kimi, loads Qwen3-Coder-Next, and passes the Architect's plan.
4.  **Executing Diffs:** Qwen3 outputs structured diffs. The Python script parses these and uses `mcp-server-filesystem` to safely apply the edits.
5.  **Validation:** `mcp-server-bash` runs the test suite. If it fails, the error log is appended to Qwen3's context, and `mlx_lm.generate` is called again.

## 5. Next Steps for Implementation

1.  **Install MLX:** `pip install mlx-lm`
2.  **Download & Test Models via MLX:**
    ```bash
    # Test Qwen3 directly in terminal via MLX
    mlx_lm.chat --model mlx-community/Qwen3-Coder-Next-80B-4bit
    ```
3.  **Develop the MCP Client:** We write the Python orchestration script that ties `mlx-lm` together with your local MCP servers to form the autonomous loop.