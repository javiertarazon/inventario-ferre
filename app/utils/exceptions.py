"""
Custom exception hierarchy for the application.
Provides structured error handling with consistent error codes and messages.
"""
from typing import Any, Optional
from datetime import datetime


class ApplicationError(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, code: str, status_code: int = 500):
        """
        Initialize application error.
        
        Args:
            message: Human-readable error message
            code: Machine-readable error code
            status_code: HTTP status code
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """
        Convert error to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            'code': self.code,
            'message': self.message,
            'status': self.status_code,
            'timestamp': self.timestamp
        }


class ValidationError(ApplicationError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        """
        Initialize validation error.
        
        Args:
            message: Validation error message
            field: Field name that failed validation (optional)
        """
        super().__init__(message, 'VALIDATION_ERROR', 400)
        self.field = field
    
    def to_dict(self) -> dict:
        """Include field information in error dict."""
        error_dict = super().to_dict()
        if self.field:
            error_dict['field'] = self.field
        return error_dict


class NotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: Any):
        """
        Initialize not found error.
        
        Args:
            resource: Type of resource (e.g., 'Product', 'Supplier')
            identifier: Resource identifier that was not found
        """
        message = f"{resource} con identificador '{identifier}' no encontrado"
        super().__init__(message, 'NOT_FOUND', 404)
        self.resource = resource
        self.identifier = identifier


class AuthenticationError(ApplicationError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Autenticación fallida"):
        """
        Initialize authentication error.
        
        Args:
            message: Authentication error message
        """
        super().__init__(message, 'AUTH_ERROR', 401)


class AuthorizationError(ApplicationError):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Permisos insuficientes"):
        """
        Initialize authorization error.
        
        Args:
            message: Authorization error message
        """
        super().__init__(message, 'AUTHZ_ERROR', 403)


class DatabaseError(ApplicationError):
    """Raised when a database operation fails."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize database error.
        
        Args:
            message: Database error message
            original_error: Original exception that caused the error
        """
        super().__init__(message, 'DB_ERROR', 500)
        self.original_error = original_error


class BusinessLogicError(ApplicationError):
    """Raised when business logic validation fails."""
    
    def __init__(self, message: str):
        """
        Initialize business logic error.
        
        Args:
            message: Business logic error message
        """
        super().__init__(message, 'BUSINESS_LOGIC_ERROR', 422)


class FileUploadError(ApplicationError):
    """Raised when file upload fails."""
    
    def __init__(self, message: str):
        """
        Initialize file upload error.
        
        Args:
            message: File upload error message
        """
        super().__init__(message, 'FILE_UPLOAD_ERROR', 400)


class ConfigurationError(ApplicationError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str):
        """
        Initialize configuration error.
        
        Args:
            message: Configuration error message
        """
        super().__init__(message, 'CONFIG_ERROR', 500)
