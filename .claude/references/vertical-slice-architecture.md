# Building a Vertical Slice Architecture Project from Scratch: A Practical Guide for AI Coding

**By Rasmus Widing**
_Product Builder | AI Adoption Specialist | Creator of the PRP Framework_

Enough theory. You know WHY to use VSA ([Article 2](link-to-article-2)). You know WHAT tooling you need ([Article 1](link-to-article-1)). Now let's BUILD.

After three years building AI-powered applications and working with engineering teams adopting vertical slice architecture, I've learned that **the hardest part isn't understanding the theory—it's knowing where to put things**.

Where does the database configuration go? What about logging? If you're building an AI agent, where do you place the OpenAI client? Which code is okay to duplicate, and which should follow DRY principles?

This article answers these questions with concrete examples. You already know [why Vertical Slice Architecture wins for AI coding](link-to-article-2). If you're jumping in here, read that first—it's worth it. Now let's build one.

All code examples reference the [companion project](link-to-project) - use it as a template for your own projects.

---

## The Setup Paradox: Infrastructure Before Features

Here's the paradox that trips up everyone: Vertical Slice Architecture organizes by features... but you need infrastructure before you have features.

Database connections, logging, configuration, API clients—these exist before your first product or user slice. So where do they go?

**The pragmatic solution:** Create `core/` and `shared/` first, then never touch them unless absolutely necessary.

```
my-fastapi-app/
├── app/
│   ├── core/              # Foundation infrastructure
│   ├── shared/            # Cross-feature utilities
│   ├── products/          # Feature slice
│   ├── inventory/         # Feature slice
│   └── categories/        # Feature slice
├── tests/
├── .env
├── pyproject.toml
└── README.md
```

This balances architectural purity with practical necessity.

---

## The Decision Framework: What Goes Where

### Rule 1: `core/` - Universal Infrastructure

The `core/` directory contains infrastructure that exists **before** features and is **universal** across the entire application. Think of it as the engine and chassis—necessary for the car to run, but not specific to any particular trip.

**What goes in `core/`:**

```
app/core/
├── config.py              # Application configuration
├── database.py            # Database connection & session management
├── logging.py             # Logging setup and configuration
├── middleware.py          # Request/response middleware
├── exceptions.py          # Base exception classes
├── dependencies.py        # Global FastAPI dependencies
└── events.py              # Application lifecycle events
```

**Decision rule:** If removing every feature slice would still require this code, it goes in `core/`.

**Why this matters for AI:** Configuration scattered across files wastes tokens on search. Centralizing in `core/config.py` gives AI a single source of truth.

#### Example: `core/config.py`

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Application
    app_name: str = "My FastAPI App"
    debug: bool = False
    version: str = "1.0.0"

    # Database
    database_url: str

    # Observability
    log_level: str = "INFO"

    # Security
    secret_key: str
    algorithm: str = "HS256"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
```

AI agents know exactly where to find configuration. No guessing, no token waste.

#### Example: `core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Key decision:** Database setup goes in `core/` because it's universal infrastructure. Individual feature models go in their own slices.

### Rule 2: `shared/` - The Three-Feature Rule

The `shared/` directory is for code that **multiple features use** but isn't foundational infrastructure. This is the gray area that causes the most confusion.

**What goes in `shared/`:**

```
app/shared/
├── models.py              # Base models, mixins (e.g., TimestampMixin)
├── schemas.py             # Common Pydantic schemas (e.g., PaginationParams)
├── utils.py               # Generic utilities (string helpers, date utils)
└── integrations/          # External API clients (3+ features)
    ├── email.py
    ├── storage.py
    └── payment.py
```

**Critical rule:** Code moves to `shared/` when **three or more** feature slices need it. Until then, duplicate it.

**Why three?**

- One instance: Feature-specific
- Two instances: Might be coincidence
- Three instances: Proven pattern worth abstracting

**Process:**

1. First feature: Write the code inline
2. Second feature: Duplicate it (add comment noting duplication)
3. Third feature: Extract to `shared/` and refactor all three features to use it

This prevents premature abstraction while catching genuine shared behavior.

#### Example: `shared/models.py`

```python
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False
        )
```

**When to use:** All your database models need timestamps. This is genuinely shared behavior, not feature-specific.

