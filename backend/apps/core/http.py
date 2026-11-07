import json
from django.http import JsonResponse


def json_ok(data=None, status=200, **extra):
    """Return standard JSON success envelope {"data": ...}."""
    payload = {"data": data if data is not None else {}}
    payload.update(extra)
    return JsonResponse(payload, status=status)


def json_error(message, errors=None, status=400, **extra):
    """Return standard JSON error envelope {"message": ..., "errors": ...}."""
    payload = {"message": message}
    if errors is not None:
        payload["errors"] = errors
    payload.update(extra)
    return JsonResponse(payload, status=status)


def parse_json(request):
    """Parse JSON body from request.

    Returns a dict or raises ValueError on invalid JSON.
    """
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid JSON body") from exc
