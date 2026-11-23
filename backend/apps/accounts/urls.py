from django.urls import path
from apps.core.views import csrf_token_view
from . import views

app_name = "accounts"

urlpatterns = [
    path("csrf/", csrf_token_view, name="csrf"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.me_view, name="me"),
]
