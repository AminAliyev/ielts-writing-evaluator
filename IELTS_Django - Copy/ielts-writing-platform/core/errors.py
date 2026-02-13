"""Error handling and response mapping for IELTS Writing Platform."""

from enum import Enum
from typing import Any, Dict, Optional
from django.http import JsonResponse


class ErrorCode(str, Enum):
    """Standard error codes for API responses."""
    
    # Validation errors (400)
    INVALID_JSON = 'invalid_json'
    INVALID_REQUEST = 'invalid_request'
    MISSING_FIELD = 'missing_field'
    INVALID_FIELD = 'invalid_field'
    VALIDATION_ERROR = 'validation_error'
    
    # Authentication errors (401)
    UNAUTHORIZED = 'unauthorized'
    INVALID_CREDENTIALS = 'invalid_credentials'
    
    # Permission errors (403)
    FORBIDDEN = 'forbidden'
    PERMISSION_DENIED = 'permission_denied'
    
    # Not found errors (404)
    NOT_FOUND = 'not_found'
    RESOURCE_NOT_FOUND = 'resource_not_found'
    TASK_NOT_FOUND = 'task_not_found'
    ATTEMPT_NOT_FOUND = 'attempt_not_found'
    
    # Conflict errors (422)
    UNPROCESSABLE_ENTITY = 'unprocessable_entity'
    MIN_WORD_COUNT = 'min_word_count'
    DUPLICATE_SUBMISSION = 'duplicate_submission'
    INVALID_STATUS_TRANSITION = 'invalid_status_transition'
    
    # Server errors (500)
    INTERNAL_ERROR = 'internal_error'
    DATABASE_ERROR = 'database_error'
    AI_SERVICE_ERROR = 'ai_service_error'
    EXTERNAL_SERVICE_ERROR = 'external_service_error'
    
    # Service unavailable (503)
    SERVICE_UNAVAILABLE = 'service_unavailable'
    MAINTENANCE = 'maintenance'


class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize API error.
        
        Args:
            code: Error code enum value.
            message: Human-readable error message.
            status_code: HTTP status code.
            details: Additional error details.
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error (400)."""
    
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(code, message, 400, details)


class InvalidJSONError(ValidationError):
    """Invalid JSON error."""
    
    def __init__(self, message: str = "Invalid JSON format") -> None:
        super().__init__(message, ErrorCode.INVALID_JSON)


class MissingFieldError(ValidationError):
    """Missing required field error."""
    
    def __init__(self, field_name: str) -> None:
        message = f"Missing required field: {field_name}"
        details = {"field": field_name}
        super().__init__(message, ErrorCode.MISSING_FIELD, details)


class InvalidFieldError(ValidationError):
    """Invalid field value error."""
    
    def __init__(self, field_name: str, reason: str) -> None:
        message = f"Invalid value for field '{field_name}': {reason}"
        details = {"field": field_name, "reason": reason}
        super().__init__(message, ErrorCode.INVALID_FIELD, details)


class MinWordCountError(APIError):
    """Minimum word count error (422)."""
    
    def __init__(self, required: int, actual: int) -> None:
        message = f"Essay must be at least {required} words. Current: {actual} words."
        details = {"required": required, "actual": actual}
        super().__init__(ErrorCode.MIN_WORD_COUNT, message, 422, details)


class DuplicateSubmissionError(APIError):
    """Duplicate submission error (422)."""
    
    def __init__(self, existing_attempt_id: str) -> None:
        message = "Duplicate submission detected"
        details = {"existing_attempt_id": existing_attempt_id}
        super().__init__(
            ErrorCode.DUPLICATE_SUBMISSION,
            message,
            422,
            details,
        )


class NotFoundError(APIError):
    """Resource not found error (404)."""
    
    def __init__(
        self,
        resource_type: str,
        code: ErrorCode = ErrorCode.NOT_FOUND,
    ) -> None:
        message = f"{resource_type} not found"
        details = {"resource_type": resource_type}
        super().__init__(code, message, 404, details)


class TaskNotFoundError(NotFoundError):
    """Task not found error."""
    
    def __init__(self) -> None:
        super().__init__("Task", ErrorCode.TASK_NOT_FOUND)


class AttemptNotFoundError(NotFoundError):
    """Attempt not found error."""
    
    def __init__(self) -> None:
        super().__init__("Attempt", ErrorCode.ATTEMPT_NOT_FOUND)


class InvalidStatusTransitionError(APIError):
    """Invalid status transition error (422)."""
    
    def __init__(self, current_status: str, requested_action: str) -> None:
        message = f"Cannot {requested_action} when status is {current_status}"
        details = {
            "current_status": current_status,
            "requested_action": requested_action,
        }
        super().__init__(
            ErrorCode.INVALID_STATUS_TRANSITION,
            message,
            422,
            details,
        )


class AIServiceError(APIError):
    """AI service error (500)."""
    
    def __init__(self, message: str = "AI evaluation service error") -> None:
        details = {"service": "ai_evaluation"}
        super().__init__(ErrorCode.AI_SERVICE_ERROR, message, 500, details)


def error_response(
    error: APIError,
    request_id: Optional[str] = None,
) -> JsonResponse:
    """Convert API error to JSON response.
    
    Args:
        error: The API error instance.
        request_id: Optional request ID for tracking.
        
    Returns:
        JSON response with error details.
    """
    response_data: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": error.code.value,
            "message": error.message,
        },
    }
    
    if error.details:
        response_data["error"]["details"] = error.details
    
    if request_id:
        response_data["request_id"] = request_id
    
    return JsonResponse(response_data, status=error.status_code)


def success_response(
    data: Dict[str, Any],
    status_code: int = 200,
    request_id: Optional[str] = None,
) -> JsonResponse:
    """Create standardized success JSON response.
    
    Args:
        data: Response data.
        status_code: HTTP status code.
        request_id: Optional request ID for tracking.
        
    Returns:
        JSON response with data.
    """
    response_data: Dict[str, Any] = {
        "success": True,
        "data": data,
    }
    
    if request_id:
        response_data["request_id"] = request_id
    
    return JsonResponse(response_data, status=status_code)


def get_error_response(
    code: ErrorCode,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> JsonResponse:
    """Create error response directly from parameters.
    
    Args:
        code: Error code.
        message: Error message.
        status_code: HTTP status code.
        details: Additional error details.
        request_id: Optional request ID for tracking.
        
    Returns:
        JSON response with error details.
    """
    error = APIError(code, message, status_code, details)
    return error_response(error, request_id)
