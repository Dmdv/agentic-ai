# Technical Specification: Multi-Dimensional Context Compaction

## Context & Goal
The current `_compact_context` method relies on naive string truncation (`content[:100]`). This is insufficient for highly complex, long-running agentic loops. When a task is completed, simply truncating the message history destroys critical semantic context about *how* the task was completed, what files were touched, and what assumptions were made. We need a "multi-dimensional" summary similar to Claude's internal Context Compaction logic.

## Requirements
### Functional Requirements
1. The Orchestrator must intercept the message history when it reaches a specific token/message threshold or upon the completion of a major phase/task.
2. Instead of truncating strings, the Orchestrator must invoke an LLM (a fast, lightweight summarizer model or the Engineer itself) to generate a **Multi-Dimensional Compaction Report**.
3. The original message history must be replaced by this single, highly dense summary message.

### The Compaction Report Structure
The LLM must generate a summary containing:
- **Completed Actions:** (e.g., "Wrote 45 lines to auth.py")
- **Active System State:** (e.g., "Postgres running on port 5432")
- **Unresolved Threads:** (e.g., "Test X still failing, deferred to next step")
- **Key Decisions:** (e.g., "Chose JWT over session cookies because of stateless requirement")

## Architecture
- Update `mcp_multi_server_loop.py` -> `MCPAgenticLoop._compact_context`.
- Convert `_compact_context` into an `async` function that utilizes the `self.model` to dynamically summarize the history before scrubbing it.

## Edge Cases
- If the history is too large to summarize in one pass, chunk the summarization.
- Ensure the System Prompt and the original User Prompt are never compacted.