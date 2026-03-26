# Python Guidelines Skill

Comprehensive Python code quality guidelines with tiered pyproject.toml configurations, domain-specific resources, and verification scripts.

## Using This Skill with Claude Code

### Automatic Activation

This skill **automatically activates** when you ask Claude to work with Python code. Claude will apply these guidelines when:

- Writing new Python code
- Reviewing existing Python code
- Setting up Python projects
- Configuring linting and type checking

### Natural Language Triggers

Simply ask Claude using natural language:

| What You Want | Example Prompts |
|---------------|-----------------|
| **New Project** | "Create a Python project with strict typing" |
| **Code Review** | "Review this Python code for best practices" |
| **Configuration** | "Configure mypy and ruff for this project" |
| **Type Hints** | "Add type hints following strict mypy standards" |
| **Testing** | "Set up pytest with fixtures and markers" |
| **Fix Issues** | "Fix the linting errors in this file" |

### What Claude Applies

When writing Python code, Claude automatically:

1. **Uses modern syntax** - Python 3.14+, `list[str]` not `List[str]`, f-strings, pathlib
2. **Adds type hints** - All functions get proper type annotations
3. **Follows naming conventions** - PEP 8 compliant names
4. **Structures code properly** - Dataclasses, proper imports, no mutable defaults
5. **Writes tests** - pytest with fixtures, proper assertions

### Configuration Options

Tell Claude which tier you want:

```
"Set up a Python project with minimal configuration"     → Scripts/prototypes
"Set up a Python project with standard configuration"   → Legacy migration
"Set up a Python project with strict configuration"     → DEFAULT for most projects
"Set up a Python project with enterprise configuration" → Regulated systems
```

### Verification

After Claude writes code, verify it passes all checks:

```bash
# Quick verification
python ~/.claude/skills/python-guidelines/scripts/verify.py

# Or individual tools
ruff check . && ruff format --check . && mypy . && pytest
```

---

## Quick Start

### 1. Choose Your Configuration Tier

| Tier | Use Case | Tools |
|------|----------|-------|
| **Minimal** | Scripts, prototypes, learning | ruff (E, F, I) |
| **Standard** | Legacy migration | ruff + mypy |
| **Strict** | **DEFAULT - Most projects** | ruff + mypy strict + pytest |
| **Enterprise** | Financial/regulated systems | All rules + security scanning |

### 2. Copy Template to Your Project

```bash
# Copy template (strict is the default)
cp ~/.claude/skills/python-guidelines/templates/strict.toml ./pyproject.toml

# Install dependencies
uv pip install -e ".[dev]"
# OR
pip install -e ".[dev]"
```

### 3. Run Verification

```bash
# Using the verification script
python ~/.claude/skills/python-guidelines/scripts/verify.py

# OR using Makefile (if configured)
make verify
```

## Installation

### Required Tools

```bash
# Install uv (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install tools
uv venv
source .venv/bin/activate
uv pip install ruff mypy pytest pytest-asyncio pytest-cov
```

### Optional Tools (Enterprise)

```bash
# Security scanning
uv pip install bandit pip-audit

# Type stubs for common libraries
uv pip install types-requests types-redis pandas-stubs
```

## How-To Examples

### Example 1: Create a FastAPI Service

```bash
# Setup project
mkdir my-api && cd my-api
cp ~/.claude/skills/python-guidelines/templates/strict.toml ./pyproject.toml
uv venv && source .venv/bin/activate
uv pip install fastapi uvicorn pydantic
uv pip install -e ".[dev]"
mkdir -p src/my_api tests
touch src/my_api/__init__.py src/my_api/py.typed tests/__init__.py
```

```python
# src/my_api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="My API")


class UserCreate(BaseModel):
    """Request model for creating a user."""

    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int
    name: str
    email: str


@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate) -> UserResponse:
    """Create a new user."""
    # In production, save to database
    return UserResponse(id=1, name=user.name, email=user.email)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    """Get user by ID."""
    if user_id != 1:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=1, name="John", email="john@example.com")
```

```python
# tests/test_main.py
import pytest
from fastapi.testclient import TestClient

from my_api.main import app

client = TestClient(app)


class TestCreateUser:
    def test_create_user_success(self):
        response = client.post(
            "/users",
            json={"name": "Alice", "email": "alice@example.com"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Alice"

    def test_create_user_invalid_email(self):
        response = client.post(
            "/users",
            json={"name": "Bob", "email": "invalid"},
        )
        assert response.status_code == 422


class TestGetUser:
    def test_get_user_found(self):
        response = client.get("/users/1")
        assert response.status_code == 200

    def test_get_user_not_found(self):
        response = client.get("/users/999")
        assert response.status_code == 404
```

```bash
# Run verification
python ~/.claude/skills/python-guidelines/scripts/verify.py
```

---

### Example 2: Add Type Hints to Existing Code

