"""Role enums for authentication."""

from enum import Enum
from typing import List

class UserRole(str, Enum):
    """Enum for user roles."""
    CLIENT = "client"
    ADMIN = "admin"
    ANALYST = "analyst"