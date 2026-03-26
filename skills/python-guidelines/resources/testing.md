# Testing Guidelines (pytest)

Comprehensive pytest patterns for reliable, maintainable tests.

## Test Structure

### File Organization
```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests (no external deps)
│   ├── conftest.py      # Unit-specific fixtures
│   ├── test_models.py
│   └── test_services.py
├── integration/         # Integration tests (database, APIs)
│   ├── conftest.py
│   └── test_api.py
└── e2e/                 # End-to-end tests
    └── test_workflows.py
```

### Test Naming
```python
# test_<module>.py files
# Test<Class> classes (optional)
# test_<functionality>_<scenario> functions

def test_user_creation_with_valid_email():
    ...

def test_user_creation_rejects_invalid_email():
    ...

def test_user_update_requires_authentication():
    ...
```

## Fixtures

### Basic Fixtures
```python
import pytest
from app.models import User

@pytest.fixture
def user() -> User:
    """Create a test user."""
    return User(id=1, name="Test User", email="test@example.com")

@pytest.fixture
def admin_user(user: User) -> User:
    """Create an admin user (depends on user fixture)."""
    user.role = "admin"
    return user

def test_user_has_name(user: User):
    assert user.name == "Test User"
```

### Fixture Scopes
```python
@pytest.fixture(scope="function")  # Default - per test
def fresh_user():
    return User(...)

@pytest.fixture(scope="class")  # Shared within test class
def class_db():
    db = create_database()
    yield db
    db.cleanup()

@pytest.fixture(scope="module")  # Shared within module
def module_connection():
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="session")  # Shared across all tests
def docker_services():
    # Start containers once for entire test session
    containers = start_containers()
    yield containers
    stop_containers(containers)
```

### Async Fixtures
```python
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="session")
async def database():
    db = await create_async_database()
    yield db
    await db.close()
```

### Factory Fixtures
```python
@pytest.fixture
def user_factory():
    """Factory for creating users with custom attributes."""
    def _create_user(
        name: str = "Test User",
        email: str | None = None,
        role: str = "user",
    ) -> User:
        if email is None:
            email = f"{name.lower().replace(' ', '.')}@test.com"
        return User(name=name, email=email, role=role)

    return _create_user

def test_admin_permissions(user_factory):
    admin = user_factory(name="Admin", role="admin")
    regular = user_factory(name="Regular")

    assert admin.can_delete_users()
    assert not regular.can_delete_users()
```

## Parametrization

### Basic Parametrize
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input: str, expected: str):
    assert input.upper() == expected
```

### Multiple Parameters
```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_addition(a: int, b: int, expected: int):
    assert add(a, b) == expected
```

### IDs for Readability
```python
@pytest.mark.parametrize("email,valid", [
    pytest.param("user@example.com", True, id="valid_email"),
    pytest.param("invalid", False, id="no_at_symbol"),
    pytest.param("@example.com", False, id="no_local_part"),
    pytest.param("user@", False, id="no_domain"),
])
def test_email_validation(email: str, valid: bool):
    assert is_valid_email(email) == valid
```

### Parametrize Fixtures
```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """Test against multiple database backends."""
    db_type = request.param
    db = create_database(db_type)
    yield db
    db.cleanup()

def test_insert_user(database):
    # Runs 3 times - once per database type
    database.insert(User(...))
    assert database.count("users") == 1
```

### Indirect Parametrize
```python
@pytest.fixture
def user(request):
    """Create user based on parameter."""
    role = request.param
    return User(name="Test", role=role)

@pytest.mark.parametrize("user", ["admin", "user", "guest"], indirect=True)
def test_user_permissions(user: User):
    # user fixture receives role as request.param
    ...
```

## Markers

### Built-in Markers
```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    ...

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Unix-only feature"
)
def test_unix_permissions():
    ...

@pytest.mark.xfail(reason="Known bug #123")
def test_known_issue():
    ...
```

### Custom Markers
```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: requires database")

# test_file.py
@pytest.mark.slow
def test_large_dataset_processing():
    ...

@pytest.mark.integration
def test_database_connection():
    ...