**Before (untyped):**
```python
def process_data(items, threshold=0.5):
    results = []
    for item in items:
        if item['score'] > threshold:
            results.append({
                'id': item['id'],
                'passed': True
            })
    return results
```

**After (fully typed):**
```python
from dataclasses import dataclass


@dataclass
class Item:
    """Input item with score."""

    id: str
    score: float


@dataclass
class Result:
    """Processing result."""

    id: str
    passed: bool


def process_data(items: list[Item], threshold: float = 0.5) -> list[Result]:
    """Process items and filter by threshold.

    Args:
        items: List of items to process.
        threshold: Minimum score to pass (default: 0.5).

    Returns:
        List of results for items that passed the threshold.
    """
    return [
        Result(id=item.id, passed=True)
        for item in items
        if item.score > threshold
    ]
```

---

### Example 3: Fix Common Linting Errors

```bash
# See what rules are failing
ruff check . --statistics

# Auto-fix safe issues
ruff check . --fix

# Format code
ruff format .

# Check specific rules
ruff check . --select=UP  # pyupgrade only
```

**Common fixes:**

```python
# UP006: Use list instead of List
# Before
from typing import List, Dict
def get_items() -> List[str]: ...

# After
def get_items() -> list[str]: ...

# SIM102: Nested if → single if with and
# Before
if x:
    if y:
        do_something()

# After
if x and y:
    do_something()

# PTH123: Use pathlib instead of open()
# Before
with open("file.txt") as f:
    data = f.read()

# After
from pathlib import Path
data = Path("file.txt").read_text()

# B008: Don't use mutable default (except FastAPI Depends)
# Before
def func(items: list = []):  # Bug!
    items.append(1)

# After
def func(items: list | None = None):
    if items is None:
        items = []
    items.append(1)
```

---

### Example 4: Data Processing Script

```python
#!/usr/bin/env python3
"""Process CSV data with proper typing and error handling."""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """Financial transaction record."""

    id: str
    amount: Decimal
    category: str


def load_transactions(filepath: Path) -> list[Transaction]:
    """Load transactions from CSV file.

    Args:
        filepath: Path to CSV file.

    Returns:
        List of parsed transactions.

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If CSV format is invalid.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    transactions: list[Transaction] = []
    lines = filepath.read_text().strip().split("\n")

    for i, line in enumerate(lines[1:], start=2):  # Skip header
        try:
            parts = line.split(",")
            if len(parts) != 3:
                raise ValueError(f"Expected 3 columns, got {len(parts)}")

            transactions.append(
                Transaction(
                    id=parts[0],
                    amount=Decimal(parts[1]),
                    category=parts[2],
                )
            )
        except (ValueError, IndexError) as e:
            logger.warning("Skipping invalid row %d: %s", i, e)

    logger.info("Loaded %d transactions", len(transactions))
    return transactions


def calculate_totals(transactions: list[Transaction]) -> dict[str, Decimal]:
    """Calculate totals by category.

    Args:
        transactions: List of transactions.

    Returns:
        Dictionary mapping category to total amount.
    """
    totals: dict[str, Decimal] = {}
    for txn in transactions:
        totals[txn.category] = totals.get(txn.category, Decimal(0)) + txn.amount
    return totals


def main() -> None:
    """Main entry point."""
    filepath = Path("transactions.csv")
    transactions = load_transactions(filepath)
    totals = calculate_totals(transactions)

    for category, total in sorted(totals.items()):
        logger.info("%s: $%s", category, total)


if __name__ == "__main__":
    main()
```

---

## Configuration Tiers

### Minimal (`templates/minimal.toml`)

For quick scripts and prototypes:

```toml
[tool.ruff.lint]
select = ["E", "F", "I"]  # Errors, Pyflakes, isort only
```

**When to use:**
- Learning Python
- One-off scripts
- Quick prototypes
- Personal utilities

### Standard (`templates/standard.toml`)

For legacy codebases or gradual migration:

```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "C4", "UP", "SIM", "N", "RUF"]

[tool.mypy]
strict = true
warn_return_any = true
```

**When to use:**
- Legacy codebase migration
- Projects with existing non-strict patterns
- Gradual adoption path

### Strict (`templates/strict.toml`) - **DEFAULT**

Recommended for all new projects:

```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "C4", "UP", "SIM", "N", "RUF",
          "PERF", "PL", "PTH", "T20", "TRY", "PIE", "RSE", "RET",
          "FLY", "FURB", "LOG", "G"]

[tool.mypy]
strict = true
```

**When to use:**
- **All new projects (DEFAULT)**
- Production services
- Team projects
- APIs and services
- Shared libraries

### Enterprise (`templates/enterprise.toml`)

Maximum compliance for regulated environments:

```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "C4", "UP", "SIM", "N", "RUF",
          "PERF", "PTH", "T20", "PL", "TRY", "S", "ANN"]

[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]

[tool.bandit]
exclude_dirs = ["tests"]
```

**When to use:**
- Financial systems
- Healthcare applications
- Regulated industries
- Security-critical code

## Resources

