"""
SQLAlchemy database models and configuration
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any

from sqlalchemy import String, Integer, Numeric, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models"""
    pass


class BookingModel(Base):
    """
    Database model for hotel room bookings
    
    Represents a customer's room reservation with all associated details.
    """
    __tablename__ = "bookings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_address: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    days_of_stay: Mapped[int] = mapped_column(Integer, nullable=False)
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("900.00"))
    total_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    check_in_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    check_out_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    def __repr__(self) -> str:
        return (
            f"<BookingModel(id={self.id}, room_number={self.room_number}, "
            f"customer_name='{self.customer_name}', is_active={self.is_active})>"
        )


class DatabaseManager:
    """
    Manages database connections and session lifecycle
    
    Provides async database engine and session management following
    the singleton pattern for connection pooling.
    """
    
    _instance: Optional['DatabaseManager'] = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    
    def __new__(cls, database_url: str = "sqlite+aiosqlite:///hotel_management.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(database_url)
        return cls._instance
    
    def _initialize(self, database_url: str) -> None:
        """Initialize database engine and session factory"""
        self._engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL query logging
            future=True,
            pool_pre_ping=True,  # Verify connections before using
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def create_tables(self) -> None:
        """Create all database tables"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self) -> None:
        """Drop all database tables (use with caution)"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    def get_session(self) -> AsyncSession:
        """Get a new database session"""
        return self._session_factory()
    
    async def close(self) -> None:
        """Close database engine and cleanup resources"""
        if self._engine:
            await self._engine.dispose()

# Made with Bob
