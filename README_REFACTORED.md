# Hotel Management System - Modern Python Implementation

A complete refactoring of the legacy C++ Hotel Management System into a modern, asynchronous Python application using SQLAlchemy, following SOLID principles and clean architecture patterns.

## 🎯 Overview

This project transforms a legacy C++ console application into a production-ready Python system with:

- **Async/Await Support**: Full asynchronous operations using `asyncio` and SQLAlchemy async
- **Clean Architecture**: Separation of concerns with distinct layers (Domain, Repository, Service, API)
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Type Safety**: Comprehensive type hints throughout the codebase
- **AI Agent Ready**: Simple, high-level API designed for easy integration with AI agents
- **Database Persistence**: SQLAlchemy ORM with SQLite (easily adaptable to PostgreSQL, MySQL, etc.)

## 📁 Project Structure

```
Hotel-Management-System/
├── src/
│   ├── __init__.py
│   ├── domain/              # Domain entities and business logic
│   │   ├── __init__.py
│   │   └── entities.py      # Booking entity with validation
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   └── database.py      # SQLAlchemy models and DB manager
│   ├── repositories/        # Data access layer (Repository pattern)
│   │   ├── __init__.py
│   │   └── booking_repository.py
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   └── booking_service.py
│   └── api/                 # High-level API for external systems
│       ├── __init__.py
│       └── hotel_manager.py # Main facade for AI agents
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── example_usage.py         # Usage examples
└── README_REFACTORED.md     # This file
```

## 🏗️ Architecture

### Layer Responsibilities

1. **Domain Layer** (`src/domain/`)
   - Pure business entities with validation
   - No dependencies on infrastructure
   - Contains core business rules

2. **Repository Layer** (`src/repositories/`)
   - Abstracts data access
   - Implements Repository pattern
   - Converts between domain entities and database models

3. **Service Layer** (`src/services/`)
   - Orchestrates business operations
   - Implements business logic
   - Coordinates between domain and repository layers

4. **API Layer** (`src/api/`)
   - High-level facade for external systems
   - Manages dependency injection
   - Provides simple interface for AI agents

### SOLID Principles Implementation

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Extensible through interfaces without modification
- **Liskov Substitution**: Repository interface allows swapping implementations
- **Interface Segregation**: Focused interfaces (IBookingRepository)
- **Dependency Inversion**: High-level modules depend on abstractions

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
import asyncio
from src.api import create_hotel_manager

async def main():
    # Initialize hotel manager
    manager = await create_hotel_manager()
    
    try:
        # Book a room
        booking = await manager.book_room(
            room_number=101,
            customer_name="John Doe",
            customer_address="123 Main St",
            customer_phone="+1-555-0123",
            days_of_stay=3
        )
        print(f"Booking created: {booking['id']}")
        
        # Get booking details
        details = await manager.get_booking(booking['id'])
        print(f"Customer: {details['customer_name']}")
        
        # Check room availability
        available = await manager.is_room_available(102)
        print(f"Room 102 available: {available}")
        
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Example

```bash
python example_usage.py
```

## 📚 API Reference

### HotelManager Class

The main entry point for all hotel management operations.

#### Methods

**`book_room(room_number, customer_name, customer_address, customer_phone, days_of_stay, daily_rate=None)`**
- Books a hotel room
- Returns: Dictionary with booking details
- Raises: `ValueError` if room is already booked

**`get_booking(booking_id)`**
- Retrieves booking by ID
- Returns: Dictionary with booking details or None

**`get_room_booking(room_number)`**
- Gets active booking for a specific room
- Returns: Dictionary with booking details or None

**`get_all_bookings(active_only=False)`**
- Retrieves all bookings
- Returns: List of booking dictionaries

**`update_booking(booking_id, customer_name=None, customer_address=None, customer_phone=None, days_of_stay=None)`**
- Updates booking details
- Returns: Dictionary with updated booking

**`checkout(booking_id)`**
- Checks out a booking
- Returns: Dictionary with updated booking

**`delete_booking(booking_id)`**
- Permanently deletes a booking
- Returns: Boolean indicating success