#### Example: `shared/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response format."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
```

**Why shared:** Every feature that lists items uses pagination the same way. Common interface, common code.

### Rule 3: Feature Slices - Self-Contained Domains

Each feature slice is self-contained. Everything needed to understand and modify that feature lives in its directory.

**Complete feature structure:**

```
app/products/
├── routes.py              # FastAPI endpoints
├── service.py             # Business logic
├── repository.py          # Database operations
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic request/response models
├── exceptions.py          # Feature-specific exceptions
├── validators.py          # Feature-specific validation (optional)
├── cache.py               # Feature-specific caching logic (optional)
├── tasks.py               # Feature-specific background tasks (optional)
├── test_routes.py         # Endpoint tests
├── test_service.py        # Business logic tests
└── README.md              # Feature documentation
```

**Not every feature needs every file.** Start with `routes.py`, `service.py`, and `schemas.py`. Add others as needed.

**Flow:** Routes → Service → Repository → Database

**Why this works for AI:**

- All product-related code in one place
- AI can load `products/` and understand entire feature
- Clear separation of concerns
- Each file has single, clear responsibility

---

## Setting Up Core Infrastructure: The Foundation

### Step 1: Structured Logging with Correlation IDs

Standard logging is hard for AI to parse. Structured JSON logging with correlation IDs is essential.

**Pattern:**

```python
# core/logging.py
import structlog
from contextvars import ContextVar
import uuid
from typing import Any

from app.core.config import get_settings

# Context variable for request correlation ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get the current request ID from context."""
    return request_id_var.get()


