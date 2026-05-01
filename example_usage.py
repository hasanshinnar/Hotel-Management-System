"""
Example usage of the Hotel Management System
Demonstrates how to use the API for AI agent integration
"""
import asyncio
from decimal import Decimal
from src.api import create_hotel_manager


async def main():
    """Demonstrate hotel management system usage"""
    
    # Create and initialize hotel manager
    print("Initializing Hotel Management System...")
    manager = await create_hotel_manager()
    
    try:
        # Example 1: Book a room
        print("\n=== Booking a Room ===")
        booking = await manager.book_room(
            room_number=101,
            customer_name="John Doe",
            customer_address="123 Main St, New York, NY",
            customer_phone="+1-555-0123",
            days_of_stay=3,
            daily_rate=900.00
        )
        print(f"Booking created: Room {booking['room_number']}")
        print(f"Customer: {booking['customer_name']}")
        print(f"Total Fare: ${booking['total_fare']}")
        booking_id = booking['id']
        
        # Example 2: Check room availability
        print("\n=== Checking Room Availability ===")
        is_available = await manager.is_room_available(101)
        print(f"Room 101 available: {is_available}")
        
        is_available = await manager.is_room_available(102)
        print(f"Room 102 available: {is_available}")
        
        # Example 3: Get booking details
        print("\n=== Getting Booking Details ===")
        booking_details = await manager.get_booking(booking_id)
        if booking_details:
            print(f"Booking ID: {booking_details['id']}")
            print(f"Room: {booking_details['room_number']}")
            print(f"Customer: {booking_details['customer_name']}")
            print(f"Days: {booking_details['days_of_stay']}")
            print(f"Status: {'Active' if booking_details['is_active'] else 'Checked Out'}")
        
        # Example 4: Book another room
        print("\n=== Booking Another Room ===")
        booking2 = await manager.book_room(
            room_number=102,
            customer_name="Jane Smith",
            customer_address="456 Oak Ave, Boston, MA",
            customer_phone="+1-555-0456",
            days_of_stay=5,
        )
        print(f"Booking created: Room {booking2['room_number']}")
        print(f"Customer: {booking2['customer_name']}")
        
        # Example 5: Get all active bookings
        print("\n=== All Active Bookings ===")
        active_bookings = await manager.get_all_bookings(active_only=True)
        print(f"Total active bookings: {len(active_bookings)}")
        for b in active_bookings:
            print(f"  - Room {b['room_number']}: {b['customer_name']} ({b['days_of_stay']} days)")
        
        # Example 6: Update booking
        print("\n=== Updating Booking ===")
        updated = await manager.update_booking(
            booking_id=booking_id,
            days_of_stay=5,  # Extend stay
        )
        print(f"Updated booking {updated['id']}")
        print(f"New days of stay: {updated['days_of_stay']}")
        print(f"New total fare: ${updated['total_fare']}")
        
        # Example 7: Get statistics
        print("\n=== Hotel Statistics ===")
        stats = await manager.get_statistics()
        print(f"Total bookings: {stats['total_bookings']}")
        print(f"Active bookings: {stats['active_bookings']}")
        print(f"Total revenue: ${stats['total_revenue']:.2f}")
        print(f"Average stay duration: {stats['average_stay_duration']:.1f} days")
        
        # Example 8: Checkout
        print("\n=== Checking Out ===")
        checked_out = await manager.checkout(booking_id)
        print(f"Checked out booking {checked_out['id']}")
        print(f"Status: {'Active' if checked_out['is_active'] else 'Checked Out'}")
        
        # Example 9: Verify room is now available
        print("\n=== Verifying Room Availability After Checkout ===")
        is_available = await manager.is_room_available(101)
        print(f"Room 101 available: {is_available}")
        
        # Example 10: Get all bookings (including inactive)
        print("\n=== All Bookings (Including Checked Out) ===")
        all_bookings = await manager.get_all_bookings(active_only=False)
        print(f"Total bookings: {len(all_bookings)}")
        for b in all_bookings:
            status = "Active" if b['is_active'] else "Checked Out"
            print(f"  - Room {b['room_number']}: {b['customer_name']} ({status})")
        
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Cleanup
        await manager.close()
        print("\n=== Hotel Management System Closed ===")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
