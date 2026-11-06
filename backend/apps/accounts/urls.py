from django.urls import path
from apps.core.views import csrf_token_view

app_name = "accounts"

urlpatterns = [
    path("csrf/", csrf_token_view, name="csrf"),
    # Auth endpoints will be registered here (P2-02) per docs/API_CONTRACT.md
]
