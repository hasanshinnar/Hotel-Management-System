"""
Configuration management for Hotel Management System
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
import os


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str = "sqlite+aiosqlite:///hotel_management.db"
    echo: bool = False
    pool_pre_ping: bool = True
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create configuration from environment variables"""
        return cls(
            url=os.getenv("DATABASE_URL", cls.url),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
            pool_pre_ping=os.getenv("DATABASE_POOL_PRE_PING", "true").lower() == "true",
        )


@dataclass
class HotelConfig:
    """Hotel business configuration"""
    default_daily_rate: Decimal = Decimal("900.00")
    hotel_name: str = "XYZ Group of Hotels"
    currency: str = "USD"
    
    @classmethod
    def from_env(cls) -> 'HotelConfig':
        """Create configuration from environment variables"""
        return cls(
            default_daily_rate=Decimal(os.getenv("DEFAULT_DAILY_RATE", "900.00")),
            hotel_name=os.getenv("HOTEL_NAME", cls.hotel_name),
            currency=os.getenv("CURRENCY", cls.currency),
        )


@dataclass
class AppConfig:
    """Application configuration"""
    database: DatabaseConfig
    hotel: HotelConfig
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        return cls(
            database=DatabaseConfig.from_env(),
            hotel=HotelConfig.from_env(),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )
    
    @classmethod
    def default(cls) -> 'AppConfig':
        """Create default configuration"""
        return cls(
            database=DatabaseConfig(),
            hotel=HotelConfig(),
            debug=False,
        )


# Global configuration instance
config = AppConfig.from_env()

# Made with Bob
