---
name: documentation-pipeline
description: |
  Generate comprehensive software lifecycle documentation across 10 phases (63 documents).
  Creates requirements, architecture, API specs, deployment guides, runbooks, and support docs.
  Supports three tiers: Essential (3 docs), Standard (4 docs - DEFAULT), Comprehensive (63 docs).
  DEFAULT BEHAVIOR: Standard tier (REQUIREMENTS.md, ARCHITECTURE.md, SYSTEM_DESIGN.md, IMPLEMENTATION_PLAN.md)
  unless user explicitly requests "essential" or "comprehensive" tier.
  Use for: creating project docs, writing requirements, architecture design, test strategies,
  deployment checklists, incident response procedures, technical debt tracking.
---

# Documentation Pipeline Skill

Generate comprehensive software documentation following the Software Factory Lifecycle methodology.

## Quick Start

**Natural language triggers:**
- "Create documentation for [project]"
- "Generate requirements for [feature]"
- "Write architecture docs"
- "Create deployment runbook"
- "Generate incident response procedures"

## Requirements

| Dependency | Version | Used By |
|------------|---------|---------|
| Python | 3.9+ | validation-scorer.py, init-docs-structure.py |
| Bash | 4.0+ | phase-gate-checker.sh (associative arrays) |

## Available Tiers

| Tier | Documents | Use Case |
|------|-----------|----------|
| Essential | REQUIREMENTS.md + ARCHITECTURE.md + IMPLEMENTATION_PLAN.md | Simple projects, POCs |
| **Standard (DEFAULT)** | + SYSTEM_DESIGN.md | **Most projects** |
| Comprehensive | All 63 documents across 10 phases | Enterprise, regulated systems |

**Default Behavior:** When tier is not explicitly specified, Standard tier is used.

## The 10 Lifecycle Phases

| Phase | Name | Documents | Resource |
|-------|------|-----------|----------|
| 0 | Conception | 5 docs | [phase-0-conception.md](resources/phase-0-conception.md) |
| 1 | Requirements | 7 docs | [phase-1-requirements.md](resources/phase-1-requirements.md) |
| 2 | Design | 8 docs | [phase-2-architecture.md](resources/phase-2-architecture.md) |
| 3 | Build | 5 docs | [phase-3-build.md](resources/phase-3-build.md) |
| 4 | Validate | 7 docs | [phase-4-validate.md](resources/phase-4-validate.md) |
| 5 | Release | 7 docs | [phase-5-release.md](resources/phase-5-release.md) |
| 6 | Operate | 5 docs | [phase-6-operations.md](resources/phase-6-operations.md) |
| 7 | Support | 7 docs | [phase-7-support.md](resources/phase-7-support.md) |
| 8 | Maintain | 7 docs | [phase-8-evolution.md](resources/phase-8-evolution.md) |
| 9 | Retire | 5 docs | [phase-9-retire.md](resources/phase-9-retire.md) |

## Output Structure

All documents are created in `.docs/` directory (gitignored):

```
.docs/
├── conception/        # Phase 0
├── requirements/      # Phase 1
├── architecture/      # Phase 2
├── api/              # API specs
├── ui/               # UI design
├── planning/         # Phase 3 (Build preparation)
├── testing/          # Phase 4
├── reviews/          # Phase 4
├── release/          # Phase 5
├── operations/       # Phase 6
├── support/          # Phase 7
├── maintenance/      # Phase 8
└── retirement/       # Phase 9
```

## Bundled Scripts

### Initialize Documentation Structure
```bash
# Run: python scripts/init-docs-structure.py [tier] [project_name]
python scripts/init-docs-structure.py standard MyProject
```

### Validate Document Quality
```bash
# Run: python scripts/validation-scorer.py [doc_path] [doc_type]
python scripts/validation-scorer.py .docs/requirements/REQUIREMENTS.md requirements
```

### Check Phase Gate Prerequisites
```bash
# Run: bash scripts/phase-gate-checker.sh [phase_number]
bash scripts/phase-gate-checker.sh 2
```

## Agent Assignments

Each document type has specialized creation and validation agents:

### Phase 1-2 (Requirements & Architecture)
- **Creation:** requirements-analyst, requirements-documentation-engineer, architect, solution-architect, software-design-architect
- **Validation:** requirements-validator, architect-critic, architecture-reviewer

### Phase 3-4 (Build & Validate)
- **Creation:** developer, standards-enforcer, tester
- **Validation:** critical-reviewer, test-coverage-validator

### Phase 5-7 (Release, Operate, Support)
- **Creation:** devops-automation-engineer, sre-reliability-engineer
- **Validation:** critical-reviewer, sre-reliability-engineer

### Phase 8-9 (Maintain & Retire)
- **Creation:** migration-planner, stakeholder-elicitor
- **Validation:** architecture-reviewer, critical-reviewer

