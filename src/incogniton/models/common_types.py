from typing import TypedDict, Optional, Generic, TypeVar, Union, Dict, Any, Protocol

# Add any common types that might be shared across different modules here
# For now it's empty as all types have been moved to their specific modules 

T = TypeVar('T')

class Timestamps(TypedDict):
    """Interface containing timestamp fields for creation and update times."""
    createdAt: str  # ISO 8601 timestamp when the resource was created
    updatedAt: str  # ISO 8601 timestamp when the resource was last updated

class BaseResponse(TypedDict):
    """Base response interface for all API responses."""
    status: int  # HTTP status code of the response
    message: Optional[str]  # Optional message describing the response

class ApiResponse(TypedDict):
    """Generic API response type."""
    status: int  # HTTP status code of the response
    message: Optional[str]  # Optional message describing the response
    data: Dict[str, Any]  # The actual response data

class ApiError(TypedDict):
    """API error response type."""
    status: int  # HTTP status code of the response
    message: Optional[str]  # Optional message describing the response
    error: str  # Error message or code 