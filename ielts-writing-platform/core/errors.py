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
        """
        Create an APIError instance with standardized fields used for response generation.
        
        Parameters:
            code (ErrorCode): Standardized error code.
            message (str): Human-readable error message.
            status_code (int): HTTP status code for the error response. Defaults to 500.
            details (Optional[Dict[str, Any]]): Additional structured error details; defaults to an empty dict.
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
        """
        Initialize a validation-related API error with HTTP 400 status.
        
        Parameters:
            message (str): Human-readable error message describing the validation failure.
            code (ErrorCode): Specific validation error code; defaults to ErrorCode.VALIDATION_ERROR.
            details (Optional[Dict[str, Any]]): Optional structured details about the validation error (e.g., field errors).
        """
        super().__init__(code, message, 400, details)


class InvalidJSONError(ValidationError):
    """Invalid JSON error."""
    
    def __init__(self, message: str = "Invalid JSON format") -> None:
        """
        Error raised when a request contains malformed JSON.
        
        Initializes the exception with a human-readable message and sets the error code to ErrorCode.INVALID_JSON (HTTP 400 by default).
        
        Parameters:
            message (str): Description of the JSON error; defaults to "Invalid JSON format".
        """
        super().__init__(message, ErrorCode.INVALID_JSON)


class MissingFieldError(ValidationError):
    """Missing required field error."""
    
    def __init__(self, field_name: str) -> None:
        """
        Initialize a MissingFieldError for a required but absent field.
        
        Parameters:
            field_name (str): Name of the missing required field; included in the error message and details.
        
        Details:
            - Sets the error message to "Missing required field: {field_name}".
            - Populates `details` with {"field": field_name}.
            - Uses `ErrorCode.MISSING_FIELD` with HTTP status 400.
        """
        message = f"Missing required field: {field_name}"
        details = {"field": field_name}
        super().__init__(message, ErrorCode.MISSING_FIELD, details)


class InvalidFieldError(ValidationError):
    """Invalid field value error."""
    
    def __init__(self, field_name: str, reason: str) -> None:
        """
        Initialize an InvalidFieldError representing an invalid value for a specific field.
        
        Creates an error with a message describing the field and reason, and includes a details dict with keys "field" and "reason" for use in API responses.
        
        Parameters:
            field_name (str): Name of the field with the invalid value.
            reason (str): Human-readable explanation why the field value is invalid.
        """
        message = f"Invalid value for field '{field_name}': {reason}"
        details = {"field": field_name, "reason": reason}
        super().__init__(message, ErrorCode.INVALID_FIELD, details)


class MinWordCountError(APIError):
    """Minimum word count error (422)."""
    
    def __init__(self, required: int, actual: int) -> None:
        """
        Create a MinWordCountError indicating the essay is shorter than required.
        
        Parameters:
            required (int): Minimum required word count.
            actual (int): Actual word count provided.
        
        Description:
            Constructs the error message and details payload describing the required and actual word counts for response generation.
        """
        message = f"Essay must be at least {required} words. Current: {actual} words."
        details = {"required": required, "actual": actual}
        super().__init__(ErrorCode.MIN_WORD_COUNT, message, 422, details)


class DuplicateSubmissionError(APIError):
    """Duplicate submission error (422)."""
    
    def __init__(self, existing_attempt_id: str) -> None:
        """
        Initialize a DuplicateSubmissionError indicating a previously submitted attempt was found.
        
        Parameters:
        	existing_attempt_id (str): Identifier of the existing attempt; included in the error's `details` payload.
        
        Notes:
        	Sets the error code to `ErrorCode.DUPLICATE_SUBMISSION` and the HTTP status to 422.
        """
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
        """
        Initialize a NotFoundError for a specific resource type.
        
        Creates an error with message "<resource_type> not found", HTTP status 404, and a details dictionary containing the resource_type. The `code` parameter defaults to ErrorCode.NOT_FOUND and can be overridden.
        
        Parameters:
            resource_type (str): Name of the missing resource (used in message and details).
            code (ErrorCode): Optional error code to categorize the not-found error (defaults to ErrorCode.NOT_FOUND).
        """
        message = f"{resource_type} not found"
        details = {"resource_type": resource_type}
        super().__init__(code, message, 404, details)


class TaskNotFoundError(NotFoundError):
    """Task not found error."""
    
    def __init__(self) -> None:
        """
        Create a NotFoundError for a missing Task resource preconfigured with the TASK_NOT_FOUND code.
        
        This initializer constructs an error indicating a Task was not found and sets the error code to ErrorCode.TASK_NOT_FOUND and the HTTP status to 404.
        """
        super().__init__("Task", ErrorCode.TASK_NOT_FOUND)


class AttemptNotFoundError(NotFoundError):
    """Attempt not found error."""
    
    def __init__(self) -> None:
        """
        Create an AttemptNotFoundError for the missing "Attempt" resource.
        
        Preconfigures the error with resource_type "Attempt" and the ErrorCode.ATTEMPT_NOT_FOUND code.
        """
        super().__init__("Attempt", ErrorCode.ATTEMPT_NOT_FOUND)


class InvalidStatusTransitionError(APIError):
    """Invalid status transition error (422)."""
    
    def __init__(self, current_status: str, requested_action: str) -> None:
        """
        Indicates an invalid status transition for an entity.
        
        Parameters:
            current_status (str): The entity's current status.
            requested_action (str): The action attempted that is not allowed from the current status.
        
        Notes:
            Sets the exception's error code to `ErrorCode.INVALID_STATUS_TRANSITION`, the HTTP status code to 422, and `details` to include `current_status` and `requested_action`.
        """
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
        """
        Initialize an APIError representing a failure of the AI evaluation service.
        
        Creates an error with code ErrorCode.AI_SERVICE_ERROR, HTTP status 500, and details identifying the failing service.
        
        Parameters:
            message (str): Human-readable error message. Defaults to "AI evaluation service error".
        """
        details = {"service": "ai_evaluation"}
        super().__init__(ErrorCode.AI_SERVICE_ERROR, message, 500, details)


def error_response(
    error: APIError,
    request_id: Optional[str] = None,
) -> JsonResponse:
    """
    Format an APIError into a standardized JSON error response.
    
    Parameters:
        request_id (Optional[str]): Optional correlation ID to include at the top level for request tracing.
    
    Returns:
        JsonResponse: JSON object with the shape
            {
                "success": False,
                "error": {
                    "code": <error code string>,
                    "message": <error message>,
                    "details": <optional details dict>
                },
                "request_id": <optional request_id>
            }
        The HTTP status of the response is set to `error.status_code`.
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
    """
    Builds a standardized JSON success response for API endpoints.
    
    Parameters:
        data (Dict[str, Any]): Payload to include under the "data" key.
        status_code (int): HTTP status code for the response.
        request_id (Optional[str]): Optional request identifier to include at top level.
    
    Returns:
        JsonResponse: JSON object with shape {"success": True, "data": data, ("request_id": request_id)}, returned with the provided HTTP status code.
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
    """
    Constructs a standardized error JsonResponse from primitive error values.
    
    Args:
        code: ErrorCode to include in the response error payload.
        message: Human-readable error message.
        status_code: HTTP status code for the response.
        details: Optional map of additional error details to include under `error.details`.
        request_id: Optional request identifier to include at the top level of the response.
    
    Returns:
        JsonResponse: Response with structure {
            "success": False,
            "error": { "code": <code>, "message": <message>, (optional) "details": <details> },
            (optional) "request_id": <request_id>
        } and HTTP status set to `status_code`.
    """
    error = APIError(code, message, status_code, details)
    return error_response(error, request_id)