## Canonical Validator Assignments (SOURCE OF TRUTH)

**CRITICAL: This table is authoritative. All other files MUST reference this.**

| Phase | Document | Validators (ALL must return score ≥ 9) | Invocation |
|-------|----------|----------------------------------------|------------|
| 1 | REQUIREMENTS.md | requirements-validator | `Task(subagent_type="requirements-validator")` |
| 1 | USER_STORIES.md | requirements-validator | `Task(subagent_type="requirements-validator")` |
| 1 | METRICS_INVENTORY.md | requirements-validator | `Task(subagent_type="requirements-validator")` |
| 2 | ARCHITECTURE.md | architect-critic + architecture-reviewer | Both required |
| 2 | SYSTEM_DESIGN.md | critical-reviewer + architecture-reviewer | Both required |
| 2 | DATA_MODEL.md | architecture-reviewer | `Task(subagent_type="architecture-reviewer")` |
| 2 | SECURITY_DESIGN.md | security-reviewer | `Task(subagent_type="security-reviewer")` |
| 2 | ADR-xxx.md | architect-critic | `Task(subagent_type="architect-critic")` |
| 3 | IMPLEMENTATION_PLAN.md | Multi-gate (7 validators across 3 gates): requirements-validator, architecture-reviewer, standards-enforcer, critical-reviewer, test-coverage-validator, architect-critic, tester | All 7 required (≥9) |
| 3 | CODING_STANDARDS.md | critical-reviewer | `Task(subagent_type="critical-reviewer")` |
| 3 | BUILD_GUIDE.md | standards-enforcer | `Task(subagent_type="standards-enforcer")` |
| 3 | CI_CD_PIPELINE.md | critical-reviewer | `Task(subagent_type="critical-reviewer")` |

**For documents requiring multiple validators:** BOTH must return score ≥ 9 before proceeding.

## Validation Loop Pattern

Each major document goes through validation until approved:

```
1. Agent creates document draft
2. Validator reviews (score 1-10)
3. If score < 9: Provide feedback, loop to step 1
4. If score >= 9: APPROVED, proceed to next document
5. Max 3 iterations before escalation
```

## MANDATORY: Execution Workflow

**🚨 CRITICAL: Claude MUST execute this workflow using Task() tool calls. NO EXCEPTIONS.**

### Standard Tier Execution (DEFAULT)

**Phase 1: Requirements (ALWAYS FIRST)**
```
1. Task(subagent_type="requirements-analyst", prompt="Analyze requirements for [project]")
2. Task(subagent_type="requirements-documentation-engineer", prompt="Create REQUIREMENTS.md for [project]")
3. VALIDATION LOOP (MANDATORY):
   a. Task(subagent_type="requirements-validator", prompt="Validate REQUIREMENTS.md, score 1-10")
   b. IF score < 9: Refine REQUIREMENTS.md, goto step 3a
   c. IF score ≥ 9: Mark APPROVED, proceed to Phase 2
   d. Max 3 iterations, escalate if not approved
```

**Phase 2: Architecture (REQUIRES Phase 1 APPROVED)**
```
ARCHITECTURE.md:
  1. Task(subagent_type="architect", prompt="Create ARCHITECTURE.md for [project]")
  2. VALIDATION LOOP (MANDATORY - BOTH validators required):
     a. Task(subagent_type="architect-critic", prompt="Review ARCHITECTURE.md, score 1-10")
     b. Task(subagent_type="architecture-reviewer", prompt="Review ARCHITECTURE.md, score 1-10")
     c. IF either score < 9: Refine document, goto step 2a
     d. IF both scores ≥ 9: Mark APPROVED, proceed to SYSTEM_DESIGN.md
     e. Max 3 iterations, escalate if not approved

SYSTEM_DESIGN.md:
  1. Task(subagent_type="software-design-architect", prompt="Create SYSTEM_DESIGN.md for [project]")
  2. VALIDATION LOOP (MANDATORY - BOTH validators required):
     a. Task(subagent_type="critical-reviewer", prompt="Review SYSTEM_DESIGN.md, score 1-10")
     b. Task(subagent_type="architecture-reviewer", prompt="Review SYSTEM_DESIGN.md, score 1-10")
     c. IF either score < 9: Refine document, goto step 2a
     d. IF both scores ≥ 9: Mark APPROVED, proceed to Phase 3
     e. Max 3 iterations, escalate if not approved
```

