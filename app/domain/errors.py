class DomainError(Exception):
    """Base class for business rule violations."""

    code = "DOMAIN_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidIntervalError(DomainError):
    code = "INVALID_INTERVAL"
