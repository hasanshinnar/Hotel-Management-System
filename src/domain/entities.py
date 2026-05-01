"""
Domain entities representing core business objects
Following Domain-Driven Design principles
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Booking:
    """
    Domain entity representing a hotel room booking
    
    This is a pure domain object with business logic and validation,
    independent of database implementation (following DDD principles).
    """
    room_number: int
    customer_name: str
    customer_address: str
    customer_phone: str
    days_of_stay: int
    daily_rate: Decimal = Decimal("900.00")
    id: Optional[int] = None
    total_fare: Optional[Decimal] = None
    check_in_date: datetime = field(default_factory=datetime.utcnow)
    check_out_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Calculate total fare after initialization"""
        if self.total_fare is None:
            self.calculate_total_fare()
        self.validate()
    
    def calculate_total_fare(self) -> Decimal:
        """Calculate and set the total fare based on days and daily rate"""
        self.total_fare = Decimal(str(self.days_of_stay)) * self.daily_rate
        return self.total_fare
    
    def validate(self) -> None:
        """Validate booking data"""
        if self.room_number <= 0:
            raise ValueError("Room number must be positive")
        
        if not self.customer_name or not self.customer_name.strip():
            raise ValueError("Customer name is required")
        
        if not self.customer_phone or not self.customer_phone.strip():
            raise ValueError("Customer phone is required")
        
        if self.days_of_stay <= 0:
            raise ValueError("Days of stay must be positive")
        
        if self.daily_rate <= 0:
            raise ValueError("Daily rate must be positive")
    
    def update_details(
        self,
        customer_name: Optional[str] = None,
        customer_address: Optional[str] = None,
        customer_phone: Optional[str] = None,
        days_of_stay: Optional[int] = None,
    ) -> None:
        """Update booking details and recalculate fare if needed"""
        if customer_name is not None:
            self.customer_name = customer_name
        
        if customer_address is not None:
            self.customer_address = customer_address
        
        if customer_phone is not None:
            self.customer_phone = customer_phone
        
        if days_of_stay is not None:
            self.days_of_stay = days_of_stay
            self.calculate_total_fare()
        
        self.updated_at = datetime.utcnow()
        self.validate()
    
    def checkout(self) -> None:
        """Mark booking as checked out"""
        self.is_active = False
        self.check_out_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert booking to dictionary representation"""
        return {
            "id": self.id,
            "room_number": self.room_number,
            "customer_name": self.customer_name,
            "customer_address": self.customer_address,
            "customer_phone": self.customer_phone,
            "days_of_stay": self.days_of_stay,
            "daily_rate": float(self.daily_rate),
            "total_fare": float(self.total_fare) if self.total_fare else 0.0,
            "check_in_date": self.check_in_date.isoformat(),
            "check_out_date": self.check_out_date.isoformat() if self.check_out_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Booking':
        """Create booking from dictionary representation"""
        return cls(
            id=data.get("id"),
            room_number=data["room_number"],
            customer_name=data["customer_name"],
            customer_address=data["customer_address"],
            customer_phone=data["customer_phone"],
            days_of_stay=data["days_of_stay"],
            daily_rate=Decimal(str(data.get("daily_rate", "900.00"))),
            total_fare=Decimal(str(data["total_fare"])) if data.get("total_fare") else None,
            check_in_date=datetime.fromisoformat(data["check_in_date"]) if isinstance(data.get("check_in_date"), str) else data.get("check_in_date", datetime.utcnow()),
            check_out_date=datetime.fromisoformat(data["check_out_date"]) if data.get("check_out_date") else None,
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.utcnow()),
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data.get("updated_at"), str) else data.get("updated_at", datetime.utcnow()),
        )

# Made with Bob
