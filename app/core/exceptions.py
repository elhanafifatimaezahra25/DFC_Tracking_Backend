"""
Unified exception handling for the application.
"""
from fastapi import HTTPException, status
from typing import Any, Dict


class ValidationError(HTTPException):
    """Custom validation error."""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundError(HTTPException):
    """Resource not found error."""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )


class UnauthorizedError(HTTPException):
    """Unauthorized access error."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(HTTPException):
    """Forbidden access error."""
    def __init__(self, detail: str = "Not enough privileges"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class InternalServerError(HTTPException):
    """Internal server error."""
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


def error_response(status_code: int, message: str, error: str = None) -> Dict[str, Any]:
    """Format error responses."""
    return {
        "status": "error",
        "status_code": status_code,
        "message": message,
        "error": error
    }
