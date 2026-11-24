from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.db import models


class UserQuerySet(models.QuerySet):
    """Custom queryset for User model providing role-based filter helpers."""

    def managers(self):
        """Filter users who have the MANAGER role.

        WHY: Centralises the domain logic of querying hotel managers, eliminating
        magic string literals like `filter(role="manager")` and ensuring consistent
        role queries across views, permissions, and administrative operations.
        """
        return self.filter(role=self.model.Role.MANAGER)

    def guests(self):
        """Filter users who have the GUEST role.

        WHY: Centralises the domain logic of querying guests, eliminating
        magic string literals like `filter(role="guest")` across bookings, reports,
        and customer notifications.
        """
        return self.filter(role=self.model.Role.GUEST)


class UserManager(DefaultUserManager.from_queryset(UserQuerySet)):
    """Custom manager for User model supporting role defaults, validation, and role querysets."""

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and save a regular user with role defaults and validation.

        WHY: Guarantees that every normal user created in the system defaults to
        the GUEST role unless explicitly specified with a valid role, and ensures
        that email is present according to business invariants.
        """
        if not email:
            raise ValueError("Users must have an email address.")
        role = extra_fields.setdefault("role", User.Role.GUEST)
        if role not in User.Role.values:
            raise ValueError(f"Invalid role '{role}'. Must be one of {User.Role.values}.")
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and save a superuser enforcing MANAGER role and admin flags.

        WHY: System administrators / superusers must be assigned the MANAGER role
        in addition to is_staff and is_superuser flags so that permissions and
        manager dashboards operate correctly for root accounts.
        """
        extra_fields.setdefault("role", User.Role.MANAGER)
        if extra_fields.get("role") != User.Role.MANAGER:
            raise ValueError("Superusers must have role=MANAGER.")
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
