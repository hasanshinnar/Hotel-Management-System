"""
High-level API for hotel management operations
Designed for easy integration with AI agents and external systems
"""
import asyncio
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import List, Optional, Dict, Any

from src.models.database import DatabaseManager
from src.repositories.booking_repository import BookingRepository
from src.services.booking_service import BookingService
from src.domain.entities import Booking


class HotelManager:
    """
    Facade class providing a simple, high-level API for hotel management
    
    This class serves as the main entry point for AI agents and external systems.
    It handles dependency injection and provides async context management.
    """
    
    def __init__(self, database_url: str = "sqlite+aiosqlite:///hotel_management.db"):
        """
        Initialize hotel manager
        
        Args:
            database_url: Database connection URL
        """
        self._database_url = database_url
        self._db_manager: Optional[DatabaseManager] = None
        self._service: Optional[BookingService] = None
    
    async def initialize(self) -> None:
        """Initialize database and create tables if needed"""
        self._db_manager = DatabaseManager(self._database_url)
        await self._db_manager.create_tables()
    
    async def close(self) -> None:
        """Close database connections and cleanup resources"""
        if self._db_manager:
            await self._db_manager.close()
    
    @asynccontextmanager
    async def _get_service(self):
        """Context manager for service with database session"""
        if self._db_manager is None:
            await self.initialize()
        
        assert self._db_manager is not None, "Database manager not initialized"
        session = self._db_manager.get_session()
        try:
            repository = BookingRepository(session)
            service = BookingService(repository)
            yield service
        finally:
            await session.close()
    
    async def book_room(
        self,
        room_number: int,
        customer_name: str,
        customer_address: str,
        customer_phone: str,
        days_of_stay: int,
        daily_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Book a hotel room
        
        Args:
            room_number: Room number to book
            customer_name: Customer's full name
            customer_address: Customer's address
            customer_phone: Customer's phone number
            days_of_stay: Number of days for the stay
            daily_rate: Daily rate (defaults to 900.00)
            
        Returns:
            Dictionary with booking details
            
        Raises:
            ValueError: If room is already booked or validation fails
        """
        async with self._get_service() as service:
            booking = await service.create_booking(
                room_number=room_number,
                customer_name=customer_name,
                customer_address=customer_address,
                customer_phone=customer_phone,
                days_of_stay=days_of_stay,
                daily_rate=Decimal(str(daily_rate)) if daily_rate else None,
            )
            return booking.to_dict()
    
    async def get_booking(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """
        Get booking details by ID
        
        Args:
            booking_id: ID of the booking
            
        Returns:
            Dictionary with booking details or None if not found
        """
        async with self._get_service() as service:
            booking = await service.get_booking_by_id(booking_id)
            return booking.to_dict() if booking else None
    
    async def get_room_booking(self, room_number: int) -> Optional[Dict[str, Any]]:
        """
        Get active booking for a specific room
        
        Args:
            room_number: Room number to search for
            
        Returns:
            Dictionary with booking details or None if room is not booked
        """
        async with self._get_service() as service:
            booking = await service.get_booking_by_room(room_number)
            return booking.to_dict() if booking else None
    
    async def get_all_bookings(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all bookings
        
        Args:
            active_only: If True, return only active bookings
            
        Returns:
            List of booking dictionaries
        """
        async with self._get_service() as service:
            if active_only:
                bookings = await service.get_all_active_bookings()
            else:
                bookings = await service.get_all_bookings()
            return [booking.to_dict() for booking in bookings]
    
    async def update_booking(
        self,
        booking_id: int,
        customer_name: Optional[str] = None,
        customer_address: Optional[str] = None,
        customer_phone: Optional[str] = None,
        days_of_stay: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Update booking details
        
        Args:
            booking_id: ID of the booking to update
            customer_name: New customer name (optional)
            customer_address: New customer address (optional)
            customer_phone: New customer phone (optional)
            days_of_stay: New number of days (optional)
            
        Returns:
            Dictionary with updated booking details
            
        Raises:
            ValueError: If booking not found or validation fails
        """
        async with self._get_service() as service:
            booking = await service.update_booking(
                booking_id=booking_id,
                customer_name=customer_name,
                customer_address=customer_address,
                customer_phone=customer_phone,
                days_of_stay=days_of_stay,
            )
            return booking.to_dict()
    
    async def checkout(self, booking_id: int) -> Dict[str, Any]:
        """
        Check out a booking
        
        Args:
            booking_id: ID of the booking to check out
            
        Returns:
            Dictionary with updated booking details
            
        Raises:
            ValueError: If booking not found
        """
        async with self._get_service() as service:
            booking = await service.checkout_booking(booking_id)
            return booking.to_dict()
    
    async def delete_booking(self, booking_id: int) -> bool:
        """
        Delete a booking permanently
        
        Args:
            booking_id: ID of the booking to delete
            
        Returns:
            True if deleted, False if not found
        """
        async with self._get_service() as service:
            return await service.delete_booking(booking_id)
    
    async def is_room_available(self, room_number: int) -> bool:
        """
        Check if a room is available
        
        Args:
            room_number: Room number to check
            
        Returns:
            True if available, False if booked
        """
        async with self._get_service() as service:
            return await service.is_room_available(room_number)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get hotel booking statistics
        
        Returns:
            Dictionary with statistics including total bookings, revenue, etc.
        """
        async with self._get_service() as service:
            return await service.get_booking_statistics()


# Convenience function for AI agents
async def create_hotel_manager(database_url: str = "sqlite+aiosqlite:///hotel_management.db") -> HotelManager:
    """
    Create and initialize a hotel manager instance
    
    Args:
        database_url: Database connection URL
        
    Returns:
        Initialized HotelManager instance
    """
    manager = HotelManager(database_url)
    await manager.initialize()
    return manager

# Made with Bob