**`is_room_available(room_number)`**
- Checks room availability
- Returns: Boolean

**`get_statistics()`**
- Gets hotel statistics
- Returns: Dictionary with statistics

## 🔧 Configuration

Configuration can be set via environment variables or using the `config.py` file:

```python
# Environment variables
DATABASE_URL=sqlite+aiosqlite:///hotel.db
DEFAULT_DAILY_RATE=900.00
HOTEL_NAME=XYZ Group of Hotels
DEBUG=false
```

## 🤖 AI Agent Integration

The system is designed for easy AI agent integration:

```python
# Simple async interface
manager = await create_hotel_manager()

# Natural language to API mapping
user_request = "Book room 101 for John Doe, 3 days"
booking = await manager.book_room(
    room_number=101,
    customer_name="John Doe",
    customer_address="...",
    customer_phone="...",
    days_of_stay=3
)

# Get structured data
stats = await manager.get_statistics()
# Returns: {"total_bookings": 5, "active_bookings": 3, ...}
```

## 🔄 Migration from C++ Version

### Key Improvements

1. **File-based to Database**: Replaced binary file storage with SQLAlchemy ORM
2. **Synchronous to Async**: Full async/await support for better performance
3. **Procedural to OOP**: Clean object-oriented design with SOLID principles
4. **Console to API**: Flexible API that can be used by any interface (CLI, Web, AI Agent)
5. **No Validation to Full Validation**: Comprehensive input validation and error handling

### Feature Mapping

| C++ Feature | Python Implementation |
|-------------|----------------------|
| `hotel::add()` | `HotelManager.book_room()` |
| `hotel::display()` | `HotelManager.get_booking()` |
| `hotel::rooms()` | `HotelManager.get_all_bookings()` |
| `hotel::modify()` | `HotelManager.update_booking()` |
| `hotel::delete_rec()` | `HotelManager.delete_booking()` |
| `hotel::check()` | `HotelManager.is_room_available()` |

## 🧪 Testing

The architecture supports easy testing:

```python
# Mock repository for testing
class MockBookingRepository(IBookingRepository):
    async def create(self, booking):
        # Test implementation
        pass

# Inject mock in service
service = BookingService(MockBookingRepository())
```

## 📈 Performance Considerations

- **Async Operations**: Non-blocking I/O for better concurrency
- **Connection Pooling**: SQLAlchemy manages database connections efficiently
- **Lazy Loading**: Data loaded only when needed
- **Type Hints**: Better IDE support and fewer runtime errors

## 🔐 Security Features

- Input validation in domain entities
- SQL injection prevention via SQLAlchemy ORM
- Type safety throughout the codebase
- Proper error handling and logging

## 🛠️ Extending the System

### Adding a New Feature

1. **Domain Layer**: Add entity or update existing
2. **Repository Layer**: Add data access methods
3. **Service Layer**: Implement business logic
4. **API Layer**: Expose through HotelManager

Example: Adding room types

```python
# 1. Domain entity
@dataclass
class RoomType:
    name: str
    base_rate: Decimal

# 2. Repository
class IRoomTypeRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[RoomType]:
        pass

# 3. Service
class RoomTypeService:
    async def get_available_types(self):
        return await self._repository.get_all()

# 4. API
class HotelManager:
    async def get_room_types(self):
        # Implementation
        pass
```

## 📝 Type Hints

All code includes comprehensive type hints for better IDE support and type checking:

```python
async def book_room(
    self,
    room_number: int,
    customer_name: str,
    customer_address: str,
    customer_phone: str,
    days_of_stay: int,
    daily_rate: Optional[float] = None,
) -> Dict[str, Any]:
    ...
```

## 🤝 Contributing

This refactored system follows best practices:
- PEP 8 style guide
- Type hints everywhere
- Comprehensive docstrings
- SOLID principles
- Clean architecture

## 📄 License

Same as original project.

## 👥 Credits

- **Original C++ Version**: Daljeet Singh Chhabra (2016-2018)
- **Python Refactoring**: Bob (Senior Software Architect) (2026)

## 🔗 Related Documentation

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Asyncio](https://docs.python.org/3/library/asyncio.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)