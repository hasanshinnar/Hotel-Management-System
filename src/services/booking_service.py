"""
Service layer implementing business logic for hotel bookings
Following Single Responsibility Principle
"""
from decimal import Decimal
from typing import List, Optional

from src.domain.entities import Booking
from src.repositories.booking_repository import IBookingRepository


class BookingService:
    """
    Service class handling booking business logic
    
    Orchestrates operations between the domain layer and repository layer.
    Contains all business rules and validation logic.
    """
    
    def __init__(self, repository: IBookingRepository):
        """
        Initialize service with repository dependency
        
        Args:
            repository: Booking repository implementation
        """
        self._repository = repository
    
    async def create_booking(
        self,
        room_number: int,
        customer_name: str,
        customer_address: str,
        customer_phone: str,
        days_of_stay: int,
        daily_rate: Optional[Decimal] = None,
    ) -> Booking:
        """
        Create a new room booking
        
        Args:
            room_number: Room number to book
            customer_name: Customer's full name
            customer_address: Customer's address
            customer_phone: Customer's phone number
            days_of_stay: Number of days for the stay
            daily_rate: Daily rate (defaults to 900.00)
            
        Returns:
            Created booking entity
            
        Raises:
            ValueError: If room is already booked or validation fails
        """
        # Check room availability
        if not await self._repository.is_room_available(room_number):
            raise ValueError(f"Room {room_number} is already booked")
        
        # Create booking entity (validation happens in __post_init__)
        booking = Booking(
            room_number=room_number,
            customer_name=customer_name.strip(),
            customer_address=customer_address.strip(),
            customer_phone=customer_phone.strip(),
            days_of_stay=days_of_stay,
            daily_rate=daily_rate or Decimal("900.00"),
        )
        
        # Persist to database
        return await self._repository.create(booking)
    
    async def get_booking_by_id(self, booking_id: int) -> Optional[Booking]:
        """
        Retrieve booking by ID
        
        Args:
            booking_id: ID of the booking
            
        Returns:
            Booking entity or None if not found
        """
        return await self._repository.get_by_id(booking_id)
    
    async def get_booking_by_room(self, room_number: int) -> Optional[Booking]:
        """
        Retrieve active booking by room number
        
        Args:
            room_number: Room number to search for
            
        Returns:
            Active booking for the room or None if not found
        """
        return await self._repository.get_by_room_number(room_number)
    
    async def get_all_active_bookings(self) -> List[Booking]:
        """
        Retrieve all active bookings
        
        Returns:
            List of active booking entities
        """
        return await self._repository.get_all_active()
    
    async def get_all_bookings(self) -> List[Booking]:
        """
        Retrieve all bookings (active and inactive)
        
        Returns:
            List of all booking entities
        """
        return await self._repository.get_all()
    
    async def update_booking(
        self,
        booking_id: int,
        customer_name: Optional[str] = None,
        customer_address: Optional[str] = None,
        customer_phone: Optional[str] = None,
        days_of_stay: Optional[int] = None,
    ) -> Booking:
        """
        Update an existing booking
        
        Args:
            booking_id: ID of the booking to update
            customer_name: New customer name (optional)
            customer_address: New customer address (optional)
            customer_phone: New customer phone (optional)
            days_of_stay: New number of days (optional)
            
        Returns:
            Updated booking entity
            
        Raises:
            ValueError: If booking not found or validation fails
        """
        # Retrieve existing booking
        booking = await self._repository.get_by_id(booking_id)
        if booking is None:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        # Update details (validation happens in update_details method)
        booking.update_details(
            customer_name=customer_name.strip() if customer_name else None,
            customer_address=customer_address.strip() if customer_address else None,
            customer_phone=customer_phone.strip() if customer_phone else None,
            days_of_stay=days_of_stay,
        )
        
        # Persist changes
        return await self._repository.update(booking)
    
    async def checkout_booking(self, booking_id: int) -> Booking:
        """
        Check out a booking (mark as inactive)
        
        Args:
            booking_id: ID of the booking to check out
            
        Returns:
            Updated booking entity
            
        Raises:
            ValueError: If booking not found
        """
        booking = await self._repository.get_by_id(booking_id)
        if booking is None:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        booking.checkout()
        return await self._repository.update(booking)
    
    async def delete_booking(self, booking_id: int) -> bool:
        """
        Delete a booking permanently
        
        Args:
            booking_id: ID of the booking to delete
            
        Returns:
            True if deleted, False if not found
        """
        return await self._repository.delete(booking_id)
    
    async def is_room_available(self, room_number: int) -> bool:
        """
        Check if a room is available for booking
        
        Args:
            room_number: Room number to check
            
        Returns:
            True if available, False if already booked
        """
        return await self._repository.is_room_available(room_number)
    
    async def calculate_revenue(self) -> Decimal:
        """
        Calculate total revenue from all bookings
        
        Returns:
            Total revenue as Decimal
        """
        bookings = await self._repository.get_all()
        return sum((booking.total_fare or Decimal("0.00") for booking in bookings), Decimal("0.00"))
    
    async def get_booking_statistics(self) -> dict:
        """
        Get booking statistics
        
        Returns:
            Dictionary with booking statistics
        """
        all_bookings = await self._repository.get_all()
        active_bookings = await self._repository.get_all_active()
        
        total_revenue = sum((booking.total_fare or Decimal("0.00") for booking in all_bookings), Decimal("0.00"))
        active_revenue = sum((booking.total_fare or Decimal("0.00") for booking in active_bookings), Decimal("0.00"))
        
        return {
            "total_bookings": len(all_bookings),
            "active_bookings": len(active_bookings),
            "completed_bookings": len(all_bookings) - len(active_bookings),
            "total_revenue": float(total_revenue),
            "active_revenue": float(active_revenue),
            "average_stay_duration": (
                sum(booking.days_of_stay for booking in all_bookings) / len(all_bookings)
                if all_bookings else 0
            ),
        }

# Made with Bob
