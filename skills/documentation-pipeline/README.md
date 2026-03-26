# Documentation Pipeline Skill

Generate comprehensive software lifecycle documentation following the Software Factory Lifecycle methodology.

## Overview

This skill provides automated generation of **63 documents** across **10 lifecycle phases**, from conception to retirement. Choose from three tiers based on your project needs:

| Tier | Documents | Use Case |
|------|-----------|----------|
| **Essential** | 3 | POCs, simple projects |
| **Standard (DEFAULT)** | 4 | **Most projects** |
| **Comprehensive** | 63 | Enterprise, regulated systems |

**Default Behavior:** When tier is not explicitly specified, Standard tier is used (REQUIREMENTS.md, ARCHITECTURE.md, SYSTEM_DESIGN.md, IMPLEMENTATION_PLAN.md).

## Quick Start

Just describe what documentation you need:

```
"Create documentation for MyProject"
"Generate requirements for the payment feature"
"Write architecture docs for the API"
"Create Phase 5 release documentation"
```

Claude automatically loads the relevant phases and generates documents.

## The 10 Lifecycle Phases

| Phase | Name | Documents | Key Outputs |
|-------|------|-----------|-------------|
| 0 | Conception | 5 | Business case, charter, stakeholder analysis |
| 1 | Requirements | 7 | SRS, user stories, acceptance criteria |
| 2 | Design | 8 | Architecture, system design, data model |
| 3 | Build | 5 | Implementation plan, coding standards, CI/CD |
| 4 | Validate | 7 | Test strategy, test plans, code review |
| 5 | Release | 7 | Deployment guide, release notes, rollback plan |
| 6 | Operate | 5 | Monitoring, alerts, SLAs, runbooks |
| 7 | Support | 7 | Incident response, support guides, postmortems |
| 8 | Maintain | 7 | Technical debt, improvement backlog, refactoring |
| 9 | Retire | 5 | Deprecation, migration, decommissioning |

## File Structure

```
~/.claude/skills/documentation-pipeline/
├── SKILL.md                          # Main skill file (YAML frontmatter + docs)
├── README.md                         # This file
├── resources/                        # Phase-specific resources (loaded on-demand)
│   ├── phase-0-conception.md
│   ├── phase-1-requirements.md
│   ├── phase-2-architecture.md
│   ├── phase-3-build.md
│   ├── phase-4-validate.md
│   ├── phase-5-release.md
│   ├── phase-6-operations.md
│   ├── phase-7-support.md
│   ├── phase-8-evolution.md
│   └── phase-9-retire.md
└── scripts/                          # Executable utilities
    ├── init-docs-structure.py        # Initialize .docs/ folder structure
    ├── validation-scorer.py          # Score document quality (1-10)
    └── phase-gate-checker.sh         # Validate phase prerequisites
```

## Usage Examples

### By Tier

```
"Create essential documentation for MyProject"
→ Generates: REQUIREMENTS.md + ARCHITECTURE.md + IMPLEMENTATION_PLAN.md

"Create standard documentation for PaymentService"
→ Generates: REQUIREMENTS.md, ARCHITECTURE.md, SYSTEM_DESIGN.md, IMPLEMENTATION_PLAN.md

"Create comprehensive documentation for TradingPlatform"
→ Generates: All 63 documents across 10 phases
```

### By Phase

```
"Generate Phase 0 conception documents for our new feature"
→ Generates: Business case, charter, stakeholder analysis, feasibility, estimates

"Create Phase 1 requirements documentation"
→ Generates: SRS, user stories, acceptance criteria, risk analysis, etc.

"Generate Phase 5 release documentation"
→ Generates: Deployment guide, release notes, rollback plan, checklists
```

### Direct Script Usage

#### Initialize Directory Structure

```bash
# Create .docs/ structure for essential tier
python ~/.claude/skills/documentation-pipeline/scripts/init-docs-structure.py essential MyProject

# Create .docs/ structure for standard tier
python ~/.claude/skills/documentation-pipeline/scripts/init-docs-structure.py standard PaymentService

# Create .docs/ structure for comprehensive tier (all 10 phases)
python ~/.claude/skills/documentation-pipeline/scripts/init-docs-structure.py comprehensive TradingPlatform
```

