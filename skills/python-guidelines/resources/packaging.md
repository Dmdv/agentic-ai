# Packaging Guidelines (pyproject.toml & uv)

Modern Python packaging with pyproject.toml and uv package manager.

## pyproject.toml Structure

### Minimal Configuration
```toml
[project]
name = "my-project"
version = "1.0.0"
description = "Project description"
requires-python = ">=3.14"

[project.optional-dependencies]
dev = ["ruff", "mypy", "pytest"]
```

### Full Configuration
```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "1.0.0"
description = "A comprehensive Python project"
readme = "README.md"
requires-python = ">=3.14"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.14",
]
keywords = ["python", "example"]

dependencies = [
    "fastapi>=0.109.0",
    "pydantic>=2.5.0",
    "httpx>=0.26.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=4.1.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.5.0",
]
all = ["my-project[dev,docs]"]

[project.urls]
Homepage = "https://github.com/user/my-project"
Documentation = "https://my-project.readthedocs.io"
Repository = "https://github.com/user/my-project"
Issues = "https://github.com/user/my-project/issues"

[project.scripts]
my-cli = "my_project.cli:main"

[project.entry-points."my_project.plugins"]
plugin1 = "my_project.plugins.plugin1:Plugin1"
```

## Build Systems

### setuptools (Most Common)
```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
include = ["my_project*"]

[tool.setuptools.package-data]
my_project = ["py.typed", "data/*.json"]
```

### Hatchling (Modern Alternative)
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/my_project"]
```

### Poetry (All-in-One)
```toml
[tool.poetry]
name = "my-project"
version = "1.0.0"
description = "Project description"
authors = ["You <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.14"
fastapi = "^0.109.0"

[tool.poetry.group.dev.dependencies]
ruff = "^0.8.0"
mypy = "^1.13.0"
pytest = "^8.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## uv Package Manager

### Installation
```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv

# Or via Homebrew
brew install uv
```

### Basic Commands
```bash
# Create virtual environment
uv venv

# Activate (Unix)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies from pyproject.toml
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Install specific package
uv pip install httpx

# Install from requirements.txt
uv pip install -r requirements.txt

# Upgrade package
uv pip install --upgrade httpx

# Show installed packages
uv pip list

# Generate requirements.txt
uv pip freeze > requirements.txt
```

### uv Project Management
```bash
# Initialize new project
uv init my-project

# Add dependency
uv add httpx

# Add dev dependency
uv add --dev ruff mypy pytest

# Remove dependency
uv remove httpx

# Update all dependencies
uv lock --upgrade

# Sync dependencies (install from lock file)
uv sync

# Run command in project environment
uv run python -m pytest
uv run ruff check .
```

### Lock Files
```bash
# Generate uv.lock from pyproject.toml
uv lock

# Install from lock file (reproducible)
uv sync

# Update specific package in lock
uv lock --upgrade-package httpx
```

## Version Management

### Single Source of Truth
```toml
# pyproject.toml
[project]
name = "my-project"
version = "1.0.0"  # Single source
```

```python
# my_project/__init__.py
__version__ = "1.0.0"  # Keep in sync with pyproject.toml
```

### Dynamic Versioning
```toml
# Using setuptools_scm (version from git tags)
[build-system]
requires = ["setuptools>=68.0", "setuptools_scm>=8.0"]
build-backend = "setuptools.build_meta"

[project]
dynamic = ["version"]

[tool.setuptools_scm]
version_scheme = "guess-next-dev"
local_scheme = "no-local-version"
```

### Semantic Versioning
```
MAJOR.MINOR.PATCH

1.0.0  - Initial release
1.0.1  - Bug fixes only (backward compatible)
1.1.0  - New features (backward compatible)
2.0.0  - Breaking changes
```

## Dependency Specification

### Version Constraints
```toml
dependencies = [
    # Exact version
    "package==1.0.0",

    # Minimum version
    "package>=1.0.0",

    # Compatible release (>=1.0.0, <2.0.0)
    "package~=1.0",

    # Range
    "package>=1.0.0,<2.0.0",

    # Any version
    "package",

    # With extras
    "httpx[http2]>=0.26.0",

    # From URL
    "package @ https://example.com/package.tar.gz",

    # From git
    "package @ git+https://github.com/user/repo.git@v1.0.0",
]
```

### Environment Markers
```toml
dependencies = [
    # Platform-specific
    "pywin32>=300; sys_platform == 'win32'",
    "uvloop>=0.19.0; sys_platform != 'win32'",

    # Python version specific
    "typing_extensions>=4.0; python_version < '3.11'",

    # Implementation specific
    "psyco; implementation_name == 'cpython'",
]
```

## Optional Dependencies

### Organized Groups
```toml
[project.optional-dependencies]
# Development tools
dev = [
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pytest>=8.0.0",
]

# Testing only
test = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.26.0",  # For TestClient
]

# Documentation
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.5.0",
]

# Database drivers
postgres = ["asyncpg>=0.29.0", "psycopg[binary]>=3.1.0"]
mysql = ["aiomysql>=0.2.0"]

# All optional deps
all = ["my-project[dev,docs,postgres]"]
```

### Installation
```bash
# Install specific group
uv pip install -e ".[dev]"

# Install multiple groups
uv pip install -e ".[dev,docs]"

# Install all optional
uv pip install -e ".[all]"
```

## Entry Points

### CLI Scripts
```toml
[project.scripts]
my-cli = "my_project.cli:main"
my-server = "my_project.server:run"
```

```python
# my_project/cli.py
import click

@click.group()
def main():
    """My CLI application."""
    pass

@main.command()
@click.argument("name")
def greet(name: str):
    """Greet someone."""
    click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    main()
```

### Plugins
```toml
[project.entry-points."my_project.plugins"]
csv = "my_project.plugins.csv:CSVPlugin"
json = "my_project.plugins.json:JSONPlugin"
```

```python
# Discover plugins
from importlib.metadata import entry_points

plugins = entry_points(group="my_project.plugins")
for plugin in plugins:
    plugin_class = plugin.load()
    instance = plugin_class()
```

## Project Layout

### src Layout (Recommended)
```
my-project/
├── pyproject.toml
├── README.md
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── py.typed        # Type hint marker
│       └── core.py
└── tests/
    └── test_core.py
```

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

### Flat Layout
```
my-project/
├── pyproject.toml
├── README.md
├── my_project/
│   ├── __init__.py
│   └── core.py
└── tests/
    └── test_core.py
```

## Type Hint Marker (py.typed)

Create empty `py.typed` file to indicate package has type hints:

```
src/my_project/py.typed  # Empty file
```

```toml
# Include in package data
[tool.setuptools.package-data]
my_project = ["py.typed"]
```

## Building & Publishing

### Build Package
```bash
# Build wheel and sdist
uv build
# or
python -m build

# Output in dist/
# my_project-1.0.0-py3-none-any.whl
# my_project-1.0.0.tar.gz
```

### Publish to PyPI
```bash
# Upload to PyPI
uv publish
# or
python -m twine upload dist/*

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

### .pypirc Configuration
```ini
# ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-xxx

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxx
```

## Makefile Integration

```makefile
.PHONY: install dev test lint format typecheck verify clean

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy .

verify: lint format typecheck test
	@echo "All checks passed!"

clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```
