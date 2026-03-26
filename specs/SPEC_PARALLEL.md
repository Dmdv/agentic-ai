# Technical Specification: True Parallel Execution (Multi-Agent Processing)

## Context & Goal
The current Swarm (`mcp_sdd_swarm.py`) executes the Architect's plan sequentially. This is a bottleneck. The Mac Studio M3 Ultra (512GB) has the memory bandwidth to run multiple instances of the Engineer model simultaneously. When the Architect outputs independent tasks (e.g., "Build Frontend Component" and "Build Backend API"), these should be executed concurrently.

## Requirements
### Functional Requirements
1. The `planning-agent` must be instructed to group tasks into "Batches" or specify dependency graphs (e.g., `{"task": "x", "depends_on": []}`).
2. The Orchestrator (`_run_execution_phase`) must evaluate the JSON plan and identify independent tasks.
3. The Orchestrator must use `asyncio.gather()` to spin up multiple parallel `MCPAgenticLoop` instances, assigning different tasks to each.
4. Each concurrent `MCPAgenticLoop` must maintain its own isolated message history to prevent cross-contamination.

## Architecture
- Update `mcp_sdd_swarm.py` `_run_execution_phase` to use `asyncio.gather`.
- Ensure `MCPAgenticLoop` class is fully thread-safe and async-native (specifically the `mlx_lm.generate` call which must be wrapped in `asyncio.to_thread` to prevent blocking the event loop).

## Edge Cases
- File collisions: If two agents try to write to the same file simultaneously, it will corrupt the code. The `planning-agent` must be strictly instructed to assign tasks that touch entirely separate files or domains if they are to be run in parallel.