def set_request_id(request_id: str | None = None) -> str:
    """Set request ID in context, generating one if not provided."""
    if not request_id:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def add_request_id(logger, method_name, event_dict):
    """Processor to add request ID to all log entries."""
    request_id = get_request_id()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    structlog.configure(
        processors=[
            add_request_id,  # Add request ID to every log entry
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,  # Format exception tracebacks
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a logger instance for a module."""
    return structlog.get_logger(name)
```

**Why critical:** The `format_exc_info` processor formats exception tracebacks as strings in JSON output. When you use `exc_info=True`, AI agents get the full stack trace in a parseable format.

**Usage in features:**

```python
# products/service.py
from app.core.logging import get_logger

logger = get_logger(__name__)

def create_product(self, product_data: ProductCreate) -> ProductResponse:
    logger.info("product.create.started", sku=product_data.sku, name=product_data.name)

    try:
        product = self.repository.create(product_data)
        logger.info("product.create.success", product_id=product.id)
        return ProductResponse.model_validate(product)
    except Exception as e:
        logger.error("product.create.failed", error=str(e), exc_info=True)
        raise
```

**Event naming pattern:** `{domain}.{action}.{status}`

AI can search logs for `"level": "error"` and get full context including exact line numbers. The `request_id` allows tracing a single request through multiple features.

### Step 2: Request Middleware

```python
# core/middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.core.logging import set_request_id, get_request_id, get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation ID."""

    async def dispatch(self, request: Request, call_next):
        # Extract or generate request ID
        request_id = request.headers.get("X-Request-ID")
        set_request_id(request_id)

        start_time = time.time()
        logger.info(
            "request.started",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            logger.info(
                "request.completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(duration, 3),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = get_request_id()
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request.failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_seconds=round(duration, 3),
                exc_info=True,
            )
            raise
```

Every request gets a unique ID that appears in all logs. When debugging, AI can filter logs by `request_id` to see the complete request lifecycle across all features.

---

## Building Your First Feature Slice: Products Example

Let's build a complete feature following the pattern. This demonstrates the full cycle.

### Step 1: Create the Structure

```bash
mkdir -p app/products
touch app/products/{__init__,routes,service,repository,models,schemas,exceptions}.py
touch app/products/test_service.py
touch app/products/README.md
```

### Step 2: Define Schemas (Outside-In Development)

Start with the API contract—what requests come in, what responses go out.

```python
# products/schemas.py
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class ProductBase(BaseModel):
    """Shared product attributes."""
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    price: Decimal = Field(..., gt=0)


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(None, gt=0)
    is_active: bool | None = None


class ProductResponse(ProductBase):
    """Schema for product responses."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### Step 3: Define Models

```python
# products/models.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text

from app.core.database import Base
from app.shared.models import TimestampMixin


class Product(Base, TimestampMixin):
    """Product database model."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
```

### Step 4: Build Repository (Data Access Layer)

```python
# products/repository.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.products.models import Product
from app.products.schemas import ProductCreate, ProductUpdate


class ProductRepository:
    """Data access layer for products."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        return self.db.query(Product).filter(Product.sku == sku).first()

    def list(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Product]:
        """List products with pagination."""
        query = self.db.query(Product)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.offset(skip).limit(limit).all()

    def create(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        product = Product(**product_data.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product, product_data: ProductUpdate) -> Product:
        """Update an existing product."""
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product
```

### Step 5: Implement Service (Business Logic)

```python
# products/service.py
from sqlalchemy.orm import Session
from typing import List

from app.products.repository import ProductRepository
from app.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.products.exceptions import ProductNotFoundError, ProductAlreadyExistsError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProductService:
    """Business logic for products."""

    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def get_product(self, product_id: int) -> ProductResponse:
        """Get a product by ID."""
        logger.info("product.fetch.started", product_id=product_id)

        product = self.repository.get(product_id)
        if not product:
            logger.warning("product.fetch.not_found", product_id=product_id)
            raise ProductNotFoundError(f"Product {product_id} not found")

        return ProductResponse.model_validate(product)

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create a new product."""
        logger.info("product.create.started", sku=product_data.sku, name=product_data.name)

        # Check if SKU already exists
        existing = self.repository.get_by_sku(product_data.sku)
        if existing:
            logger.warning("product.create.duplicate_sku", sku=product_data.sku)
            raise ProductAlreadyExistsError(f"Product with SKU {product_data.sku} already exists")

        product = self.repository.create(product_data)
        logger.info("product.create.success", product_id=product.id, sku=product.sku)

        return ProductResponse.model_validate(product)
```

### Step 6: Define Exceptions

```python
# products/exceptions.py
class ProductError(Exception):
    """Base exception for product-related errors."""
    pass


class ProductNotFoundError(ProductError):
    """Raised when a product is not found."""
    pass


class ProductAlreadyExistsError(ProductError):
    """Raised when attempting to create a product with duplicate SKU."""
    pass
```

### Step 7: Create Routes (API Layer)

```python
# products/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.products.service import ProductService
from app.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.products.exceptions import ProductNotFoundError, ProductAlreadyExistsError

router = APIRouter(prefix="/products", tags=["products"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Dependency to get ProductService instance."""
    return ProductService(db)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """Create a new product."""
    try:
        return service.create_product(product_data)
    except ProductAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Get a product by ID."""
    try:
        return service.get_product(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
```

### Step 8: Document the Feature

```markdown
# products/README.md

# Products Feature

Manages product catalog including CRUD operations and pricing.

## Key Flows

### Create Product

1. Validate product data (name, SKU, price)
2. Check SKU doesn't exist
3. Create product in database
4. Return product response

## Database Schema

Table: `products`

- `id` (Integer, PK)
- `sku` (String, Unique)
- `name` (String)
- `description` (Text, nullable)
- `price` (Numeric)
- `is_active` (Boolean)
- `created_at`, `updated_at` (DateTime)

## Business Rules

1. SKU must be unique across all products
2. Price must be positive with max 2 decimal places
3. Deleted products use soft delete (`is_active=False`)

## Integration Points

- **Inventory**: Products link to inventory records by SKU
- **Orders**: Order items reference products by ID
```

**Why this README helps AI:** AI reads the README before diving into code. Business rules prevent AI from breaking constraints. Integration points show dependencies between features.

---

## When to Duplicate vs. DRY: The Decision Matrix

**Duplicate when:**

1. Used by 1-2 features (wait for the third)
2. Slight variations exist (don't force abstraction)
3. Feature-specific logic (even if code looks similar)
4. Uncertain stability (requirements might diverge)

**Extract to shared when:**

1. Used by 3+ features (clear pattern)
2. Identical logic (no variations)
3. Infrastructure-level (database mixins, base schemas)
4. Stable interface (won't need feature-specific mods)

**Example:** Product price validation vs. inventory quantity validation may look similar, but they solve different problems for different domains. Keep them separate.

---

## LLM Integration: Where Does AI Infrastructure Go?

If you're building an AI agent or LLM-powered application, you need additional infrastructure.

### Decision Rule

**Small apps (AI is core purpose):** Put in `core/llm.py`

**Larger apps (multiple AI features):** Create dedicated `llm/` module

```
app/llm/
├── clients.py             # LLM client wrappers
├── prompts.py             # Centralized prompt management
├── tools.py               # Tool registry for function calling
└── messages.py            # Message formatting utilities
```

### Three Approaches to LLM Integration

**1. Direct API Calls**
Call OpenAI/Anthropic APIs directly in your feature code. Simple for getting started, but repetitive.

**2. Agent Frameworks (Pydantic AI, LangChain, CrewAI)**
Use a framework to handle conversation state, tool calling, and prompt management. Great for complex workflows, but adds dependencies and abstraction layers.

**3. Wrapper Pattern (Recommended)**
Build thin wrappers around provider APIs with a unified interface. Abstracts provider differences while staying lightweight.

**Where code goes:**

- `app/llm/clients.py` - Provider wrappers (Anthropic, OpenAI)
- `app/llm/prompts.py` - Reusable prompts used across features
- `app/llm/tools.py` - Function definitions for tool calling
- `app/products/ai.py` - Product-specific AI logic (e.g., description generation)

**Why this works:** Generic infrastructure lives in `llm/`, feature-specific AI logic stays in features. AI agents know exactly where to find what they need.

### Critical Pattern: Client Wrapper with Protocol

Don't expose raw OpenAI/Anthropic APIs directly. Wrap them with a unified interface:

```python
# llm/clients.py
from anthropic import Anthropic
from openai import OpenAI
from functools import lru_cache
from typing import Protocol

from app.core.config import get_settings


class LLMClient(Protocol):
    """Protocol for LLM clients."""
    def complete(self, prompt: str, **kwargs) -> str: ...


class AnthropicClientWrapper:
    """Wrapper for Anthropic client with standard interface."""

    def __init__(self):
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.default_model = settings.anthropic_model

    def complete(self, prompt: str, **kwargs) -> str:
        """Complete a prompt using Claude."""
        response = self.client.messages.create(
            model=kwargs.get("model", self.default_model),
            max_tokens=kwargs.get("max_tokens", 1024),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


@lru_cache()
def get_llm_client(provider: str = "anthropic") -> LLMClient:
    """Get LLM client by provider name."""
    if provider == "anthropic":
        return AnthropicClientWrapper()
    elif provider == "openai":
        return OpenAIClientWrapper()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
```

**Why:** Abstracts provider differences, makes switching easier, AI understands interface without knowing implementation.

See `app/llm/` in reference project for complete implementation including prompt management and tool registry.

---

## Cross-Feature Patterns: The Messy 20%

### Transactions Spanning Multiple Features

**Problem:** Creating an order needs products (check availability), inventory (reserve stock), orders (create record).

**Solution: Orchestrating Service (Recommended)**

```python
# orders/service.py
from sqlalchemy.orm import Session

from app.products.repository import ProductRepository
from app.inventory.repository import InventoryRepository
from app.orders.repository import OrderRepository


class OrderService:
    """Service that orchestrates across multiple features."""

    def __init__(self, db: Session):
        self.db = db
        self.products = ProductRepository(db)  # Same session
        self.inventory = InventoryRepository(db)  # Same session
        self.orders = OrderRepository(db)  # Same session

    def create_order(self, order_data: OrderCreate) -> OrderResponse:
        """Create order with transaction spanning multiple features."""
        try:
            # All repositories share session = single transaction
            for item in order_data.items:
                product = self.products.get(item.product_id)
                if not product:
                    raise ProductNotFoundError(f"Product {item.product_id} not found")

                # Check and reserve inventory
                available = self.inventory.check_availability(product.sku, item.quantity)
                if not available:
                    raise InsufficientInventoryError(f"Not enough stock for {product.sku}")

                self.inventory.reserve(product.sku, item.quantity)

            # Create the order
            order = self.orders.create(order_data)

            # Commit happens when session context closes
            self.db.commit()
            return OrderResponse.model_validate(order)

        except Exception as e:
            self.db.rollback()
            raise
```

**Why this works:** Transaction boundary is explicit, orchestrating service coordinates workflow, AI can trace entire flow in one file.

### Feature-to-Feature Data Access

**Critical rule:** If Feature A reads from Feature B's tables:

1. **Never write** to Feature B's tables from Feature A
2. Document the dependency in both feature READMEs
3. Consider events for writes, direct reads for queries

Example: Inventory can read from products repository, but never writes to products table.

### Background Jobs and Tasks

**Problem:** Product images need resizing, emails need sending, reports need generating. Where do async tasks live?

**Solution: Feature-Specific Task Files**

```python
# products/tasks.py
from celery import shared_task
from app.products.service import ProductService

@shared_task
def resize_product_images(product_id: int):
    """Background task to resize product images."""
    # Task logic here
```

**Why this works:** Tasks are feature-specific, so they live in the feature directory. Celery/RQ configuration lives in `core/tasks.py`, but individual task definitions live with their features.

### Caching Strategy

**Problem:** Product catalog gets hit constantly. Where does caching logic go?

**Solution: Core Client + Feature Keys**

```python
# core/cache.py - Redis client setup
from redis import Redis
from functools import lru_cache

@lru_cache()
def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url)

# products/cache.py - Feature-specific caching
from app.core.cache import get_redis

class ProductCache:
    def __init__(self):
        self.redis = get_redis()
        self.prefix = "products"  # Feature-specific prefix

    def get_product(self, product_id: int):
        key = f"{self.prefix}:product:{product_id}"
        return self.redis.get(key)
```

**Why split:** Core provides infrastructure (Redis client), features own their caching logic and key strategies.

### Feature Flags

**Problem:** Rolling out new pricing engine to 10% of users. Where does feature flag logic go?

**Solution: Core Client + Feature Checks**

```python
# core/feature_flags.py - Flag client
from launchdarkly import LDClient

@lru_cache()
def get_flags_client() -> LDClient:
    return LDClient(settings.launchdarkly_key)

# products/service.py - Feature uses flags
from app.core.feature_flags import get_flags_client

class ProductService:
    def calculate_price(self, product, user):
        flags = get_flags_client()
        if flags.variation("new-pricing-engine", user, False):
            return self.new_pricing_calculation(product)
        return self.legacy_pricing_calculation(product)
```

**Why split:** Flag client is infrastructure (`core/`), flag checks happen in features where business logic lives.

### Authentication: The Dual-Nature Feature

Authentication is both a feature (login/register) and infrastructure (authorization middleware).

**Structure:**

- `core/dependencies.py` - `get_current_user()` dependency used everywhere
- `auth/` - Feature slice with login, register, user management, JWT utils

```python
# core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.utils import decode_jwt
from app.auth.models import User

security = HTTPBearer()


def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    token = credentials.credentials

    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
```

**Why split:** `auth/` owns user data and authentication logic. `core/dependencies.py` provides reusable FastAPI dependencies. Other features just use `Depends(get_current_user)`.

---

## Testing in Vertical Slices: Unit vs Integration

Testing follows the same isolation principle as your code structure.

**Unit Tests: Colocated with Features**

```
app/products/
├── service.py
├── repository.py
├── test_service.py        # Tests service business logic
├── test_repository.py     # Tests repository data access
└── conftest.py            # Product-specific test fixtures
```

**Why colocate:** When AI modifies `products/service.py`, it can immediately see and update `test_service.py`. Everything needed to understand the feature—including how to test it—lives together.

**Integration Tests: Separate Directory**

```
tests/
├── conftest.py            # Shared fixtures (test database, test client)
├── integration/
│   ├── test_order_flow.py      # Orders + Products + Inventory
│   └── test_checkout_flow.py   # Multiple features working together
└── e2e/
    └── test_full_purchase.py    # End-to-end scenarios
```

**Why separate:** Integration tests span multiple features. They belong at the root level, not buried in a single feature directory.

**The pattern:**

- Test ONE feature in isolation? → Unit test in feature directory
- Test MULTIPLE features together? → Integration test in `tests/`
- Test ENTIRE user flow? → E2E test in `tests/e2e/`

**Fixtures strategy:**

- Feature-specific fixtures → `app/products/conftest.py`
- Shared fixtures (DB, clients) → `tests/conftest.py`

---

## Scaffolding a New Project: The Practical Checklist

Here's the exact order to set up new Vertical Slice projects:

### Step 1: Initialize Project (5 minutes)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
mkdir my-fastapi-app && cd my-fastapi-app
uv init

# Add dependencies
uv add fastapi uvicorn sqlalchemy pydantic pydantic-settings structlog
# Why structlog? AI can't parse your printf-debugging logs at 2am. JSON output is searchable.

# Add dev dependencies
uv add --dev ruff mypy pyright pytest pytest-cov httpx
# Why all three? Ruff catches style, MyPy catches obvious types, Pyright catches subtle type bugs.
```

### Step 2: Create Directory Structure (5 minutes)

```bash
mkdir -p app/core app/shared tests
touch app/__init__.py app/core/__init__.py app/shared/__init__.py
touch app/main.py .env .env.example README.md
```

### Step 3: Setup Core Infrastructure (15 minutes)

Create in this order:

1. `app/core/config.py` - Configuration first, everything depends on it
2. `app/core/logging.py` - Logging second, for debugging setup issues
3. `app/core/database.py` - Database connection
4. `app/core/exceptions.py` - Base exception classes
5. `app/core/dependencies.py` - Common FastAPI dependencies

### Step 4: Create `main.py` (5 minutes)

```python
# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.database import engine, Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    # Add cleanup code here


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}


# Import and include routers here as features are added
# from app.products.routes import router as products_router
# app.include_router(products_router)
```

### Step 5: Setup Tooling (5 minutes)

Add to `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ANN", "S", "RUF"]
ignore = ["B008", "ANN101", "S311"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ANN"]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]
```

### Step 6: Create First Feature Slice (15 minutes)

Follow the Products example above.

### Step 7: Wire Up the Feature (5 minutes)

```python
# app/main.py
from app.products.routes import router as products_router

app.include_router(products_router)
```

### Step 8: Test Your Setup (5 minutes)

```bash
# Run the server
uv run uvicorn app.main:app --reload

# In another terminal, test
curl http://localhost:8000/health
curl http://localhost:8000/products
```

**Total time: ~60 minutes** from zero to working Vertical Slice API.

---

## Migrating from Layered Architecture: The Strangler Fig Pattern

You have an existing layered architecture app. Don't rewrite. Instead, **add new features in Vertical Slice alongside old code**, then gradually migrate hot paths.

**The strategy:**

1. All new features use VSA
2. When touching old features, migrate if you're changing >50% of the code
3. Document the boundary in `MIGRATION.md`
4. Stop at 80%—leave stable code alone

**Why this works:** Most code changes happen in a small percentage of files. Migrate those, ignore the rest. Over 6-12 months, you'll naturally migrate what matters.

Migration deserves its own deep-dive article. For now: start with new features, let the old structure coexist peacefully.

---

## Common Pitfalls and Solutions

### Pitfall 1: Over-Extracting to Shared Too Early

**Solution:** Wait for the third instance. Duplicate code in 2 places is better than the wrong abstraction.

### Pitfall 2: Putting Feature Logic in Core

**Solution:** `core/` is for universal infrastructure only. If it's feature-specific, it goes in the feature slice.

### Pitfall 3: Creating Circular Dependencies

**Solution:** Use event bus pattern for cross-feature communication:

```python
# shared/events.py
from typing import Callable, Dict, List
from dataclasses import dataclass


@dataclass
class Event:
    """Base class for domain events."""
    pass


class EventBus:
    """Simple event bus for cross-feature communication."""

    def __init__(self):
        self._handlers: Dict[type, List[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: Event):
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)


event_bus = EventBus()
```

---

## The AI-Ready Checklist

**Structure:**

- [ ] Clear `core/` directory (universal infrastructure only)
- [ ] Optional `shared/` (3+ feature rule enforced)
- [ ] Each feature self-contained in own directory
- [ ] No circular dependencies between features

**Documentation:**

- [ ] Root README explains architecture and setup
- [ ] Each feature has README (flows, rules, integration points)
- [ ] `ARCHITECTURE.md` documents where code goes

**Observability:**

- [ ] Structured JSON logging with correlation IDs
- [ ] Consistent event naming (`domain.action.status`)
- [ ] Exception tracebacks in parseable format (`exc_info=True`)

**AI Friendliness:**

- [ ] Files under 300 lines
- [ ] Explicit dependencies (no hidden globals)
- [ ] Minimal magic and metaprogramming
- [ ] Feature code is self-contained and discoverable

---

## Quick Reference: Decision Flowchart

```
New code to write?
│
├─ Does it exist before any features?
│  (config, database, logging, middleware)
│  └─→ core/
│
├─ Used by 3+ features AND identical logic?
│  (base models, pagination, utilities)
│  └─→ shared/
│
├─ Feature-specific?
│  (business logic, domain models, endpoints)
│  └─→ Feature slice (app/{feature}/)
│
└─ Used by 1-2 features?
   └─→ Duplicate in each feature (wait for third)
```

---

## Project Structure Template

```
my-fastapi-app/
├── app/
│   ├── core/                      # Universal infrastructure
│   │   ├── config.py              # Settings
│   │   ├── database.py            # DB connection
│   │   ├── logging.py             # Structured logging + correlation
│   │   ├── middleware.py          # Request/response middleware
│   │   ├── exceptions.py          # Base exceptions
│   │   └── dependencies.py        # Global dependencies
│   │
│   ├── shared/                    # 3+ features only
│   │   ├── models.py              # Base models, mixins
│   │   ├── schemas.py             # Common schemas (PaginationParams)
│   │   └── integrations/          # External APIs (email, storage, payment)
│   │
│   ├── llm/                       # LLM infrastructure (if building AI)
│   │   ├── clients.py             # Wrapped clients with unified interface
│   │   ├── prompts.py             # Prompt management
│   │   └── tools.py               # Tool registry
│   │
│   └── products/                  # Feature slice (repeat pattern)
│       ├── routes.py              # Endpoints
│       ├── service.py             # Business logic
│       ├── repository.py          # Data access
│       ├── models.py              # Database models
│       ├── schemas.py             # Request/response models
│       ├── exceptions.py          # Feature exceptions
│       ├── test_service.py        # Tests colocated
│       └── README.md              # Feature docs
│
├── tests/
│   ├── conftest.py                # Shared fixtures
│   └── integration/               # Cross-feature tests
│
├── .env.example                   # Template for environment
├── pyproject.toml                 # Dependencies and tooling
└── README.md                      # Project overview
```

---

## When VSA Is (and Isn't) Worth It

**Use VSA when:**

- Building production applications (not throwaway prototypes)
- Working with AI agents extensively
- Team size > 1 (enables parallel work)
- Codebase > 5K lines (navigation becomes expensive)
- Planning to maintain code for 6+ months

**Skip VSA for:**

- POCs and MVPs you'll throw away
- Weekend projects just for you
- Scripts and automation tools
- True prototypes validating an idea

**The parallel development advantage:** With VSA, two developers (or AI agents) can work on separate features simultaneously without merge conflicts. The `products/` directory is completely independent from `inventory/`. One person adds product reviews while another builds inventory tracking—zero coordination needed.

---

## Conclusion: Build for Change, Optimize for Understanding

Vertical Slice Architecture isn't about following dogma. It's about organizing code so both humans and AI can:

1. **Understand it quickly** - Everything related lives together
2. **Modify it safely** - Clear boundaries prevent ripple effects
3. **Extend it easily** - Add features without touching existing code

**The principles:**

- Start with infrastructure (`core/` first, features second)
- Keep features isolated (self-contained slices)
- Duplicate until proven shared (three-feature rule)
- Document liberally (READMEs are AI's navigation)
- Make implicit explicit (no hidden dependencies)

When you need to add a feature, you know exactly where it goes. When AI needs to modify a feature, it finds all related code in one place. When something breaks, logs point directly to the responsible slice.

This is how you build systems that scale with both team size and AI assistance.

See the [reference project](link-to-project) for complete implementations of every pattern in this guide.

---

**About the Author**

Rasmus Widing is a Product Builder and AI adoption specialist who has been using AI to build agents, automations, and web apps for over three years. He created the PRP (Product Requirements Prompts) framework for agentic engineering, now used by hundreds of engineers. He helps teams adopt AI through systematic frameworks, workshops, and training at [rasmuswiding.com](https://rasmuswiding.com).

_Want to dive deeper? Check out my PRP framework on GitHub: [github.com/Wirasm/PRPs-agentic-eng](https://github.com/Wirasm/PRPs-agentic-eng)_