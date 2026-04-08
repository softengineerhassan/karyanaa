from enum import Enum


class UserRoleFilter(str, Enum):
    """Enum for filtering users by role"""
    CUSTOMER = "customer"
    VENDOR = "vendor"
    STAFF = "staff"
    ADMIN = "admin"


class UserStatusFilter(str, Enum):
    """Enum for filtering users by status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ALL = "all"


class UserSegment(str, Enum):
    """Enum for filtering users by segment"""
    NEW = "new"
    ACTIVE = "active"
    VIP = "vip"
    ALL = "all"










