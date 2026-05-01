# Architecture Documentation

## System Architecture Overview

This document describes the architecture of the refactored Hotel Management System, explaining design decisions, patterns used, and how components interact.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           HotelManager (Facade)                      │   │
│  │  - Simple interface for AI agents                    │   │
│  │  - Dependency injection                              │   │
│  │  - Session management                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           BookingService                             │   │
│  │  - Business logic orchestration                      │   │
│  │  - Validation and rules                              │   │
│  │  - Transaction coordination                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      IBookingRepository (Interface)                  │   │
│  │           ▲                                          │   │
│  │           │                                          │   │
│  │  ┌────────┴────────┐                                │   │
│  │  │ BookingRepository│                                │   │
│  │  │  - Data access   │                                │   │
│  │  │  - CRUD ops      │                                │   │
│  │  │  - Queries       │                                │   │
│  │  └─────────────────┘                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Booking (Entity)                        │   │
│  │  - Pure business logic                               │   │
│  │  - Validation rules                                  │   │
│  │  - No infrastructure dependencies                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         DatabaseManager & Models                     │   │
│  │  - SQLAlchemy ORM                                    │   │
│  │  - Connection pooling                                │   │
│  │  - Async operations                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. Repository Pattern

**Purpose**: Abstracts data access logic from business logic

**Implementation**:
- [`IBookingRepository`](src/repositories/booking_repository.py:15) - Interface defining contract
- [`BookingRepository`](src/repositories/booking_repository.py:65) - SQLAlchemy implementation

**Benefits**:
- Easy to swap database implementations
- Testable with mock repositories
- Separates concerns

### 2. Facade Pattern

**Purpose**: Provides simplified interface to complex subsystem

**Implementation**:
- [`HotelManager`](src/api/hotel_manager.py:18) - High-level API for external systems

**Benefits**:
- Simple API for AI agents
- Hides complexity
- Single entry point

### 3. Dependency Injection

**Purpose**: Invert control of dependencies

**Implementation**:
```python
# Service depends on repository interface
class BookingService:
    def __init__(self, repository: IBookingRepository):
        self._repository = repository

# Manager creates and injects dependencies
async with self._get_service() as service:
    # service has repository injected
```

**Benefits**:
- Loose coupling
- Easy testing
- Flexible configuration

### 4. Domain-Driven Design (DDD)

**Purpose**: Focus on core business domain

**Implementation**:
- [`Booking`](src/domain/entities.py:12) entity with business logic
- Rich domain model with validation
- Separation from infrastructure

**Benefits**:
- Business logic in one place
- Easy to understand and maintain
- Technology-agnostic

## SOLID Principles

### Single Responsibility Principle (SRP)

Each class has one reason to change:

- [`Booking`](src/domain/entities.py:12) - Represents booking entity
- [`BookingRepository`](src/repositories/booking_repository.py:65) - Handles data access
- [`BookingService`](src/services/booking_service.py:12) - Orchestrates business logic
- [`HotelManager`](src/api/hotel_manager.py:18) - Provides API interface

### Open/Closed Principle (OCP)

Open for extension, closed for modification:

```python
# Can add new repository implementations without changing service
class PostgresBookingRepository(IBookingRepository):
    # New implementation
    pass

# Service works with any IBookingRepository
service = BookingService(PostgresBookingRepository())
```

### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for base types:

```python
# Any IBookingRepository implementation can be used
def create_service(repo: IBookingRepository) -> BookingService:
    return BookingService(repo)

# Both work
service1 = create_service(BookingRepository(session))
service2 = create_service(MockBookingRepository())
```

### Interface Segregation Principle (ISP)

Clients shouldn't depend on interfaces they don't use:

- [`IBookingRepository`](src/repositories/booking_repository.py:15) - Focused interface for booking operations
- No "god interface" with unrelated methods

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions:

```python
# Service depends on interface, not concrete implementation
class BookingService:
    def __init__(self, repository: IBookingRepository):  # Interface
        self._repository = repository
```

## Async Architecture

### Why Async?

1. **Better Performance**: Non-blocking I/O operations
2. **Scalability**: Handle multiple requests concurrently
3. **Modern Python**: Leverages Python 3.7+ async/await
4. **Database Efficiency**: Async SQLAlchemy for better throughput

### Implementation

```python
# All operations are async
async def book_room(self, ...):
    async with self._get_service() as service:
        booking = await service.create_booking(...)
        return booking.to_dict()

# Context manager for session lifecycle
@asynccontextmanager
async def _get_service(self):
    session = self._db_manager.get_session()
    try:
        repository = BookingRepository(session)
        service = BookingService(repository)
        yield service
    finally:
        await session.close()
```

## Data Flow

### Booking Creation Flow

```
1. AI Agent/Client
   ↓ calls book_room()
2. HotelManager (API Layer)
   ↓ creates service with session
3. BookingService (Service Layer)
   ↓ validates and creates entity
4. Booking (Domain Layer)
   ↓ validates business rules
5. BookingRepository (Repository Layer)
   ↓ converts to database model
6. SQLAlchemy (Infrastructure)
   ↓ persists to database
7. Database
```

### Response Flow

```
1. Database
   ↓ returns model
2. SQLAlchemy
   ↓ hydrates model
3. BookingRepository
   ↓ converts to entity
4. BookingService
   ↓ returns entity
5. HotelManager
   ↓ converts to dict
6. AI Agent/Client
```

## Error Handling

