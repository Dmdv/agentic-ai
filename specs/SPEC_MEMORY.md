# Technical Specification: Tier 2 Procedural Memory (Vector DB)

## Context & Goal
Stateless agents forget their debugging lessons and context the moment the script exits. By implementing a local Vector Database (ChromaDB), we can give the Swarm a persistent "Hive Mind". When an agent learns something (e.g., a specific syntax fix or an infrastructure dependency), it stores it. Future swarms can query this memory.

## Requirements
### Functional Requirements
1. **The Vector DB:** Use `chromadb` to maintain a local `.hive_memory` database.
2. **Write Phase:** At the end of every task execution, the `critical-reviewer` agent must generate a concise "Lesson Learned" string. The Orchestrator must embed and store this string in ChromaDB.
3. **Read Phase:** Before the `spec-writer` or `planning-agent` begins a new task, the Orchestrator must query ChromaDB using the user's prompt to retrieve the Top K (e.g., 3) most relevant past lessons, injecting them into the System Prompt.

## Architecture
- `hive_memory.py`: A wrapper class around ChromaDB with `add_lesson` and `get_relevant_lessons` methods.
- `mcp_sdd_swarm.py`: Inject `hive_memory.get_relevant_lessons` into the Phase 1 generation prompt. Add a prompt to `critical-reviewer` in Phase 3 to write lessons to `LESSONS.txt`, which the Python script then reads and passes to `hive_memory.add_lesson`.

## Edge Cases
- Ensure the Vector DB gracefully handles empty queries or identical duplicate lessons without throwing errors.