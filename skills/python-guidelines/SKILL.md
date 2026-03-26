---
name: python-guidelines
description: |
  Enforce modern Python best practices with type safety, linting, and testing standards.
  Uses Ruff (replaces black+isort+flake8), mypy --strict, and pytest.
  Use for: writing Python code, reviewing code, ensuring type safety, configuring projects.
---

# Python Development Guidelines

Automatically enforces modern Python best practices when creating or modifying Python code.

## Quick Start

**Natural language triggers:**
- "Create a Python project with strict typing"
- "Review this Python code for best practices"
- "Configure mypy and ruff for this project"
- "Add type hints following strict mypy standards"
- "Set up pytest with fixtures and markers"

## Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.14+ | Runtime (3.14 required) |
| Ruff | 0.8+ | Linting + Formatting (replaces black, isort, flake8) |
| mypy | 1.13+ | Static type checking |
| pytest | 8.0+ | Testing framework |
| uv | 0.5+ | Package management (recommended) |

## Tool Stack (2025)

### Ruff - All-in-One Linter & Formatter
Ruff replaces: black, isort, flake8, pyupgrade, autoflake, pydocstyle, and 800+ rules.

**Why Ruff:**
- 10-100x faster than alternatives (written in Rust)
- Single tool for lint + format
- Used by: FastAPI, pandas, Pydantic, Apache Airflow

**Ruff does NOT replace mypy** - still need type checking separately.

### mypy - Static Type Checker
Use `strict = true` for all new projects. This enables:
- `disallow_untyped_defs` - All functions must have type hints
- `warn_return_any` - Catch accidental Any returns
- `disallow_any_generics` - No implicit Any in generics
- `strict_equality` - Type-safe comparisons

### pytest - Testing Framework
Modern pytest with:
- `asyncio_mode = "auto"` - Automatic async test detection
- `--strict-markers` - Prevent typos in markers
- Fixtures with proper scoping (function, class, module, session)

## Guideline Domains

| Domain | Resource | When to Load | Status |
|--------|----------|--------------|--------|
| Universal | [universal.md](resources/universal.md) | All Python code | Complete |
| Web/API | [web.md](resources/web.md) | FastAPI, Flask, async APIs | Complete |
| Testing | [testing.md](resources/testing.md) | pytest patterns, fixtures | Complete |
| Data Science | data-science.md | pandas, numpy, sklearn | Planned *(coming soon)* |
| ML/AI | ml-ai.md | PyTorch, transformers | Planned *(coming soon)* |
| CLI | cli.md | Click, argparse, rich | Planned *(coming soon)* |
| Async | async.md | asyncio, aiohttp patterns | Planned *(coming soon)* |
| Packaging | [packaging.md](resources/packaging.md) | pyproject.toml, uv | Complete |

## Configuration Tiers

### Minimal (Quick Start)
```toml
[tool.ruff]
line-length = 88
[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.mypy]
strict = true
ignore_missing_imports = true
```

### Standard (Legacy/Migration)
```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "C4", "UP", "SIM", "N", "RUF"]

[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]
```

### Strict (DEFAULT - Most Projects)
```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "C4", "UP", "SIM", "N", "RUF",
          "PERF", "PL", "PTH", "T20", "TRY", "PIE", "RSE", "RET",
          "FLY", "FURB", "LOG", "G"]

[tool.mypy]
strict = true
warn_unused_ignores = true
show_error_codes = true
```

### Enterprise (Full Compliance)
See [templates/enterprise.toml](templates/enterprise.toml) for complete configuration.

## Ruff Rule Reference

| Code | Name | Purpose | Tier |
|------|------|---------|------|
| E | pycodestyle errors | Style violations | Minimal |
| F | Pyflakes | Undefined names, unused imports | Minimal |
| I | isort | Import sorting | Minimal |
| W | pycodestyle warnings | Additional style checks | Standard |
| B | flake8-bugbear | Common bug patterns | Standard |
| C4 | flake8-comprehensions | Better list/dict comprehensions | Standard |
| UP | pyupgrade | Modern Python syntax | Standard |
| SIM | flake8-simplify | Simplify code patterns | Standard |
| N | pep8-naming | Naming conventions | Standard |
| RUF | Ruff-specific | Additional quality rules | Standard |
| PERF | Performance | Anti-patterns affecting speed | Strict |
| PL | Pylint | Comprehensive code analysis | Strict |
| PTH | pathlib | Use pathlib instead of os.path | Strict |
| T20 | flake8-print | No print() in production | Strict |
| TRY | tryceratops | Exception handling patterns | Strict |
| S | flake8-bandit | Security vulnerabilities | Enterprise |
| ANN | flake8-annotations | Type annotation coverage | Enterprise |

## Common mypy Overrides

### Tests (Relaxed)
```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false
```

### Third-Party Without Stubs
```toml
[[tool.mypy.overrides]]
module = ["redis.*", "httpx.*", "uvicorn.*"]
ignore_missing_imports = true
```

### FastAPI Dependencies
```toml
[tool.ruff.lint.per-file-ignores]
"app/api/**/*.py" = ["B008"]  # Allow Depends() in defaults
```

## Enforcement Modes

### Strict Mode (New Code)
- All violations reported
- mypy --strict enforced
- No print() statements (T20)
- Load: All applicable domain resources

### Advisory Mode (Code Review)
- Violations reported with severity
- Non-blocking recommendations
- Load: Targeted domain resources

### Incremental Mode (Migration)
- Focus on modified code only
- Gradually enable strict rules
- Load: Relevant patterns only

## Verification

```bash
# Full verification (recommended)
make verify  # or: ruff check . && ruff format --check . && mypy . && pytest

# Individual tools
ruff check .           # Lint
ruff format --check .  # Format check
mypy .                 # Type check
pytest -v              # Tests
```

## Integration

Works standalone or composed with domain-specific skills:
- `python-guidelines` + `fastapi` → Type-safe API development
- `python-guidelines` + `data-science` → Typed pandas/numpy code
- `python-guidelines` + `ml-ai` → PyTorch with type hints

## Version

Based on: **Python Best Practices 2025**
- Ruff documentation: https://docs.astral.sh/ruff/
- mypy documentation: https://mypy.readthedocs.io/
- pytest documentation: https://docs.pytest.org/
- Last updated: 2026-01-05
