"""Authentication and authorization decorators returning standardized JSON responses."""

import logging
from functools import wraps
from typing import Any, Callable, Optional, Sequence
from .http import json_error

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("apps.security")


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
            path = getattr(request, "path", "unknown")
            remote_addr = request.META.get("REMOTE_ADDR") if request and hasattr(request, "META") else "unknown"
            security_logger.warning("Unauthenticated access attempt to %s from IP %s", path, remote_addr)
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
                path = getattr(request, "path", "unknown")
                remote_addr = request.META.get("REMOTE_ADDR") if request and hasattr(request, "META") else "unknown"
                security_logger.warning(
                    "Unauthenticated access attempt to %s from IP %s (roles required: %s)",
                    path,
                    remote_addr,
                    allowed_roles,
                )
                return json_error("Authentication required.", status=401)

            user_role = getattr(request.user, "role", None)
            if user_role not in allowed_roles:
                path = getattr(request, "path", "unknown")
                security_logger.warning(
                    "Forbidden role access: user_id=%s role='%s' denied access to %s (allowed: %s)",
                    getattr(request.user, "id", None),
                    user_role,
                    path,
                    allowed_roles,
                )
                return json_error("Permission denied.", status=403)

            return view_func(*args, **kwargs)

        return _wrapped_view

    return decorator


def verified_required(
    view_func: Optional[Callable] = None,
    *,
    methods: Optional[Sequence[str]] = None,
) -> Callable:
    """
    Decorator for views that checks if the user is authenticated and has verified their email.
    Returns HTTP 401 if unauthenticated, and HTTP 403 if email is not verified.

    If `methods` is specified (e.g. methods=["POST"]), verification is only enforced
    for those HTTP methods. If omitted, verification is enforced for all methods.

    Usage:
        @verified_required
        def booking_create_view(request): ...

        @verified_required(methods=["POST"])
        def manager_hotels_list_create_view(request): ...
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def _wrapped_view(*args, **kwargs):
            request = _extract_request(args)
            if request is None or not getattr(request, "user", None) or not request.user.is_authenticated:
                path = getattr(request, "path", "unknown")
                remote_addr = request.META.get("REMOTE_ADDR") if request and hasattr(request, "META") else "unknown"
                security_logger.warning("Unauthenticated access attempt to %s from IP %s", path, remote_addr)
                return json_error("Authentication required.", status=401)

            method_match = True
            if methods is not None:
                req_method = getattr(request, "method", "").upper()
                method_match = req_method in [m.upper() for m in methods]

            if method_match and not getattr(request.user, "email_verified", False):
                path = getattr(request, "path", "unknown")
                security_logger.warning(
                    "Forbidden unverified access attempt: user_id=%s path=%s",
                    request.user.id,
                    path,
                )
                return json_error(
                    "Email verification required. Please verify your email address.",
                    status=403,
                )

            return fn(*args, **kwargs)

        return _wrapped_view

    if view_func is not None:
        return decorator(view_func)
    return decorator
