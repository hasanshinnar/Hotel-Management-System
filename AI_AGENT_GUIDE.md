# AI Agent Integration Guide

This guide explains how AI agents can interact with the Hotel Management System.

## Quick Start for AI Agents

### Basic Setup

```python
import asyncio
from src.api import create_hotel_manager

async def ai_agent_example():
    # Initialize the system
    manager = await create_hotel_manager()
    
    try:
        # Your AI agent logic here
        pass
    finally:
        await manager.close()

# Run the agent
asyncio.run(ai_agent_example())
```

## Common AI Agent Tasks

### 1. Natural Language to Booking

```python
# User says: "Book room 101 for John Doe, staying 3 days"

async def process_booking_request(user_input: str):
    manager = await create_hotel_manager()
    
    # Parse user input (your NLP logic here)
    room_number = 101
    customer_name = "John Doe"
    days = 3
    
    try:
        booking = await manager.book_room(
            room_number=room_number,
            customer_name=customer_name,
            customer_address="Address from user profile",
            customer_phone="Phone from user profile",
            days_of_stay=days
        )
        
        return f"✅ Booked room {booking['room_number']} for {booking['customer_name']}. Total: ${booking['total_fare']}"
    
    except ValueError as e:
        return f"❌ Cannot book: {str(e)}"
    
    finally:
        await manager.close()
```

### 2. Check Availability

```python
# User asks: "Is room 102 available?"

async def check_room_availability(room_number: int):
    manager = await create_hotel_manager()
    
    try:
        available = await manager.is_room_available(room_number)
        
        if available:
            return f"✅ Room {room_number} is available"
        else:
            # Get booking details
            booking = await manager.get_room_booking(room_number)
            return f"❌ Room {room_number} is booked by {booking['customer_name']}"
    
    finally:
        await manager.close()
```

### 3. Get Booking Information

```python
# User asks: "Show me booking details for room 101"

async def get_booking_info(room_number: int):
    manager = await create_hotel_manager()
    
    try:
        booking = await manager.get_room_booking(room_number)
        
        if booking:
            return {
                "status": "found",
                "room": booking['room_number'],
                "customer": booking['customer_name'],
                "phone": booking['customer_phone'],
                "days": booking['days_of_stay'],
                "total": booking['total_fare'],
                "check_in": booking['check_in_date']
            }
        else:
            return {"status": "not_found", "message": "Room not booked"}
    
    finally:
        await manager.close()
```

### 4. List All Bookings

```python
# User asks: "Show me all active bookings"

async def list_active_bookings():
    manager = await create_hotel_manager()
    
    try:
        bookings = await manager.get_all_bookings(active_only=True)
        
        summary = []
        for booking in bookings:
            summary.append({
                "room": booking['room_number'],
                "customer": booking['customer_name'],
                "days": booking['days_of_stay'],
                "total": booking['total_fare']
            })
        
        return {
            "count": len(bookings),
            "bookings": summary
        }
    
    finally:
        await manager.close()
```

### 5. Update Booking

```python
# User says: "Extend room 101 booking to 5 days"

async def extend_booking(room_number: int, new_days: int):
    manager = await create_hotel_manager()
    
    try:
        # Get current booking
        booking = await manager.get_room_booking(room_number)
        
        if not booking:
            return f"❌ No active booking for room {room_number}"
        
        # Update
        updated = await manager.update_booking(
            booking_id=booking['id'],
            days_of_stay=new_days
        )
        
        return f"✅ Extended booking to {updated['days_of_stay']} days. New total: ${updated['total_fare']}"
    
    finally:
        await manager.close()
```

### 6. Checkout

```python
# User says: "Check out room 101"

async def checkout_room(room_number: int):
    manager = await create_hotel_manager()
    
    try:
        booking = await manager.get_room_booking(room_number)
        
        if not booking:
            return f"❌ No active booking for room {room_number}"
        
        checked_out = await manager.checkout(booking['id'])
        
        return f"✅ Checked out room {room_number}. Total paid: ${checked_out['total_fare']}"
    
    finally:
        await manager.close()
```

### 7. Get Statistics

```python
# User asks: "Show me hotel statistics"

async def get_hotel_stats():
    manager = await create_hotel_manager()
    
    try:
        stats = await manager.get_statistics()
        
        return f"""
📊 Hotel Statistics:
- Total bookings: {stats['total_bookings']}
- Active bookings: {stats['active_bookings']}
- Completed: {stats['completed_bookings']}
- Total revenue: ${stats['total_revenue']:.2f}
- Average stay: {stats['average_stay_duration']:.1f} days
"""
    
    finally:
        await manager.close()
```

## Advanced Patterns

### Persistent Manager (Long-Running Agent)

```python
class HotelAssistantAgent:
    """AI agent that maintains a persistent connection"""
    
    def __init__(self):
        self.manager = None
    
    async def start(self):
        """Initialize the agent"""
        self.manager = await create_hotel_manager()
    
    async def stop(self):
        """Cleanup resources"""
        if self.manager:
            await self.manager.close()
    
    async def process_command(self, command: str):
        """Process user commands"""
        # Your NLP logic here
        if "book" in command.lower():
            return await self._handle_booking(command)
        elif "check" in command.lower():
            return await self._handle_check(command)
        # ... more handlers
    
    async def _handle_booking(self, command: str):
        # Extract parameters from command
        # Call manager.book_room()
        pass

# Usage
agent = HotelAssistantAgent()
await agent.start()

try:
    response = await agent.process_command("Book room 101 for John")
    print(response)
finally:
    await agent.stop()
```

