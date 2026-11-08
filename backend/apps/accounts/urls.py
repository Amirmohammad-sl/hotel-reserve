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
    path("verify-email/", views.verify_email_view, name="verify-email"),
    path("resend-verification/", views.resend_verification_view, name="resend-verification"),
]