### Domain-Specific Guides

| Resource | Topics |
|----------|--------|
| `resources/universal.md` | Type hints, naming, imports, error handling, logging |
| `resources/testing.md` | pytest fixtures, parametrize, mocking, coverage |
| `resources/web.md` | FastAPI, Pydantic, httpx, middleware |
| `resources/packaging.md` | pyproject.toml, uv, versioning, publishing |

### Quick Reference

```python
# Modern type hints (Python 3.14+)
def process(data: str | None) -> dict[str, int]: ...

# Generic collections
items: list[str] = []
mapping: dict[str, int] = {}

# Pydantic models
class UserRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
```

## Common Workflows

### New Project Setup

```bash
# 1. Create project structure
mkdir my-project && cd my-project
uv init

# 2. Copy configuration (strict is the default)
cp ~/.claude/skills/python-guidelines/templates/strict.toml ./pyproject.toml

# 3. Edit project metadata
# Update [project] section with your project name, version, etc.

# 4. Install dependencies
uv pip install -e ".[dev]"

# 5. Create source directory
mkdir -p src/my_project tests
touch src/my_project/__init__.py src/my_project/py.typed
```

### Adding to Existing Project

```bash
# 1. Backup existing config
cp pyproject.toml pyproject.toml.backup

# 2. Merge tool configurations
# Copy [tool.ruff], [tool.mypy], [tool.pytest] sections from template

# 3. Install missing tools
uv pip install ruff mypy pytest

# 4. Run initial check (expect errors)
ruff check . --statistics

# 5. Auto-fix safe issues
ruff check . --fix
ruff format .

# 6. Address remaining issues incrementally
```

### Pre-Commit Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]
```

### CI/CD Integration

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv pip install -e ".[dev]"
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy .
      - run: pytest -v --cov
```

### Makefile Integration

```makefile
.PHONY: verify lint format typecheck test

verify: lint format typecheck test
	@echo "All checks passed!"

lint:
	ruff check .

format:
	ruff format --check .

typecheck:
	mypy .

test:
	pytest -v

fix:
	ruff check . --fix
	ruff format .
```

## Customization

### Adding Per-File Ignores

```toml
[tool.ruff.lint.per-file-ignores]
# Tests can use assert and don't need annotations
"tests/**/*.py" = ["S101", "ANN"]

# Migrations have auto-generated code
"alembic/**/*.py" = ["E501", "UP"]

# Scripts can use print
"scripts/**/*.py" = ["T20"]
```

### Adding Custom Markers (pytest)

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "integration: requires external services",
    "e2e: end-to-end tests",
]
```

### Relaxing mypy for Specific Modules

```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
strict = false

[[tool.mypy.overrides]]
module = ["redis.*", "celery.*"]
ignore_missing_imports = true
```

## Ruff Rules Quick Reference

| Code | Category | Description |
|------|----------|-------------|
| E | pycodestyle | Style errors |
| F | Pyflakes | Logic errors |
| I | isort | Import sorting |
| B | flake8-bugbear | Common bugs |
| C4 | flake8-comprehensions | Better comprehensions |
| UP | pyupgrade | Modern syntax |
| SIM | flake8-simplify | Simplifications |
| N | pep8-naming | Naming conventions |
| PERF | Perflint | Performance |
| PTH | flake8-use-pathlib | Use pathlib |
| T20 | flake8-print | No print() |
| S | flake8-bandit | Security |
| ANN | flake8-annotations | Type annotations |
| PL | Pylint | Various checks |

## Troubleshooting

### "Module has no attribute" errors

```bash
# Install type stubs
uv pip install types-requests types-redis

# Or ignore in mypy config
[[tool.mypy.overrides]]
module = "problematic_library.*"
ignore_missing_imports = true
```

### Ruff conflicts with existing formatter

```toml
# Disable conflicting rules if using black
[tool.ruff.lint]
extend-ignore = ["E501"]  # Line length handled by formatter
```

### Too many errors on first run

```bash
# Start with fewer rules
ruff check . --select=E,F

# Fix incrementally
ruff check . --select=E,F --fix

# Add more rules over time
ruff check . --select=E,F,I,UP --fix
```

## File Structure

```
skills/python-guidelines/
├── SKILL.md              # Main skill file (Claude reads this)
├── README.md             # This documentation
├── templates/
│   ├── minimal.toml      # Scripts/prototypes
│   ├── standard.toml     # Legacy migration
│   ├── strict.toml       # DEFAULT - Most projects
│   └── enterprise.toml   # Regulated systems
├── resources/
│   ├── universal.md      # Core Python patterns
│   ├── testing.md        # pytest patterns
│   ├── web.md            # FastAPI/web patterns
│   └── packaging.md      # pyproject/uv patterns
└── scripts/
    └── verify.py         # Verification script
```

## Version History

- **1.1.0** (2026-01): Python 3.14, strict as default
- **1.0.0** (2025-01): Initial release with 4 tiers, 4 resources
