"""HTTP request logging middleware for core app."""

import logging
import time

logger = logging.getLogger("apps.core.middleware")


class RequestLogMiddleware:
    """Middleware that measures request execution duration and logs request summary.

    Logs: method, path, HTTP status, authenticated user ID (or 'anon'), and duration in ms.
    Never logs request bodies, query passwords, tokens, or session keys.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        response = None
        try:
            response = self.get_response(request)
            return response
        finally:
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            user_id = None
            user = getattr(request, "user", None)
            if user and getattr(user, "is_authenticated", False):
                user_id = getattr(user, "id", None) or getattr(user, "pk", None)

            status_code = response.status_code if response is not None else 500
            user_label = f"user_id={user_id}" if user_id is not None else "user_id=anon"

            logger.info(
                "%s %s %s %s duration_ms=%.2f",
                request.method,
                request.get_full_path(),
                status_code,
                user_label,
                duration_ms,
                extra={
                    "method": request.method,
                    "path": request.get_full_path(),
                    "status_code": status_code,
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                },
            )
