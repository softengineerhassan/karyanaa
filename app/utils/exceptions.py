
from typing import Any, Optional, Dict


class AuthServiceException(Exception):
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ============================================
# Authentication Exceptions
# ============================================

class InvalidCredentialsError(AuthServiceException):
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, status_code=401)


class InvalidTokenError(AuthServiceException):
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, status_code=401)


class ExpiredTokenError(AuthServiceException):
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, status_code=401)


class RevokedTokenError(AuthServiceException):
    
    def __init__(self, message: str = "Token has been revoked"):
        super().__init__(message, status_code=401)


class MissingTokenError(AuthServiceException):
    
    def __init__(self, message: str = "Authorization token is required"):
        super().__init__(message, status_code=401)


# ============================================
# User Account Exceptions
# ============================================

class UserNotFoundError(AuthServiceException):
    
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404)


class UserAlreadyExistsError(AuthServiceException):
    
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message, status_code=409)


class UserInactiveError(AuthServiceException):
    
    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message, status_code=403)


class UserLockedError(AuthServiceException):
    
    def __init__(self, message: str = "Account is locked. Please try again later or reset your password"):
        super().__init__(message, status_code=403)


class EmailNotVerifiedError(AuthServiceException):
    
    def __init__(self, message: str = "Email verification required"):
        super().__init__(message, status_code=403, details={"is_verified": False})


# ============================================
# Password Exceptions
# ============================================

class WeakPasswordError(AuthServiceException):
    
    def __init__(self, message: str = "Password does not meet security requirements"):
        super().__init__(message, status_code=400)


class PasswordResetTokenInvalidError(AuthServiceException):
    
    def __init__(self, message: str = "Invalid or expired password reset token"):
        super().__init__(message, status_code=400)


class PasswordResetTokenUsedError(AuthServiceException):
    
    def __init__(self, message: str = "Password reset token has already been used"):
        super().__init__(message, status_code=400)


# ============================================
# Permission & Authorization Exceptions
# ============================================

class PermissionDeniedError(AuthServiceException):
    
    def __init__(self, message: str = "Permission denied", required_permission: Optional[str] = None):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, status_code=403, details=details)




class RoleNotFoundError(AuthServiceException):
    
    def __init__(self, message: str = "Role not found"):
        super().__init__(message, status_code=404)


class PermissionNotFoundError(AuthServiceException):
    
    def __init__(self, message: str = "Permission not found"):
        super().__init__(message, status_code=404)


class SystemRoleModificationError(AuthServiceException):
    
    def __init__(self, message: str = "Cannot modify system role"):
        super().__init__(message, status_code=403)


# Validation Exceptions
# ============================================

class ValidationError(AuthServiceException):
    
    def __init__(self, message: str = "Validation error", errors: Optional[list] = None):
        details = {}
        if errors:
            details["validation_errors"] = errors
        super().__init__(message, status_code=422, details=details)


class InvalidEmailError(AuthServiceException):
    
    def __init__(self, message: str = "Invalid email format"):
        super().__init__(message, status_code=400)


class EmailVerificationTokenInvalidError(AuthServiceException):
    
    def __init__(self, message: str = "Invalid or expired email verification token"):
        super().__init__(message, status_code=400)


# ============================================
# Rate Limiting Exceptions
# ============================================

class RateLimitExceededError(AuthServiceException):
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(message, status_code=429, details=details)


# ============================================
# Entity-Specific Exceptions
# ============================================

class ModuleNotFoundError(AuthServiceException):
    
    def __init__(self, message: str = "Module not found"):
        super().__init__(message, status_code=404)


class VenueNotFoundError(AuthServiceException):
    
    def __init__(self, message: str = "Venue not found"):
        super().__init__(message, status_code=404)


class ModuleNameExistsError(AuthServiceException):
    
    def __init__(self, module_name: str):
        message = f"Module with name '{module_name}' already exists"
        super().__init__(message, status_code=400)


class PermissionNameExistsError(AuthServiceException):
    
    def __init__(self, permission_name: str):
        message = f"Permission with name '{permission_name}' already exists"
        super().__init__(message, status_code=400)


