"""
Repository pattern implementation for booking data access
Abstracts database operations following the Repository pattern
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Booking
from src.models.database import BookingModel


class IBookingRepository(ABC):
    """
    Interface for booking repository (Dependency Inversion Principle)
    
    Defines the contract for booking data access operations.
    This allows for easy testing and swapping of implementations.
    """
    
    @abstractmethod
    async def create(self, booking: Booking) -> Booking:
        """Create a new booking"""
        pass
    
    @abstractmethod
    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID"""
        pass
    
    @abstractmethod
    async def get_by_room_number(self, room_number: int) -> Optional[Booking]:
        """Get booking by room number"""
        pass
    
    @abstractmethod
    async def get_all_active(self) -> List[Booking]:
        """Get all active bookings"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Booking]:
        """Get all bookings"""
        pass
    
    @abstractmethod
    async def update(self, booking: Booking) -> Booking:
        """Update an existing booking"""
        pass
    
    @abstractmethod
    async def delete(self, booking_id: int) -> bool:
        """Delete a booking"""
        pass
    
    @abstractmethod
    async def is_room_available(self, room_number: int) -> bool:
        """Check if a room is available"""
        pass


class BookingRepository(IBookingRepository):
    """
    SQLAlchemy implementation of booking repository
    
    Handles all database operations for bookings using async SQLAlchemy.
    Converts between domain entities and database models.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session
        
        Args:
            session: Async SQLAlchemy session for database operations
        """
        self._session = session
    
    def _to_entity(self, model: BookingModel) -> Booking:
        """Convert database model to domain entity"""
        return Booking(
            id=model.id,
            room_number=model.room_number,
            customer_name=model.customer_name,
            customer_address=model.customer_address,
            customer_phone=model.customer_phone,
            days_of_stay=model.days_of_stay,
            daily_rate=model.daily_rate,
            total_fare=model.total_fare,
            check_in_date=model.check_in_date,
            check_out_date=model.check_out_date,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _to_model(self, entity: Booking) -> BookingModel:
        """Convert domain entity to database model"""
        model = BookingModel(
            room_number=entity.room_number,
            customer_name=entity.customer_name,
            customer_address=entity.customer_address,
            customer_phone=entity.customer_phone,
            days_of_stay=entity.days_of_stay,
            daily_rate=entity.daily_rate,
            total_fare=entity.total_fare,
            check_in_date=entity.check_in_date,
            check_out_date=entity.check_out_date,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        
        if entity.id is not None:
            model.id = entity.id
        
        return model
    
    async def create(self, booking: Booking) -> Booking:
        """
        Create a new booking in the database
        
        Args:
            booking: Booking entity to create
            
        Returns:
            Created booking with assigned ID
            
        Raises:
            ValueError: If room is already booked
        """
        # Check if room is available
        if not await self.is_room_available(booking.room_number):
            raise ValueError(f"Room {booking.room_number} is already booked")
        
        model = self._to_model(booking)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        
        return self._to_entity(model)
    
    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """
        Get booking by ID
        
        Args:
            booking_id: ID of the booking
            
        Returns:
            Booking entity or None if not found
        """
        stmt = select(BookingModel).where(BookingModel.id == booking_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._to_entity(model) if model else None
    
    async def get_by_room_number(self, room_number: int) -> Optional[Booking]:
        """
        Get active booking by room number
        
        Args:
            room_number: Room number to search for
            
        Returns:
            Active booking for the room or None if not found
        """
        stmt = select(BookingModel).where(
            BookingModel.room_number == room_number,
            BookingModel.is_active == True
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._to_entity(model) if model else None
    
    async def get_all_active(self) -> List[Booking]:
        """
        Get all active bookings
        
        Returns:
            List of active booking entities
        """
        stmt = select(BookingModel).where(BookingModel.is_active == True)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_all(self) -> List[Booking]:
        """
        Get all bookings (active and inactive)
        
        Returns:
            List of all booking entities
        """
        stmt = select(BookingModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]
    
    async def update(self, booking: Booking) -> Booking:
        """
        Update an existing booking
        
        Args:
            booking: Booking entity with updated data
            
        Returns:
            Updated booking entity
            
        Raises:
            ValueError: If booking not found
        """
        if booking.id is None:
            raise ValueError("Cannot update booking without ID")
        
        stmt = (
            update(BookingModel)
            .where(BookingModel.id == booking.id)
            .values(
                customer_name=booking.customer_name,
                customer_address=booking.customer_address,
                customer_phone=booking.customer_phone,
                days_of_stay=booking.days_of_stay,
                daily_rate=booking.daily_rate,
                total_fare=booking.total_fare,
                check_out_date=booking.check_out_date,
                is_active=booking.is_active,
                updated_at=booking.updated_at,
            )
        )
        
        await self._session.execute(stmt)
        await self._session.commit()
        
        # Fetch updated booking
        updated = await self.get_by_id(booking.id)
        if updated is None:
            raise ValueError(f"Booking with ID {booking.id} not found")
        
        return updated
    
    async def delete(self, booking_id: int) -> bool:
        """
        Delete a booking
        
        Args:
            booking_id: ID of the booking to delete
            
        Returns:
            True if deleted, False if not found
        """
        stmt = delete(BookingModel).where(BookingModel.id == booking_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        
        return result.rowcount > 0 if hasattr(result, 'rowcount') else False
    
    async def is_room_available(self, room_number: int) -> bool:
        """
        Check if a room is available for booking
        
        Args:
            room_number: Room number to check
            
        Returns:
            True if available, False if already booked
        """
        stmt = select(BookingModel).where(
            BookingModel.room_number == room_number,
            BookingModel.is_active == True
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return model is None

# Made with Bob