**Phase 3: Build (REQUIRES Phase 2 APPROVED)**
```
1. Create .docs/planning/ directory
2. Task(subagent_type="developer", prompt="Create IMPLEMENTATION_PLAN.md for [project]")
3. VALIDATION LOOP (MANDATORY - BOTH validators required):
   a. Task(subagent_type="critical-reviewer", prompt="Review IMPLEMENTATION_PLAN.md, score 1-10")
   b. Task(subagent_type="test-coverage-validator", prompt="Validate test coverage in plan, score 1-10")
   c. IF either score < 9: Refine document, goto step 3a
   d. IF both scores ≥ 9: Mark APPROVED, Standard tier COMPLETE
   e. Max 3 iterations, escalate if not approved
```

### Essential Tier Execution

Execute Phase 1-2 (create REQUIREMENTS.md and ARCHITECTURE.md), then create IMPLEMENTATION_PLAN.md from Phase 3.
Skip SYSTEM_DESIGN.md (Standard tier adds this). Essential tier = 3 documents total.

### Comprehensive Tier Execution

Execute all 10 phases sequentially, each with validation loops as specified in phase resources.

### Enforcement Rules

**❌ BLOCKING ERRORS - Cannot proceed if:**
1. Validation loop not executed for a document
2. Validator returns score < 9 after 3 iterations
3. Phase gate check fails (missing prerequisites)
4. Task() tool not used for agent invocations

**✅ REQUIRED for APPROVED status:**
1. All validators return score ≥ 9
2. Reasoning provided for selection decisions
3. Phase gate prerequisites verified
4. Documents stored in correct .docs/ subdirectories

**🔍 VERIFICATION - Claude must confirm:**
1. "Task(subagent_type='[validator]', ...) executed" for each document
2. "Validator returned score: X/10" for each validation
3. "APPROVED - proceeding to next phase" before moving forward

## Phase Gate Enforcement

**CRITICAL: Phases MUST be executed sequentially. Skipping phases is NOT allowed.**

### Phase Execution Rules

1. **Phase 1 (Requirements)** - ALWAYS FIRST
   - Creates: REQUIREMENTS.md (Essential+)
   - Gate: requirements-validator MUST approve (score ≥ 9)
   - BLOCKS: Cannot proceed to Phase 2 without approved REQUIREMENTS.md

2. **Phase 2 (Architecture)** - REQUIRES Phase 1 complete
   - Creates: ARCHITECTURE.md (Essential+), SYSTEM_DESIGN.md (Standard+), + 6 others (Comprehensive)
   - Gate: architect-critic AND architecture-reviewer MUST approve
   - BLOCKS: Cannot proceed to Phase 3 without approved architecture docs

3. **Phase 3 (Build)** - REQUIRES Phase 2 complete
   - Creates: IMPLEMENTATION_PLAN.md (Standard+), + 4 others (Comprehensive)
   - Location: .docs/planning/ directory MUST be created
   - Gate: critical-reviewer MUST approve implementation plan
   - BLOCKS: Cannot proceed to Phase 4 without build documentation

4. **Subsequent Phases** - Sequential execution enforced
   - Each phase checks prerequisites using phase-gate-checker.sh
   - Missing documents from previous phases = BLOCKING ERROR
   - Agent MUST complete current phase before starting next

### Validation

Use bundled script to verify phase prerequisites:
```bash
# Check if prerequisites for Phase 3 are met
bash scripts/phase-gate-checker.sh 3
# Exit code 0 = pass, 1 = fail (missing prerequisites)
```

### Common Violations to Prevent

❌ Creating only REQUIREMENTS.md + ARCHITECTURE.md for Essential tier (MISSING IMPLEMENTATION_PLAN.md)
❌ Creating only REQUIREMENTS.md + ARCHITECTURE.md for Standard tier (MISSING SYSTEM_DESIGN.md, IMPLEMENTATION_PLAN.md)
❌ Skipping Phase 3 entirely (no .docs/planning/ directory)
❌ Creating code structure instead of documentation (src/, tests/ are NOT part of documentation-pipeline)
❌ Proceeding to next phase without validation approval

## Usage Examples

### Essential Tier (Quick Start)
```
"Create essential documentation for PaymentService with OAuth2 authentication and PostgreSQL storage"
```

### Standard Tier (Most Projects)
```
"Generate standard tier docs for UserAuthService including:
- OAuth2 + JWT authentication
- PostgreSQL user store
- Redis session cache
- REST API"
```

### Comprehensive Tier (Enterprise)
```
"Create comprehensive documentation for TradingPlatform following all 10 phases"
```

### Single Phase
```
"Generate Phase 2 (Design) documentation for NotificationService"
```

## Integration with Commands

This skill complements existing commands (not deprecated):
- `/doc-lifecycle` - Full lifecycle orchestration
- `/doc-phase-X-*` - Individual phase execution

## References

- **Agent Definitions:** `~/.claude/agents/documentation.md`
- **Phase Commands:** `~/.claude/commands/doc-phase-*.md`
- **Lifecycle Orchestrator:** `~/.claude/commands/doc-lifecycle.md`
