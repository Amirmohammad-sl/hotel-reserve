"""Forms for user registration and authentication."""

from typing import Any, Dict, Optional
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import models
from .models import User


def user_to_dict(user: User) -> Dict[str, Any]:
    """
    Serialize user instance to standard dictionary per API_CONTRACT.md.
    user = {id, username, email, role, email_verified}
    """
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "email_verified": user.email_verified,
    }


class RegisterForm(forms.Form):
    """Form handling user registration with password confirmation and role assignment."""

    username = forms.CharField(
        max_length=150,
        required=True,
        error_messages={"required": "Username is required."},
    )
    email = forms.EmailField(
        required=True,
        error_messages={"required": "Email is required."},
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        error_messages={"required": "Password is required."},
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        error_messages={"required": "Password confirmation is required."},
    )
    role = forms.ChoiceField(
        choices=User.Role.choices,
        required=False,
        initial=User.Role.GUEST,
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
    )

    def clean_username(self) -> str:
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        role = cleaned_data.get("role") or User.Role.GUEST
        cleaned_data["role"] = role

        if password and password2:
            if password != password2:
                self.add_error("password2", "Passwords do not match.")
            else:
                temp_user = User(
                    username=cleaned_data.get("username", ""),
                    email=cleaned_data.get("email", ""),
                )
                try:
                    validate_password(password, user=temp_user)
                except forms.ValidationError as error:
                    self.add_error("password", error)

        return cleaned_data

    def save(self) -> User:
        """Create and return a new User."""
        return User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            role=self.cleaned_data.get("role", User.Role.GUEST),
            phone=self.cleaned_data.get("phone", ""),
        )


class LoginForm(forms.Form):
    """Form handling user login with username or email, and optional remember-me."""

    username_or_email = forms.CharField(
        required=True,
        error_messages={"required": "Username or email is required."},
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        error_messages={"required": "Password is required."},
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache: Optional[User] = None

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get("username_or_email")
        password = cleaned_data.get("password")

        if username_or_email and password:
            identifier = username_or_email.strip()
            user_obj = User.objects.filter(
                models.Q(username__iexact=identifier) | models.Q(email__iexact=identifier)
            ).first()

            if user_obj is None:
                self.add_error("username_or_email", "Invalid username or email.")
            elif not user_obj.check_password(password):
                self.add_error("password", "Invalid password.")
            elif not user_obj.is_active:
                self.add_error("__all__", "This account is inactive.")
            else:
                user = authenticate(
                    request=self.request,
                    username=user_obj.username,
                    password=password,
                )
                self.user_cache = user

        return cleaned_data

    def get_user(self) -> Optional[User]:
        """Return the authenticated user after clean."""
        return self.user_cache