class PermissionResourceActionExistsError(AuthServiceException):
    
    def __init__(self, resource: str, action: str):
        message = f"Permission with resource '{resource}' and action '{action}' already exists"
        super().__init__(message, status_code=400)


class RoleNameExistsError(AuthServiceException):
    
    def __init__(self, role_name: str):
        message = f"Role with name '{role_name}' already exists"
        super().__init__(message, status_code=400)


# ============================================
# External Service Exceptions
# ============================================

class EmailSendError(AuthServiceException):
    
    def __init__(self, message: str = "Failed to send email"):
        super().__init__(message, status_code=500)


class KafkaPublishError(AuthServiceException):
    
    def __init__(self, message: str = "Failed to publish event"):
        super().__init__(message, status_code=500)


class CacheError(AuthServiceException):
    
    def __init__(self, message: str = "Cache operation failed"):
        super().__init__(message, status_code=500)


# ============================================
# Database Exceptions
# ============================================

class DatabaseError(AuthServiceException):
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class DuplicateRecordError(AuthServiceException):
    
    def __init__(self, message: str = "Record already exists"):
        super().__init__(message, status_code=409)


class RecordNotFoundError(AuthServiceException):
    
    def __init__(self, message: str = "Record not found"):
        super().__init__(message, status_code=404)


# ============================================
# Configuration Exceptions
# ============================================

class ConfigurationError(AuthServiceException):
    
    def __init__(self, message: str = "Configuration error"):
        super().__init__(message, status_code=500)


class KeyLoadError(AuthServiceException):
    
    def __init__(self, message: str = "Failed to load RSA keys"):
        super().__init__(message, status_code=500)


class CategoryNotFoundError(Exception):
    pass


class CategoryNameExistsError(Exception):
    def __init__(self):
        super().__init__("Category name already exists")


class ModuleNotFoundError(Exception):
    pass


class ModuleNameExistsError(Exception):
    def __init__(self, name: str):
        super().__init__(f"Module with name '{name}' already exists")

class SubCategoryError(Exception):
    """Base exception for subcategory related errors."""
    pass


class SubCategoryNotFoundError(SubCategoryError):
    """Raised when a subcategory is not found."""
    def __init__(self, message: str = "Subcategory not found"):
        super().__init__(message)


class SubCategoryNameExistsError(SubCategoryError):
    """Raised when a subcategory name already exists in the same category."""
    def __init__(
        self,
        message: str = "Subcategory name already exists in this category"
    ):
        super().__init__(message)

class ResourceNotFoundError(Exception):
    """Raised when a resource is not found"""
    pass

class PerkNotFoundError(Exception):
    pass

class PerkNameExistsError(Exception):
    pass

class VenuePerkNotFoundError(Exception):
    pass

class VenuePerkLimitError(Exception):
    pass

class InactivePerkError(Exception):
    pass

class PricingNotFoundError(Exception):
    def __init__(self, message: str = "Pricing not found"):
        super().__init__(message)


class PricingNameExistsError(Exception):
    def __init__(self, message: str = "Pricing already exists"):
        super().__init__(message)




class BookingNotFoundError(Exception):
    """Raised when a booking is not found"""
    pass

# ==============================
# Booking Exceptions
# ==============================

class BookingError(AuthServiceException):
    """Base class for booking-related errors."""
    def __init__(self, message: str = "Booking error", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=status_code, details=details)


class BookingNotFoundError(BookingError):
    """Raised when a booking is not found."""
    def __init__(self, message: str = "Booking not found"):
        super().__init__(message, status_code=404)


class BookingValidationError(BookingError):
    """Raised when booking validation fails."""
    def __init__(self, message: str = "Booking validation error"):
        super().__init__(message, status_code=400)


class BookingConflictError(BookingError):
    """Raised when booking time slot conflicts."""
    pass


class InvalidQRTokenError(BookingError):
    """Raised when QR token is invalid or malformed."""
    pass


class ExpiredQRTokenError(BookingError):
    """Raised when QR token has expired."""
    pass


class UnauthorizedVenueAccessError(BookingError):
    """Raised when staff tries to access booking from unauthorized venue."""
    pass

