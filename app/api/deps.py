from fastapi import Request

from app.domain.errors import UnauthorizedError


def current_user_id(request: Request) -> int:
    """Educational authentication: the user id is passed in the X-User-Id header."""
    raw = request.headers.get("X-User-Id")
    if raw is None or not raw.isdigit():
        raise UnauthorizedError("X-User-Id header is required")
    user = request.app.state.container.users.get(int(raw))
    if user is None:
        raise UnauthorizedError("unknown user")
    return user.id
