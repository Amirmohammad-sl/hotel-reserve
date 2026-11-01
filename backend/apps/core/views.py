from django.views.decorators.http import require_GET
from .http import json_ok


@require_GET
def health_check(request):
    """Health check endpoint returning {"data": {"status": "ok"}}."""
    return json_ok({"status": "ok"})