### Batch Operations

```python
async def process_multiple_bookings(booking_requests: list):
    """Process multiple bookings efficiently"""
    manager = await create_hotel_manager()
    results = []
    
    try:
        for request in booking_requests:
            try:
                booking = await manager.book_room(**request)
                results.append({"status": "success", "booking": booking})
            except ValueError as e:
                results.append({"status": "error", "message": str(e)})
        
        return results
    
    finally:
        await manager.close()
```

### Error Handling

```python
async def safe_booking(room_number: int, **kwargs):
    """Booking with comprehensive error handling"""
    manager = await create_hotel_manager()
    
    try:
        # Validate inputs
        if room_number <= 0:
            return {"error": "Invalid room number"}
        
        # Check availability first
        if not await manager.is_room_available(room_number):
            return {"error": f"Room {room_number} is already booked"}
        
        # Attempt booking
        booking = await manager.book_room(room_number=room_number, **kwargs)
        return {"success": True, "booking": booking}
    
    except ValueError as e:
        return {"error": f"Validation error: {str(e)}"}
    
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
    
    finally:
        await manager.close()
```

## Response Formats

### Success Response

```python
{
    "status": "success",
    "data": {
        "id": 1,
        "room_number": 101,
        "customer_name": "John Doe",
        "total_fare": 2700.00,
        # ... more fields
    }
}
```

### Error Response

```python
{
    "status": "error",
    "message": "Room 101 is already booked",
    "code": "ROOM_UNAVAILABLE"
}
```

## Integration Examples

### With LangChain

```python
from langchain.tools import Tool
from src.api import create_hotel_manager

async def book_room_tool(input_str: str):
    """LangChain tool for booking rooms"""
    # Parse input_str to extract parameters
    manager = await create_hotel_manager()
    try:
        booking = await manager.book_room(...)
        return f"Booked successfully: {booking}"
    finally:
        await manager.close()

# Create LangChain tool
booking_tool = Tool(
    name="BookHotelRoom",
    func=book_room_tool,
    description="Books a hotel room. Input: room_number, customer_name, days"
)
```

### With OpenAI Function Calling

```python
import openai
import json

# Define function schema
functions = [
    {
        "name": "book_room",
        "description": "Book a hotel room",
        "parameters": {
            "type": "object",
            "properties": {
                "room_number": {"type": "integer"},
                "customer_name": {"type": "string"},
                "customer_address": {"type": "string"},
                "customer_phone": {"type": "string"},
                "days_of_stay": {"type": "integer"}
            },
            "required": ["room_number", "customer_name", "customer_address", "customer_phone", "days_of_stay"]
        }
    }
]

async def execute_function(function_name: str, arguments: dict):
    """Execute the called function"""
    manager = await create_hotel_manager()
    
    try:
        if function_name == "book_room":
            result = await manager.book_room(**arguments)
            return json.dumps(result)
    finally:
        await manager.close()
```

### With Rasa

```python
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import asyncio

class ActionBookRoom(Action):
    def name(self):
        return "action_book_room"
    
    def run(self, dispatcher, tracker, domain):
        # Extract entities
        room_number = tracker.get_slot("room_number")
        customer_name = tracker.get_slot("customer_name")
        
        # Call async function
        result = asyncio.run(self._book_room(room_number, customer_name))
        
        dispatcher.utter_message(text=result)
        return []
    
    async def _book_room(self, room_number, customer_name):
        manager = await create_hotel_manager()
        try:
            booking = await manager.book_room(
                room_number=room_number,
                customer_name=customer_name,
                # ... other params
            )
            return f"Booked room {booking['room_number']}"
        finally:
            await manager.close()
```

## Best Practices for AI Agents

1. **Always close the manager**: Use try/finally blocks
2. **Handle errors gracefully**: Catch ValueError for business logic errors
3. **Validate inputs**: Check parameters before calling API
4. **Use type hints**: Helps with code generation and validation
5. **Cache manager**: For long-running agents, reuse the manager instance
6. **Log operations**: Track what the agent does for debugging
7. **Provide feedback**: Return clear success/error messages
8. **Check availability**: Before booking, verify room is available
9. **Use transactions**: Operations are atomic by default
10. **Test thoroughly**: Use mock data for testing

## Testing Your Agent

```python
import pytest
from src.api import create_hotel_manager

@pytest.mark.asyncio
async def test_agent_booking():
    """Test AI agent booking flow"""
    manager = await create_hotel_manager("sqlite+aiosqlite:///:memory:")
    
    try:
        # Test booking
        booking = await manager.book_room(
            room_number=101,
            customer_name="Test User",
            customer_address="Test Address",
            customer_phone="123-456-7890",
            days_of_stay=2
        )
        
        assert booking['room_number'] == 101
        assert booking['customer_name'] == "Test User"
        
        # Test availability check
        available = await manager.is_room_available(101)
        assert not available
        
    finally:
        await manager.close()
```

## Troubleshooting

### Common Issues

1. **"Database manager not initialized"**
   - Solution: Call `await manager.initialize()` or use `create_hotel_manager()`

2. **"Room already booked"**
   - Solution: Check availability first with `is_room_available()`

3. **"Validation error"**
   - Solution: Ensure all required fields are provided and valid

4. **"Session closed"**
   - Solution: Don't reuse manager after calling `close()`

## Support

For more examples, see [`example_usage.py`](example_usage.py) in the project root.

For architecture details, see [`ARCHITECTURE.md`](ARCHITECTURE.md).