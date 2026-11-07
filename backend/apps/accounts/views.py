"""Authentication views returning standard JSON responses."""

from django.contrib.auth import login, logout
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from apps.core.decorators import login_required_json
from apps.core.forms import form_errors
from apps.core.http import json_error, json_ok, parse_json
from .forms import LoginForm, RegisterForm, user_to_dict


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
        return json_error("Invalid JSON body.", status=400)

    form = RegisterForm(data=data)
    if form.is_valid():
        user = form.save()
        return json_ok(user_to_dict(user), status=201)

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

        user_data = user_to_dict(user)
        user_data["last_login"] = login_time
        return json_ok(user_data, status=200)

    return json_error("Invalid credentials.", errors=form_errors(form), status=400)


@require_POST
@login_required_json
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    POST /api/auth/logout/
    Terminate user session.
    Returns 200 on success, 401 if unauthenticated.
    """
    request.session.flush()
    logout(request)
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
        return json_ok(data)
    return JsonResponse({"data": None}, status=200)
