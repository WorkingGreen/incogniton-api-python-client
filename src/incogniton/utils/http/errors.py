class IncognitonError(Exception):
    """Base exception for Incogniton errors."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)

class IncognitonAPIError(IncognitonError):
    """Exception raised for API-specific errors."""
    pass

class IncognitonConnectionError(IncognitonError):
    """Exception raised for connection errors."""
    pass

class IncognitonTimeoutError(IncognitonError):
    """Exception raised for timeout errors."""
    pass

class IncognitonValidationError(IncognitonError):
    """Exception raised for validation errors."""
    pass

# Removed unnecessary error classes:
# - IncognitonAPIError
# - IncognitonConnectionError
# - IncognitonTimeoutError
# - IncognitonValidationError 