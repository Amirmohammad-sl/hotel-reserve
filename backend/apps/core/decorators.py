"""Authentication and authorization decorators returning standardized JSON responses."""

from functools import wraps
from typing import Any, Callable, Sequence
from .http import json_error


def _extract_request(args: Sequence[Any]):
    """Extract HttpRequest object whether used on a function view or a CBV method."""
    if len(args) > 0 and hasattr(args[0], "user"):
        return args[0]
    if len(args) > 1 and hasattr(args[1], "user"):
        return args[1]
    return args[0] if len(args) > 0 else None


def login_required_json(view_func: Callable) -> Callable:
    """
    Decorator for views that checks if the user is authenticated.
    Returns HTTP 401 JSON error if user is unauthenticated.
    """
    @wraps(view_func)
    def _wrapped_view(*args, **kwargs):
        request = _extract_request(args)
        if request is None or not getattr(request, "user", None) or not request.user.is_authenticated:
            return json_error("Authentication required.", status=401)
        return view_func(*args, **kwargs)

    return _wrapped_view


def role_required(*allowed_roles: str) -> Callable:
    """
    Decorator for views that checks if the user is authenticated and has one of the allowed roles.
    Returns HTTP 401 if unauthenticated, and HTTP 403 if role is not permitted.

    Usage:
        @role_required("manager")
        @role_required("manager", "guest")
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            request = _extract_request(args)
            if request is None or not getattr(request, "user", None) or not request.user.is_authenticated:
                return json_error("Authentication required.", status=401)

            user_role = getattr(request.user, "role", None)
            if user_role not in allowed_roles:
                return json_error("Permission denied.", status=403)

            return view_func(*args, **kwargs)

        return _wrapped_view

    return decorator
