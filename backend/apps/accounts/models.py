from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.db import models


class UserManager(DefaultUserManager):
    """Custom manager skeleton for User model supporting role defaults."""

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.GUEST)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.MANAGER)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for the hotel reservation system."""

    class Role(models.TextChoices):
        MANAGER = "manager", "Manager"
        GUEST = "guest", "Guest"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST,
        help_text="User role in the system: manager or guest.",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Contact phone number.",
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        help_text="Required unique email address.",
    )
    email_verified = models.BooleanField(
        default=False,
        help_text="Designates whether the user's email has been verified.",
    )

    objects = UserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["id"]

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    @property
    def is_guest(self):
        return self.role == self.Role.GUEST

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