### Validation Errors

```python
# Domain validation
class Booking:
    def validate(self):
        if self.room_number <= 0:
            raise ValueError("Room number must be positive")

# Service validation
async def create_booking(self, ...):
    if not await self._repository.is_room_available(room_number):
        raise ValueError(f"Room {room_number} is already booked")
```

### Database Errors

```python
# Repository handles database errors
try:
    await self._session.commit()
except SQLAlchemyError as e:
    await self._session.rollback()
    raise
```

## Testing Strategy

### Unit Tests

```python
# Test domain logic
def test_booking_validation():
    with pytest.raises(ValueError):
        Booking(room_number=-1, ...)

# Test service with mock repository
@pytest.mark.asyncio
async def test_create_booking():
    mock_repo = MockBookingRepository()
    service = BookingService(mock_repo)
    booking = await service.create_booking(...)
    assert booking.room_number == 101
```

### Integration Tests

```python
# Test with real database
@pytest.mark.asyncio
async def test_full_booking_flow():
    manager = await create_hotel_manager("sqlite+aiosqlite:///:memory:")
    booking = await manager.book_room(...)
    assert booking['id'] is not None
```

## Configuration Management

### Environment-Based Config

```python
# config.py
@dataclass
class AppConfig:
    database: DatabaseConfig
    hotel: HotelConfig
    
    @classmethod
    def from_env(cls):
        return cls(
            database=DatabaseConfig.from_env(),
            hotel=HotelConfig.from_env(),
        )
```

### Usage

```python
from config import config

# Access configuration
db_url = config.database.url
daily_rate = config.hotel.default_daily_rate
```

## Database Schema

### Bookings Table

```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number INTEGER UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_address VARCHAR(200) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    days_of_stay INTEGER NOT NULL,
    daily_rate NUMERIC(10, 2) NOT NULL,
    total_fare NUMERIC(10, 2) NOT NULL,
    check_in_date DATETIME NOT NULL,
    check_out_date DATETIME,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX idx_room_number ON bookings(room_number);
```

## Performance Considerations

### Connection Pooling

```python
# DatabaseManager uses connection pooling
self._engine = create_async_engine(
    database_url,
    pool_pre_ping=True,  # Verify connections
)
```

### Lazy Loading

```python
# Data loaded only when needed
booking = await repository.get_by_id(1)  # Single query
# Related data loaded on access
```

### Batch Operations

```python
# Get all bookings in one query
bookings = await repository.get_all_active()
```

## Security Considerations

### SQL Injection Prevention

- SQLAlchemy ORM prevents SQL injection
- Parameterized queries automatically

### Input Validation

```python
# Domain-level validation
class Booking:
    def validate(self):
        if not self.customer_name.strip():
            raise ValueError("Customer name required")
```

### Type Safety

```python
# Type hints prevent type-related bugs
async def book_room(
    self,
    room_number: int,  # Must be int
    customer_name: str,  # Must be str
    ...
) -> Dict[str, Any]:
```

## Extensibility

### Adding New Features

1. **New Entity**: Add to [`src/domain/`](src/domain/)
2. **New Repository**: Add to [`src/repositories/`](src/repositories/)
3. **New Service**: Add to [`src/services/`](src/services/)
4. **Expose in API**: Update [`HotelManager`](src/api/hotel_manager.py:18)

### Example: Adding Payment Processing

```python
# 1. Domain
@dataclass
class Payment:
    booking_id: int
    amount: Decimal
    method: str

# 2. Repository
class IPaymentRepository(ABC):
    @abstractmethod
    async def create(self, payment: Payment) -> Payment:
        pass

# 3. Service
class PaymentService:
    def __init__(self, repository: IPaymentRepository):
        self._repository = repository
    
    async def process_payment(self, ...):
        # Business logic
        pass

# 4. API
class HotelManager:
    async def process_payment(self, ...):
        async with self._get_payment_service() as service:
            return await service.process_payment(...)
```

## Migration Path

### From C++ to Python

| C++ Component | Python Equivalent |
|---------------|-------------------|
| Binary file I/O | SQLAlchemy ORM |
| Synchronous operations | Async/await |
| Console UI | API interface |
| Global state | Dependency injection |
| Manual memory management | Automatic GC |

## Best Practices

1. **Always use async/await** for I/O operations
2. **Validate at domain level** for business rules
3. **Use type hints** everywhere
4. **Keep layers separate** - no cross-layer dependencies
5. **Test with mocks** for unit tests
6. **Use context managers** for resource cleanup
7. **Document public APIs** with docstrings
8. **Follow PEP 8** style guide

## Future Enhancements

Potential areas for extension:

1. **Authentication/Authorization**: Add user management
2. **Payment Processing**: Integrate payment gateways
3. **Notifications**: Email/SMS notifications
4. **Reporting**: Advanced analytics and reports
5. **Multi-tenancy**: Support multiple hotels
6. **REST API**: Add FastAPI/Flask endpoints
7. **WebSocket**: Real-time updates
8. **Caching**: Redis for performance
9. **Message Queue**: Celery for background tasks
10. **Monitoring**: Prometheus/Grafana integration

## Conclusion

This architecture provides:

- ✅ Clean separation of concerns
- ✅ Easy to test and maintain
- ✅ Scalable and performant
- ✅ Type-safe and robust
- ✅ AI agent friendly
- ✅ Production-ready

The system follows industry best practices and modern Python patterns, making it suitable for production use and easy integration with AI agents.