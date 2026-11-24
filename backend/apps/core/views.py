"""Core views including health check, CSRF token endpoint, SPA host view, and custom error handlers."""

import logging
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from .http import json_error, json_ok

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("apps.security")


@require_GET
def health_check(request):
    """Health check endpoint returning {"data": {"status": "ok"}}."""
    return json_ok({"status": "ok"})


@require_GET
@ensure_csrf_cookie
def csrf_token_view(request):
    """
    Ensure the CSRF cookie is set and return the token in JSON envelope.
    Path: /api/auth/csrf/
    """
    token = get_token(request)
    return json_ok({"csrfToken": token})


@require_GET
@ensure_csrf_cookie
def spa_host_view(request, *args, **kwargs):
    """
    Renders the Single Page Application index.html host template
    for client-side routing.
    """
    return render(request, "index.html")


def bad_request_view(request, exception=None):
    """Custom 400 handler returning JSON for /api/ paths."""
    if request.path.startswith("/api/"):
        logger.warning("Bad request on %s: %s", request.path, exception)
        return json_error("Bad request.", status=400)
    from django.views.defaults import bad_request
    return bad_request(request, exception)


def permission_denied_view(request, exception=None):
    """Custom 403 handler returning JSON for /api/ paths."""
    if request.path.startswith("/api/"):
        security_logger.warning("Permission denied on %s: %s", request.path, exception)
        return json_error("Permission denied.", status=403)
    from django.views.defaults import permission_denied
    return permission_denied(request, exception)


def page_not_found_view(request, exception=None):
    """Custom 404 handler returning JSON for /api/ paths."""
    if request.path.startswith("/api/"):
        logger.info("Resource not found on %s: %s", request.path, exception)
        return json_error("Resource not found.", status=404)
    from django.views.defaults import page_not_found
    return page_not_found(request, exception)


def server_error_view(request):
    """Custom 500 handler returning JSON for /api/ paths."""
    if request.path.startswith("/api/"):
        logger.error("Internal server error on %s", request.path, exc_info=True)
        return json_error("Internal server error.", status=500)
    from django.views.defaults import server_error
    return server_error(request)
