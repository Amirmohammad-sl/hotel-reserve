from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for custom User model."""

    list_display = (
        "username",
        "email",
        "role",
        "phone",
        "email_verified",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "role",
        "email_verified",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = ("username", "email", "phone")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Hotel Role & Verification",
            {
                "fields": (
                    "role",
                    "phone",
                    "email_verified",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Hotel Role & Profile",
            {
                "fields": (
                    "email",
                    "role",
                    "phone",
                    "email_verified",
                )
            },
        ),
    )
