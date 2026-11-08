"""Token generation and email verification helpers using django.core.signing."""

import logging
from typing import Optional
from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

from apps.accounts.models import User

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("apps.security")

# Token validity duration: 48 hours in seconds (per ADR D-007)
VERIFICATION_TOKEN_MAX_AGE = 48 * 3600  # 172800 seconds
TOKEN_SALT = "accounts.email-verification"


def get_signer() -> TimestampSigner:
    """Return a TimestampSigner instance with dedicated salt."""
    return TimestampSigner(salt=TOKEN_SALT)


def generate_verification_token(user: User) -> str:
    """
    Generate a signed, timestamped verification token encoding user ID.
    Uses django.core.signing.TimestampSigner.
    """
    signer = get_signer()
    return signer.sign(str(user.pk))


def verify_token(token: str) -> User:
    """
    Validate signed token and return the corresponding User instance.

    Raises:
        SignatureExpired: If token timestamp is older than VERIFICATION_TOKEN_MAX_AGE.
        BadSignature: If token signature has been altered or is malformed.
        User.DoesNotExist: If user ID in valid token does not exist in database.
    """
    if not token or not isinstance(token, str):
        raise BadSignature("Token must be a non-empty string.")

    signer = get_signer()
    # unsign validates signature and checks max_age
    user_id_str = signer.unsign(token.strip(), max_age=VERIFICATION_TOKEN_MAX_AGE)
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise BadSignature("Malformed token payload.")

    return User.objects.get(pk=user_id)


def build_verification_url(token: str) -> str:
    """Build full URL to frontend verification page."""
    base_url = getattr(settings, "FRONTEND_ORIGIN", "http://localhost:5173").rstrip("/")
    return f"{base_url}/verify-email?token={token}"


def send_verification_email(user: User, request=None) -> bool:
    """
    Generate token and send verification email to user.
    Uses configured EMAIL_BACKEND (console backend in development/tests).

    Returns True if sent successfully, False otherwise.
    """
    token = generate_verification_token(user)
    verification_url = build_verification_url(token)

    subject = "Verify your email address - Hotel Reservation"
    message = (
        f"Hello {user.username},\n\n"
        "Thank you for registering at Hotel Reservation.\n"
        "Please verify your email address by opening the following link:\n\n"
        f"{verification_url}\n\n"
        "This link will expire in 48 hours.\n"
        "If you did not register for this account, you can safely ignore this email.\n"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@hotel.local")

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=False,
        )
        security_logger.info(
            "Verification email sent: user_id=%s email=%s",
            user.id,
            user.email,
        )
        return True
    except Exception as exc:
        logger.error(
            "Failed to send verification email: user_id=%s email=%s error=%s",
            user.id,
            user.email,
            exc,
        )
        return False
