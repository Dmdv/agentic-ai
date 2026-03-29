# Master Prompt Templates for Agentic AI Swarm

These are highly optimized, copy-pasteable prompt templates designed to maximize the effectiveness of the Spec-Driven Development (SDD) Swarm and the underlying Architect/Engineer model dynamic.

---

## 1. New Project Initialization (The "Blank Canvas")
*Use this when starting a completely new project. It forces the Architect to utilize your corporate `skills/` and strictly sandbox itself.*

```text
Initialize a new [LANGUAGE/FRAMEWORK] project inside the directory 'project_name'. 
You MUST proactively read the relevant corporate skills from the `skills/` directory before writing any code.
Strictly enforce [LINTING TOOL] and [TESTING FRAMEWORK]. 
The goal of the project is to: [DESCRIPTION OF WHAT TO BUILD].
Ensure you write a complete test suite before considering the project complete.
```

## 2. The "Memory Book" / Onboarding Document Generation
*Use this when you want the Swarm to read an existing, poorly documented repository and write a comprehensive "Memory Book" so future AI agents (or humans) can understand it.*

```text
Acting as a Senior Systems Architect, perform a deep-dive audit of the current repository.
I want you to write a comprehensive 'MEMORY_BOOK.md' file at the root.
The memory book must include:
1. The exact tech stack and versions used.
2. The core architectural design patterns (e.g., MVC, Event-Driven).
3. The data flow of the primary application loop.
4. A list of known technical debt or areas that lack test coverage.
Do not modify any source code during this run; your only job is exhaustive documentation.
```

## 3. Deep-Dive Bug Hunting (The "Ghost in the Machine")
*Use this when you have a complex, silent bug or a race condition that standard linters can't find.*

```text
We have a critical bug in the [COMPONENT NAME]. [DESCRIBE THE SYMPTOM, e.g., "The database occasionally deadlocks under high load"].
Do NOT attempt to write a fix immediately. 
1. Use the `error-investigator` and `researcher` agents to trace the data flow.
2. Write a highly detailed hypothesis to a file called 'BUG_REPORT.md'.
3. Once the hypothesis is written, write a failing test case that mathematically reproduces the bug.
4. Only once the test fails, write the fix to turn the test green.
```

## 4. Massive Framework Migration
*Use this when upgrading major versions of a framework where breaking changes are guaranteed.*

```text
We need to migrate this project from [OLD VERSION] to [NEW VERSION].
Before touching any code:
1. Load the `migration-planner` agent.
2. Use the `web_search` tool to find the official breaking changes documentation for [NEW VERSION].
3. Map out a step-by-step migration plan in `AGENT_PLAN.md`.
4. Execute the migration one file at a time, running the test suite after every single file modification. If a test breaks, you must fix it before moving to the next file.
```

## 5. The Security & Vulnerability Audit
*Use this to trigger the offensive security capabilities of the Swarm.*

```text
Perform a strict, Zero-Trust security audit on the `[DIRECTORY NAME]` directory.
1. Load the `security-researcher` agent to statically analyze the code for OWASP Top 10 vulnerabilities (especially Injection and IDOR).
2. If vulnerabilities are found, load the `pentester` agent and instruct it to write a safe, local Python Proof-of-Concept (PoC) script to exploit them.
3. Write your findings to a 'SECURITY_AUDIT.md' report.
4. Finally, patch the vulnerabilities in the source code.
```

## 6. Procedural Memory Seeding (Manual Injection)
*Use this to explicitly force a new "Lesson Learned" into the ChromaDB Hive Mind without having to run a full coding loop.*

```text
I want to permanently add a new architectural rule to your Vector DB memory.
Please load the `critical-reviewer` agent.
Use your tools to write the following lesson into the `.hive_memory/` database: 
"When writing Dockerfiles for our production environment, ALWAYS use Alpine Linux base images and NEVER run the container as the root user."
Verify the lesson was stored successfully.
```