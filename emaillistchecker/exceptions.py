"""EmailListChecker SDK Exceptions"""


class EmailListCheckerException(Exception):
    """Base exception for EmailListChecker SDK"""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(EmailListCheckerException):
    """Raised when API authentication fails"""
    pass


class InsufficientCreditsError(EmailListCheckerException):
    """Raised when account has insufficient credits"""
    pass


class RateLimitError(EmailListCheckerException):
    """Raised when API rate limit is exceeded"""
    pass


class ValidationError(EmailListCheckerException):
    """Raised when request validation fails"""
    pass


class APIError(EmailListCheckerException):
    """Raised for general API errors"""
    pass
