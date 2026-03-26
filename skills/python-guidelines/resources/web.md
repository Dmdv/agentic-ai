# Web Development Guidelines (FastAPI)

Modern async web API patterns with FastAPI, Pydantic, and httpx.

## FastAPI Application Structure

### Project Layout
```
app/
├── __init__.py
├── main.py              # Application entry point
├── core/
│   ├── config.py        # Settings management
│   ├── security.py      # Auth utilities
│   └── dependencies.py  # Shared dependencies
├── api/
│   ├── __init__.py
│   ├── dependencies.py  # API-specific dependencies
│   └── v1/
│       ├── __init__.py
│       ├── router.py    # Main router
│       ├── users.py     # User endpoints
│       └── items.py     # Item endpoints
├── models/              # SQLAlchemy/database models
├── schemas/             # Pydantic schemas
└── services/            # Business logic
```

### Application Factory
```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    await init_database()
    await init_cache()
    yield
    # Shutdown
    await close_database()
    await close_cache()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api/v1")
    return app

app = create_app()
```

## Pydantic Schemas

### Request/Response Models
```python
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Request schema - for input validation
class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8)

# Response schema - for output serialization
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Update schema - partial updates
class UpdateUserRequest(BaseModel):
    name: str | None = None
    email: str | None = None
```

### Validators
```python
from pydantic import BaseModel, field_validator, model_validator

class OrderRequest(BaseModel):
    quantity: int
    price: float
    discount: float = 0.0

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v

    @model_validator(mode="after")
    def validate_discount(self) -> "OrderRequest":
        if self.discount > self.price * self.quantity:
            raise ValueError("discount cannot exceed total price")
        return self
```

### Generic Response Wrapper
```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    message: str | None = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool
```

## Dependency Injection

### Basic Dependencies
```python
from fastapi import Depends, HTTPException, status
from app.core.security import decode_token
from app.models import User

async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> User:
    """Extract and validate current user from token."""
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    user = await get_user_by_id(payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user
```

### Database Session Dependency
```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield database session with automatic cleanup."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Service Dependencies
```python
from functools import lru_cache
from app.services.user import UserService
from app.services.email import EmailService

@lru_cache
def get_email_service() -> EmailService:
    """Singleton email service."""
    return EmailService(settings.SMTP_HOST, settings.SMTP_PORT)

async def get_user_service(
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
) -> UserService:
    """Create user service with dependencies."""
    return UserService(db=db, email_service=email_service)
```

## API Endpoints

### CRUD Operations
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.user import CreateUserRequest, UserResponse, UpdateUserRequest
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: CreateUserRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user."""
    return await service.create(data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get user by ID."""
    user = await service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UpdateUserRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update user."""
    user = await service.update(user_id, data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> None:
    """Delete user."""
    deleted = await service.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
```

### Pagination
```python
@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserResponse]:
    """List users with pagination."""
    items, total = await service.list(page=page, page_size=page_size)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=page * page_size < total,
    )
```

## Error Handling

### Custom Exception Handlers
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import AppError, NotFoundError, ValidationError

app = FastAPI()

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": exc.message},
    )

@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": exc.message, "details": exc.details},
    )

@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )
```

## Async HTTP Client (httpx)

### Client Configuration
```python
import httpx
from contextlib import asynccontextmanager

class APIClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @asynccontextmanager
    async def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"User-Agent": "MyApp/1.0"},
            )
        yield self._client

    async def get(self, path: str, **kwargs) -> dict:
        async with self._get_client() as client:
            response = await client.get(path, **kwargs)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, data: dict, **kwargs) -> dict:
        async with self._get_client() as client:
            response = await client.post(path, json=data, **kwargs)
            response.raise_for_status()
            return response.json()

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
```

### Retry Logic
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def fetch_with_retry(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

## Middleware

### Request Logging
```python
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # Add request ID to state
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time

            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )

            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.exception(
                "Request failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
            )
            raise
```

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Configuration Management

### Settings with Pydantic
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "My API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()
```

## Background Tasks

### FastAPI Background Tasks
```python
from fastapi import BackgroundTasks

@router.post("/users/")
async def create_user(
    data: CreateUserRequest,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.create(data)

    # Add background task for email
    background_tasks.add_task(
        send_welcome_email,
        email=user.email,
        name=user.name,
    )

    return user

async def send_welcome_email(email: str, name: str) -> None:
    """Send welcome email (runs in background)."""
    await email_service.send(
        to=email,
        subject="Welcome!",
        body=f"Hello {name}, welcome to our platform!",
    )
```

## Testing FastAPI

### Test Client
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/users/",
        json={"name": "Test", "email": "test@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert data["email"] == "test@example.com"
```

### Dependency Overrides
```python
from app.main import app
from app.api.dependencies import get_user_service

@pytest.fixture
def mock_user_service():
    service = Mock(spec=UserService)
    service.get_by_id.return_value = User(id=1, name="Test", email="test@test.com")
    return service

@pytest.fixture
def client_with_mocks(mock_user_service):
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield TestClient(app)
    app.dependency_overrides.clear()
```
