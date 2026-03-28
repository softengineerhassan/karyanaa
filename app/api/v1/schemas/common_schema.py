
from typing import Optional, Generic, TypeVar, List, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============================================
# Base Response Models
# ============================================

T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    
    success: bool = Field(True, description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Human-readable message")
    data: Optional[T] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="List of error messages")
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    errors: Optional[List[str]] = Field(None, description="Detailed error messages")
    details: Optional[dict] = Field(None, description="Additional error details")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Pagination Models
# ============================================

class PaginationParams(BaseModel):
    
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class PaginationMeta(BaseModel):
    
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    
    success: bool = Field(True, description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Human-readable message")
    data: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    summary: Optional[Any] = Field(None, description="Optional summary data")
    stats: Optional[Any] = Field(None, description="Optional statistics data")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Base Entity Schemas
# ============================================

class BaseSchema(BaseModel):
    
    id: UUID = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )


class TimestampSchema(BaseModel):
    
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Filter & Sort Models
# ============================================

class SortOrder(str):
    ASC = "asc"
    DESC = "desc"


class FilterParams(BaseModel):
    
    search: Optional[str] = Field(None, description="Search query")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    created_from: Optional[datetime] = Field(None, description="Filter from creation date")
    created_to: Optional[datetime] = Field(None, description="Filter to creation date")


class SortParams(BaseModel):
    
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")


# ============================================
# ID Response Models
# ============================================

class IDResponse(BaseModel):
    
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class BulkIDResponse(BaseModel):
    
    ids: List[UUID] = Field(..., description="List of affected IDs")
    count: int = Field(..., description="Number of affected records")


# ============================================
# Status Response Models
# ============================================

class StatusResponse(BaseModel):
    
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Status message")


class HealthResponse(BaseModel):
    
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    checks: Optional[dict] = Field(None, description="Individual health checks")


# ============================================
# Message Response Models
# ============================================

class MessageResponse(BaseModel):
    
    message: str = Field(..., description="Response message")


class SuccessResponse(BaseModel):
    
    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
