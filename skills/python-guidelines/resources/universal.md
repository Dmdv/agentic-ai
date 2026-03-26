# Universal Python Guidelines

Core patterns that apply to all Python code regardless of domain.

## Type Hints (Modern Syntax)

### Python 3.10+ Union Syntax
```python
# Modern (preferred)
def process(data: str | None) -> dict[str, int]:
    ...

# Legacy (avoid in new code)
from typing import Optional, Dict
def process(data: Optional[str]) -> Dict[str, int]:
    ...
```

### Generic Collections (Python 3.9+)
```python
# Modern - use built-in types directly
items: list[str] = []
mapping: dict[str, int] = {}
coordinates: tuple[float, float] = (0.0, 0.0)

# Legacy (avoid)
from typing import List, Dict, Tuple
items: List[str] = []
```

### TypeVar and Generics
```python
from typing import TypeVar, Generic

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Cache(Generic[K, V]):
    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        return self._data.get(key)
```

### Protocol for Structural Typing
```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

def process_readable(r: Readable) -> str:
    return r.read()  # Any object with read() method works
```

### TypedDict for Structured Dicts
```python
from typing import TypedDict, NotRequired

class UserConfig(TypedDict):
    name: str
    email: str
    age: NotRequired[int]  # Optional key

config: UserConfig = {"name": "Alice", "email": "a@b.com"}
```

## Naming Conventions (PEP 8)

### Variables and Functions
```python
# snake_case for variables and functions
user_count = 0
def calculate_total_price(items: list[Item]) -> Decimal:
    ...

# SCREAMING_SNAKE_CASE for constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30.0
API_BASE_URL = "https://api.example.com"
```

### Classes and Exceptions
```python
# PascalCase for classes
class UserAccount:
    ...

class InvalidCredentialsError(Exception):
    """Exception names should end with 'Error'."""
    ...
```

### Private and Protected
```python
class Service:
    def __init__(self) -> None:
        self._internal_state = {}   # Protected (single underscore)
        self.__private_data = []    # Private (double underscore)

    def _helper_method(self) -> None:
        """Protected method - use within class hierarchy."""
        ...
```

### Boolean Variables
```python
# Use is_, has_, can_, should_ prefixes
is_active = True
has_permission = False
can_edit = user.role == "admin"
should_retry = attempt < MAX_RETRIES
```

## Import Organization

### Import Order (Ruff I rules)
```python
# 1. Standard library
import json
import os
from collections.abc import Callable
from pathlib import Path

# 2. Third-party packages
import httpx
import pydantic
from fastapi import FastAPI, HTTPException

# 3. First-party (your project)
from app.core.config import settings
from app.models.user import User
from app.services.auth import AuthService
```

### Import Style
```python
# Prefer explicit imports over star imports
from typing import Any, TypeVar  # Good
from typing import *             # Bad - pollutes namespace

# Group related imports
from pydantic import BaseModel, Field, validator

# Use 'from' for specific items, 'import' for modules
import json  # When using json.loads(), json.dumps()
from json import loads, dumps  # When using loads(), dumps() directly
```

### Conditional Imports (Type Checking)
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # These imports only happen during type checking, not runtime
    from app.models.user import User
    from app.services.database import Database

class UserService:
    def __init__(self, db: "Database") -> None:  # Forward reference
        self.db = db
```

## Error Handling

### Custom Exceptions
```python
class AppError(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code

class ValidationError(AppError):
    """Raised when input validation fails."""
    pass

class NotFoundError(AppError):
    """Raised when a resource is not found."""
    pass
```

### Exception Handling Patterns
```python
# Catch specific exceptions
try:
    result = await fetch_data(url)
except httpx.TimeoutException:
    logger.warning("Request timed out", url=url)
    raise ServiceUnavailableError("External service timeout")
except httpx.HTTPStatusError as e:
    logger.error("HTTP error", status=e.response.status_code)
    raise

# Use 'from' for exception chaining
try:
    config = load_config(path)
except FileNotFoundError as e:
    raise ConfigurationError(f"Config not found: {path}") from e

# Context managers for cleanup
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        resource.cleanup()
```

## Data Classes and Models

### dataclass for Simple Data
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)  # Immutable
class Point:
    x: float
    y: float

@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
```

### Pydantic for Validation
```python
from pydantic import BaseModel, Field, field_validator

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(..., ge=0, le=150)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip().title()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}  # ORM mode
```

## String Formatting

### f-strings (Always Prefer)
```python
# f-strings are fastest and most readable
name = "Alice"
count = 42
message = f"User {name} has {count} items"

# With expressions
price = 19.99
formatted = f"Price: ${price:.2f}"

# With alignment
for item, qty in items:
    print(f"{item:<20} {qty:>5}")
```

### Multi-line Strings
```python
# Triple quotes for multi-line
query = """
    SELECT id, name, email
    FROM users
    WHERE active = true
    ORDER BY created_at DESC
"""

# Implicit concatenation for long strings
message = (
    f"Processing request for user {user_id} "
    f"with {len(items)} items totaling ${total:.2f}"
)
```

## Path Handling (pathlib)

### Always Use pathlib
```python
from pathlib import Path

# Creating paths
config_dir = Path.home() / ".config" / "myapp"
data_file = Path(__file__).parent / "data" / "config.json"

# Path operations
if not config_dir.exists():
    config_dir.mkdir(parents=True, exist_ok=True)

# Reading/writing
content = data_file.read_text()
data_file.write_text(json.dumps(config))

# Iteration
for py_file in Path("src").rglob("*.py"):
    print(py_file.name)
```

## Logging

### Structured Logging
```python
import logging
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()

# Log with context
logger.info(
    "Processing request",
    user_id=user.id,
    action="update_profile",
    ip_address=request.client.host,
)

# Bind context for request lifecycle
log = logger.bind(request_id=request_id)
log.info("Request started")
# ... later
log.info("Request completed", duration_ms=elapsed)
```

## Performance Patterns

### Generators for Large Data
```python
# Generator for memory efficiency
def read_large_file(path: Path):
    with path.open() as f:
        for line in f:
            yield line.strip()

# Generator expression
squares = (x * x for x in range(1_000_000))
```

### Caching
```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    # Cached based on arguments
    return sum(range(n))

@cache  # Unlimited cache (Python 3.9+)
def load_config() -> dict:
    return json.loads(Path("config.json").read_text())
```

### Collection Pre-allocation
```python
# Pre-allocate when size is known
results: list[int] = [0] * 1000

# Use list comprehension over append loops
squares = [x * x for x in range(100)]  # Faster than loop + append
```