# Run specific markers:
# pytest -m "not slow"
# pytest -m integration
```

### Marker for Async
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result == expected

# With asyncio_mode = "auto" in pytest.ini, marker is optional
async def test_auto_detected():
    result = await async_function()
    assert result == expected
```

## Mocking

### Basic Mocking
```python
from unittest.mock import Mock, MagicMock, patch

def test_with_mock():
    mock_service = Mock()
    mock_service.get_user.return_value = User(id=1, name="Test")

    result = process_user(mock_service, user_id=1)

    mock_service.get_user.assert_called_once_with(1)
    assert result.name == "Test"
```

### Patching
```python
@patch("app.services.external_api.fetch_data")
def test_with_patch(mock_fetch):
    mock_fetch.return_value = {"status": "ok"}

    result = process_external_data()

    assert result.status == "ok"

# Context manager style
def test_with_context_patch():
    with patch("app.services.send_email") as mock_email:
        mock_email.return_value = True

        result = create_user_with_notification(user_data)

        mock_email.assert_called_once()
```

### pytest-mock
```python
def test_with_mocker(mocker):
    # mocker is provided by pytest-mock
    mock_api = mocker.patch("app.services.api_client")
    mock_api.get.return_value = {"data": "test"}

    result = fetch_and_process()

    assert result == "test"

def test_spy(mocker):
    # Spy calls real method but tracks calls
    spy = mocker.spy(user_service, "validate_email")

    user_service.create_user(email="test@example.com")

    spy.assert_called_once_with("test@example.com")
```

### Async Mocking
```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_mock():
    mock_client = AsyncMock()
    mock_client.fetch.return_value = {"status": "ok"}

    result = await process_async(mock_client)

    mock_client.fetch.assert_awaited_once()
```

## Assertions

### Basic Assertions
```python
def test_assertions():
    # Equality
    assert result == expected
    assert result != other

    # Truth/Falsy
    assert is_valid
    assert not is_invalid

    # Membership
    assert item in collection
    assert key in dictionary

    # Type checking
    assert isinstance(obj, ExpectedType)
```

### Exception Testing
```python
def test_raises_exception():
    with pytest.raises(ValueError) as exc_info:
        validate_negative(-1)

    assert "negative" in str(exc_info.value)

def test_raises_with_match():
    with pytest.raises(ValueError, match=r"invalid.*email"):
        validate_email("not-an-email")
```

### Approximate Comparisons
```python
def test_floating_point():
    result = calculate_percentage(1, 3)
    assert result == pytest.approx(33.33, rel=0.01)

def test_list_approx():
    results = [0.1 + 0.2, 0.3]
    assert results[0] == pytest.approx(results[1])
```

## Test Organization Patterns

### Arrange-Act-Assert (AAA)
```python
def test_user_update():
    # Arrange
    user = User(id=1, name="Original")
    update_data = {"name": "Updated"}

    # Act
    result = user_service.update(user.id, update_data)

    # Assert
    assert result.name == "Updated"
```

### Given-When-Then (BDD Style)
```python
def test_user_login_with_valid_credentials():
    # Given a registered user
    user = create_user(email="test@example.com", password="secret")

    # When they attempt to login
    result = auth_service.login(email="test@example.com", password="secret")

    # Then they receive a valid token
    assert result.token is not None
    assert result.user_id == user.id
```

## conftest.py Patterns

### Shared Configuration
```python
# tests/conftest.py
import pytest
from app import create_app
from app.database import Database

@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    app = create_app(testing=True)
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture(autouse=True)
def reset_database(db):
    """Reset database before each test."""
    db.truncate_all()
    yield
    db.truncate_all()
```

### Environment Setup
```python
# tests/conftest.py
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    """Set environment variables for testing."""
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    yield
    del os.environ["TESTING"]
```

## Coverage

### Running with Coverage
```bash
# Basic coverage
pytest --cov=app tests/

# With HTML report
pytest --cov=app --cov-report=html tests/

# Fail under threshold
pytest --cov=app --cov-fail-under=80 tests/

# Show missing lines
pytest --cov=app --cov-report=term-missing tests/
```

### Coverage Configuration
```toml
# pyproject.toml
[tool.coverage.run]
source = ["app"]
branch = true
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 80
```