**Output:**
```
.docs/
├── requirements/
├── architecture/
├── api/              # Standard+ tier
├── planning/         # Standard+ tier
├── conception/       # Comprehensive tier only
├── tests/            # Comprehensive tier only
├── release/          # Comprehensive tier only
├── operations/       # Comprehensive tier only
├── support/          # Comprehensive tier only
└── maintenance/      # Comprehensive tier only
```

#### Validate Document Quality

```bash
# Score REQUIREMENTS.md (1-10 scale)
python ~/.claude/skills/documentation-pipeline/scripts/validation-scorer.py \
    .docs/requirements/REQUIREMENTS.md requirements

# Score ARCHITECTURE.md
python ~/.claude/skills/documentation-pipeline/scripts/validation-scorer.py \
    .docs/architecture/ARCHITECTURE.md architecture

# Score test strategy
python ~/.claude/skills/documentation-pipeline/scripts/validation-scorer.py \
    .docs/tests/TESTING_STRATEGY.md test-strategy
```

**Output:**
```
REQUIREMENTS.md Validation Report

Overall Score: 8.5/10 [NEEDS WORK]

Component Scores:
  Completeness:  9/10 [PASS]
  Measurability: 8/10 [PASS]
  Consistency:   9/10 [PASS]
  Traceability:  8/10 [PASS]
  Clarity:       8/10 [PASS]

Issues:
  [!] Missing acceptance criteria for user story US-003
  [!] Requirement REQ-005 lacks measurable success criteria

Suggestions:
  [*] Add quantifiable metrics to performance requirements
  [*] Include traceability matrix linking requirements to test cases
```

#### Check Phase Gate Prerequisites

```bash
# Check if ready for Phase 2 (Architecture)
bash ~/.claude/skills/documentation-pipeline/scripts/phase-gate-checker.sh 2

# Check if ready for Phase 5 (Release)
bash ~/.claude/skills/documentation-pipeline/scripts/phase-gate-checker.sh 5

# Check all phases
bash ~/.claude/skills/documentation-pipeline/scripts/phase-gate-checker.sh all
```

**Output:**
```
=== Phase 2: Design ===

Prerequisites:
  [PASS] .docs/requirements/REQUIREMENTS.md exists
  [PASS] .docs/requirements/REQUIREMENTS.md is IMMUTABLE

[OK] GATE PASSED - Ready to proceed to Phase 2
```

## Output Structure

All documents are created in `.docs/` directory (gitignored by default):

```
.docs/
├── conception/          # Phase 0
│   ├── BUSINESS_CASE.md
│   ├── PROJECT_CHARTER.md
│   └── ...
├── requirements/        # Phase 1
│   ├── REQUIREMENTS.md
│   ├── USER_STORIES.md
│   └── ...
├── architecture/        # Phase 2
│   ├── ARCHITECTURE.md
│   ├── SYSTEM_DESIGN.md
│   └── ...
├── planning/           # Phase 3
├── tests/              # Phase 4
├── release/            # Phase 5
├── operations/         # Phase 6
├── support/            # Phase 7
├── maintenance/        # Phase 8
└── retirement/         # Phase 9
```

## Integration

### With V2 Pipeline

The skill automatically integrates with the V2 Development Pipeline:

- **Phase 1**: Uses `general-purpose` agent to create REQUIREMENTS.md
- **Phase 1.5**: Uses `requirements-validator` in validation loop (score >= 9)
- **Phase 2**: Uses `architect` + `architect-critic` for ARCHITECTURE.md
- **Phase 11**: Uses `requirements-documentation-engineer` for README.md

### With Other Skills

Composes with other skills for complete project setup:

```
"Create comprehensive documentation and Rust guidelines for TradingPlatform"
→ Loads: documentation-pipeline + rust-guidelines
→ Generates: Full documentation with Rust-specific compliance
```

## Validation Loop Pattern

Documents are validated iteratively until they meet quality standards:

1. Agent generates document
2. Validator scores document (1-10)
3. If score < 9: Agent refines document
4. Repeat until score >= 9 (APPROVED)

Example: Phase 1.5 validation loop with requirements-validator.

## 🚨 MANDATORY: Execution Workflow

**CRITICAL: Claude MUST execute validation loops using Task() tool. Skipping validation is a PROTOCOL VIOLATION.**

### Standard Tier Workflow (4 Documents)

**Phase 1: REQUIREMENTS.md**
1. Create document with requirements-documentation-engineer
2. **VALIDATE** with requirements-validator (must return score ≥ 9)
3. Iterate up to 3 times until APPROVED

**Phase 2: ARCHITECTURE.md + SYSTEM_DESIGN.md**

ARCHITECTURE.md:
1. Create with architect
2. **VALIDATE** with architect-critic AND architecture-reviewer (both must return score ≥ 9)
3. Iterate up to 3 times until APPROVED

SYSTEM_DESIGN.md:
1. Create with software-design-architect
2. **VALIDATE** with critical-reviewer AND architecture-reviewer (both must return score ≥ 9)
3. Iterate up to 3 times until APPROVED

**Phase 3: IMPLEMENTATION_PLAN.md**
1. Create .docs/planning/ directory
2. Create document with developer
3. **VALIDATE** with critical-reviewer AND test-coverage-validator (both must return score ≥ 9)
4. Iterate up to 3 times until APPROVED

### Protocol Violations to Prevent

**❌ NEVER DO THIS:**
- Create documents without validation loops
- Skip validator agents and only use validation-scorer.py script
- Proceed to next phase without APPROVED status
- Create only 2 documents for Standard tier (must be 4)
- Skip Phase 3 entirely
- Use wrong validators (e.g., critical-reviewer for Phase 2 documents)

**✅ ALWAYS DO THIS:**
- Use Task(subagent_type="validator", ...) for each document
- Wait for score ≥ 9 before proceeding
- Verify phase gates before starting next phase
- Create ALL 4 documents for Standard tier
- Use correct validators for each phase

### Validation Requirements by Phase

