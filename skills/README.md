# Claude Code Skills

Skills provide specialized capabilities that Claude discovers through natural language. No slash commands needed - just describe what you want.

## How Skills Work

1. **Natural Language Discovery**: Describe your task and Claude matches it to relevant skills
2. **Progressive Loading**: Only loads detailed resources when needed (saves tokens)
3. **Bundled Scripts**: Skills can include executable Python/Bash utilities

## Available Skills

| Skill | Description | Triggers |
|-------|-------------|----------|
| [documentation-pipeline](documentation-pipeline/SKILL.md) | Generate software lifecycle docs (63 documents, 10 phases) | "create docs", "generate requirements", "write architecture" |
| [rust-guidelines](rust-guidelines/SKILL.md) | Enforce Microsoft's Pragmatic Rust Guidelines with automated validation | "implement Rust", "review Rust code", "write Rust library", "FFI safety" |

## Usage Examples

### Documentation Pipeline

**Basic usage:**
```
"Create documentation for MyProject"
"Generate requirements for the payment feature"
"Write architecture docs"
```

**Tier selection:**
```
"Create essential documentation for MyProject"      # 2 docs (requirements + architecture)
"Create standard documentation for MyProject"       # 4 docs (+ system design, implementation plan)
"Create comprehensive documentation for MyProject"  # 63 docs (all 10 phases)
```

**Phase-specific:**
```
"Generate Phase 1 requirements documentation"
"Create Phase 2 architecture documentation"
"Run Phase 5 release documentation"
```

**Direct script usage:**
```bash
# Initialize .docs/ folder structure
python ~/.claude/skills/documentation-pipeline/scripts/init-docs-structure.py essential MyProject

# Validate document quality (score 1-10)
python ~/.claude/skills/documentation-pipeline/scripts/validation-scorer.py .docs/requirements/REQUIREMENTS.md requirements

# Check phase gate prerequisites
bash ~/.claude/skills/documentation-pipeline/scripts/phase-gate-checker.sh 2
```

### Rust Guidelines

**Basic usage:**
```
"Implement user authentication in Rust"
"Review this Rust code for guideline compliance"
"Create a library following Microsoft Rust guidelines"
"Check this FFI code for safety issues"
```

**Enforcement modes:**
```
"Implement payment service in Rust with strict guidelines"    # Strict mode (new code)
"Review this Rust code for guideline violations"              # Moderate mode (existing code)
"Explain Rust guidelines for error handling"                  # Advisory mode (learning)
```

**Domain-specific:**
```
"Create a Rust library with proper API design"     # Loads libraries.md
"Implement FFI bindings safely"                    # Loads ffi.md + safety.md
"Optimize this Rust code for performance"          # Loads performance.md
```

**Direct validation:**
```bash
# Strict mode (fails on errors/warnings)
python ~/.claude/skills/rust-guidelines/scripts/guideline-checker.py --strict src/

# Moderate mode (fails on critical only)
python ~/.claude/skills/rust-guidelines/scripts/guideline-checker.py --moderate src/

# Advisory mode (report only, never fails)
python ~/.claude/skills/rust-guidelines/scripts/guideline-checker.py --advisory src/
```

**Guideline domains:**
- Universal: Error handling, type safety, memory safety (always loaded)
- Libraries: API design, semver, documentation (library crates)
- FFI: Foreign function safety, repr(C), ownership (C interop)
- Safety: Unsafe code, security, concurrency (security-critical)
- Applications: CLI, error messages (minimal - future expansion)
- Performance: Optimization patterns (minimal - future expansion)
- Documentation: Doc standards (minimal - future expansion)
- AI Integration: ML patterns (minimal - future expansion)

## Skill Structure

```
~/.claude/skills/
├── README.md                      # This file
└── <skill-name>/
    ├── SKILL.md                   # Required: YAML frontmatter + main content
    ├── resources/                 # Optional: On-demand loaded files
    │   └── *.md
    └── scripts/                   # Optional: Executable utilities
        ├── *.py
        └── *.sh
```

## Creating New Skills

### 1. Create SKILL.md with YAML frontmatter

```markdown
---
name: my-skill
description: |
  Brief description of what this skill does.
  Use for: specific use cases, triggers, keywords.
---

# My Skill

Detailed documentation here...
```

### 2. Add resources (optional)

Place detailed reference files in `resources/` subdirectory. These are loaded on-demand to save tokens.

### 3. Add scripts (optional)

Include Python/Bash scripts in `scripts/` subdirectory. Document version requirements:
- Python scripts: Add `Requires: Python 3.x+` in docstring
- Bash scripts: Add `Requires: Bash 4.x+` in header comment

### 4. Add runtime version checks

```python
# Python
import sys
if sys.version_info < (3, 9):
    sys.exit("Error: Python 3.9+ required")
```

```bash
# Bash
if [[ ${BASH_VERSINFO[0]} -lt 4 ]]; then
    echo "Error: Bash 4.0+ required"
    exit 1
fi
```

## Skills vs Commands

| Aspect | Skills | Commands |
|--------|--------|----------|
| Invocation | Natural language | `/command-name` |
| Discovery | Automatic matching | Explicit invocation |
| Token usage | Progressive loading | Full load |
| Best for | Common workflows | Specific operations |

Skills and commands coexist - use whichever fits your workflow.

## Requirements

| Dependency | Version | Notes |
|------------|---------|-------|
| Python | 3.9+ | For scripts using `is_relative_to()`, `list[str]` |
| Bash | 4.0+ | For scripts using associative arrays |
