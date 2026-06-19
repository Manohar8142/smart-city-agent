"""
Custom exception classes for the Smart City Agent.
Why custom exceptions?
- Better error handling granularity
- Easier debugging (specific error types)
- Can attach metadata to exceptions
- Cleaner code (catch specific errors)
"""

class SmartCityError(Exception):
    """Base exception for all Smart City Agent errors."""
    def __init__(self, message:str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ToolExecutionError(SmartCityError):
    """Raised when a tool fails to execute"""
    pass

class ValidationError(SmartCityError):
    """Raised when input validation fails"""
    pass

class ConfigurationError(SmartCityError):
    """Raised when there is a configuration issue"""
    pass

class ExternalAPIError(SmartCityError):
    """Raised when an external API call fails"""
    def __init__(self, message:str, api_name:str, status_code: int | None = None):
        self.api_name = api_name
        self.status_code = status_code
        super().__init__(
            message,
            details = {
                "api": api_name,
                "status_code": status_code
            }
        )