**SOURCE OF TRUTH:** See [SKILL.md - Canonical Validator Assignments](SKILL.md#canonical-validator-assignments-source-of-truth)

**Quick Reference (Standard Tier):**

| Phase | Document | Validators (ALL must return score ≥ 9) |
|-------|----------|------------------------------------------|
| 1 | REQUIREMENTS.md | requirements-validator |
| 2 | ARCHITECTURE.md | architect-critic + architecture-reviewer |
| 2 | SYSTEM_DESIGN.md | critical-reviewer + architecture-reviewer |
| 3 | IMPLEMENTATION_PLAN.md | Multi-gate (7 validators): requirements-validator, architecture-reviewer, standards-enforcer, critical-reviewer, test-coverage-validator, architect-critic, tester |

## Document Lifecycle States

### DRAFT (Phases 1-2)
- ✅ Iterative updates allowed during creation
- Documents can be rewritten until approved
- Ends when validator returns APPROVED

### IMMUTABLE (Phase 4+)
- ❌ No rewrites after approval
- Documents become source-of-truth
- ✅ Only amendments/versions allowed
- Marked with `<!-- IMMUTABLE: SOURCE OF TRUTH -->`

## Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Scripts use `is_relative_to()`, `list[str]` |
| Bash | 4.0+ | Associative arrays in gate checker |

## Validation

All scripts include:
- ✅ Runtime version checks (fail fast if requirements not met)
- ✅ Path validation (security: prevents path traversal)
- ✅ Input sanitization (prevents injection attacks)
- ✅ Proper error handling with clear messages

## Advanced Usage

### Custom Validation Criteria

Edit validation-scorer.py to customize scoring:

```python
CRITERIA_WEIGHTS = {
    'completeness': 0.25,
    'measurability': 0.20,
    'consistency': 0.20,
    'traceability': 0.15,
    'clarity': 0.20,
}
```

### Custom Phase Gates

Edit phase-gate-checker.sh to add custom prerequisites:

```bash
PHASE_PREREQS=(
    [2]=".docs/requirements/REQUIREMENTS.md"
    [3]=".docs/architecture/ARCHITECTURE.md .docs/architecture/SYSTEM_DESIGN.md"
)
```

## Examples

### Startup Documentation

```
"Create essential documentation for our new mobile app startup"
```

**Result:**
- `.docs/requirements/REQUIREMENTS.md` (functional and non-functional requirements)
- `.docs/architecture/ARCHITECTURE.md` (system architecture and components)
- `.docs/planning/IMPLEMENTATION_PLAN.md` (implementation steps and tasks)

### Enterprise System

```
"Create comprehensive documentation for our banking platform"
```

**Result:**
- All 63 documents across 10 phases
- Complete audit trail from conception to retirement
- Full traceability between requirements, architecture, tests, deployment

### Feature Documentation

```
"Generate Phase 1 requirements for the authentication feature"
```

**Result:**
- SRS with detailed requirements
- User stories with acceptance criteria
- Risk analysis
- Requirements traceability matrix

## Troubleshooting

### "Python 3.9+ required" error
**Solution**: Upgrade Python or use `python3.9` explicitly

### "Path must be under .docs/" error
**Cause**: Security check prevents path traversal
**Solution**: Ensure paths are under project directory

### "GATE FAILED" message
**Cause**: Prerequisites for next phase not met
**Solution**: Complete required documents for previous phase first

### "Validation loop was skipped" error
**Cause**: Documents created without running validation agents
**Solution**: MUST use Task(subagent_type="validator") for each document before proceeding
**Prevention**: Follow the MANDATORY Execution Workflow (see above)

### "Score < 9 without iteration" error
**Cause**: Proceeded to next phase despite low validation score
**Solution**: Iterate up to 3 times until validator returns score ≥ 9
**Prevention**: Do NOT skip validation loops - they are MANDATORY

## Phase Gate Enforcement

**CRITICAL: Phases MUST be executed sequentially. Skipping phases is NOT allowed.**

### Sequential Execution Rules

1. **Phase 1 (Requirements)** - ALWAYS FIRST
   - Must create REQUIREMENTS.md before Phase 2
   - Validation score ≥ 9 required to proceed

2. **Phase 2 (Architecture)** - REQUIRES Phase 1
   - Essential: ARCHITECTURE.md
   - Standard: + SYSTEM_DESIGN.md
   - Cannot proceed to Phase 3 without approval

3. **Phase 3 (Build)** - REQUIRES Phase 2
   - Standard: Creates .docs/planning/ directory with IMPLEMENTATION_PLAN.md
   - This phase is MANDATORY for Standard tier (cannot skip!)
   - Cannot proceed without build documentation

### Common Violations to Prevent

❌ **Creating only 2 docs for Standard tier** (should be 4: REQUIREMENTS.md, ARCHITECTURE.md, SYSTEM_DESIGN.md, IMPLEMENTATION_PLAN.md)
❌ **Skipping Phase 3 entirely** (no .docs/planning/ directory created)
❌ **Creating code structure** (src/, tests/ are NOT part of documentation-pipeline scope)
❌ **Proceeding without validation approval** (all docs must score ≥ 9)

### Verification

Check prerequisites before proceeding to next phase:
```bash
bash ~/.claude/skills/documentation-pipeline/scripts/phase-gate-checker.sh 3
# Exit 0 = ready for Phase 3, Exit 1 = missing prerequisites
```

## Contributing

To extend or customize:

1. **Add new phase**: Create `resources/phase-X-newphase.md`
2. **Add document type**: Update validation-scorer.py criteria
3. **Add gate rule**: Update phase-gate-checker.sh PHASE_PREREQS

## Guidelines Version

Based on: **Software Factory Lifecycle Methodology**
- 10-phase comprehensive lifecycle
- Validation loop pattern for quality assurance
- Document protection policy for immutability
- Last updated: 2026-01-03

## See Also

- [SKILL.md](SKILL.md) - Main skill documentation
- [DOCS_PROTECTION_POLICY.md](../../DOCS_PROTECTION_POLICY.md) - Document lifecycle rules
