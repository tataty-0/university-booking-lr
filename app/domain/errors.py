class DomainError(Exception):
    """Base class for business rule violations."""

    code = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidIntervalError(DomainError):
    code = "INVALID_INTERVAL"
    status_code = 422


class NotFoundError(DomainError):
    code = "NOT_FOUND"
    status_code = 404


class SlotConflictError(DomainError):
    code = "SLOT_CONFLICT"
    status_code = 409


class ForbiddenError(DomainError):
    code = "FORBIDDEN"
    status_code = 403


class UnauthorizedError(DomainError):
    code = "UNAUTHORIZED"
    status_code = 401


class InvalidTransitionError(DomainError):
    code = "INVALID_TRANSITION"
    status_code = 409
