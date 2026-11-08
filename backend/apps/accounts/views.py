"""Authentication views returning standard JSON responses."""

import logging
from django.contrib.auth import login, logout
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from apps.core.decorators import login_required_json
from apps.core.forms import form_errors
from apps.core.http import json_error, json_ok, parse_json
from .forms import LoginForm, RegisterForm, user_to_dict

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("apps.security")


def _extract_request_data(request: HttpRequest):
    """Extract dict payload from JSON body or POST form data."""
    if request.content_type == "application/json" or request.body:
        try:
            return parse_json(request)
        except ValueError:
            return None
    return request.POST.dict()


@require_POST
def register_view(request: HttpRequest) -> HttpResponse:
    """
    POST /api/auth/register/
    Register a new user account.
    Returns 201 with user object on success, 400 with field errors on validation failure.
    """
    data = _extract_request_data(request)
    if data is None:
        logger.warning("Registration failed: Invalid JSON payload from IP %s", request.META.get("REMOTE_ADDR"))
        return json_error("Invalid JSON body.", status=400)

    form = RegisterForm(data=data)
    if form.is_valid():
        user = form.save()
        security_logger.info(
            "User registered successfully: user_id=%s username=%s role=%s email=%s",
            user.id,
            user.username,
            user.role,
            user.email,
        )
        return json_ok(user_to_dict(user), status=201)

    logger.warning(
        "Registration validation failed for username=%s email=%s: %s",
        data.get("username"),
        data.get("email"),
        form_errors(form),
    )
    return json_error("Validation failed.", errors=form_errors(form), status=400)


@require_POST
def login_view(request: HttpRequest) -> HttpResponse:
    """
    POST /api/auth/login/
    Authenticate user and initiate session.
    Returns 200 with user object on success, 400 with field errors on invalid credentials.
    """
    data = _extract_request_data(request)
    if data is None:
        logger.warning("Login failed: Invalid JSON payload from IP %s", request.META.get("REMOTE_ADDR"))
        return json_error("Invalid JSON body.", status=400)

    form = LoginForm(data=data, request=request)
    if form.is_valid():
        user = form.get_user()
        login(request, user)

        # Store last login time in session (P3-06)
        login_time = timezone.now().isoformat()
        request.session["last_login"] = login_time

        if form.cleaned_data.get("remember_me"):
            request.session.set_expiry(1209600)  # 2 weeks
        else:
            request.session.set_expiry(0)  # expires on browser close

        security_logger.info(
            "User logged in successfully: user_id=%s username=%s role=%s remember_me=%s IP=%s",
            user.id,
            user.username,
            user.role,
            bool(form.cleaned_data.get("remember_me")),
            request.META.get("REMOTE_ADDR"),
        )

        user_data = user_to_dict(user)
        user_data["last_login"] = login_time
        return json_ok(user_data, status=200)

    # Hard Rule 9: Never log passwords! Only record identifier (username/email) and IP
    identifier = data.get("username_or_email") or data.get("username") or data.get("email") or "unknown"
    security_logger.warning(
        "Login failed for identifier=%s from IP %s: %s",
        identifier,
        request.META.get("REMOTE_ADDR"),
        form_errors(form),
    )
    return json_error("Invalid credentials.", errors=form_errors(form), status=400)


@require_POST
@login_required_json
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    POST /api/auth/logout/
    Terminate user session.
    Returns 200 on success, 401 if unauthenticated.
    """
    user_id = request.user.id
    username = request.user.username
    request.session.flush()
    logout(request)
    security_logger.info("User logged out: user_id=%s username=%s", user_id, username)
    return json_ok({"message": "Successfully logged out."})


@require_GET
def me_view(request: HttpRequest) -> HttpResponse:
    """
    GET /api/auth/me/
    Retrieve current authenticated user or null.
    Returns 200 with user object if authenticated, or {"data": null} if anonymous.
    """
    if request.user.is_authenticated:
        data = user_to_dict(request.user)
        data["last_login"] = request.session.get("last_login") or (
            request.user.last_login.isoformat() if request.user.last_login else None
        )
        logger.debug("Current user requested: user_id=%s username=%s", request.user.id, request.user.username)
        return json_ok(data)
    logger.debug("Current user requested: anonymous")
    return JsonResponse({"data": None}, status=200)
