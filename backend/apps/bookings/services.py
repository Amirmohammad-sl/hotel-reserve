"""Domain and business logic services for guest bookings and discounts."""

from datetime import date
from typing import Any, Dict, Optional, Tuple
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from apps.bookings.models import Booking, DiscountCode
from apps.hotels.models import RoomType


class AvailabilityConflictError(Exception):
    """Raised when the requested room count exceeds available inventory for given dates."""
    pass


class BookingCancellationError(Exception):
    """Raised when a booking cannot be cancelled according to business rules."""
    pass


def validate_discount_code(
    hotel,
    code: str,
    today: Optional[date] = None,
) -> Tuple[bool, Optional[DiscountCode], str]:
    """
    Validate a discount coupon code for a given hotel and date.

    Returns:
        (is_valid, discount_obj, reason_message)
    """
    if not code:
        return False, None, "Discount code cannot be empty."

    if today is None:
        today = timezone.localdate()

    valid_discount = DiscountCode.objects.get_valid(hotel=hotel, code=code, today=today)
    if valid_discount:
        return True, valid_discount, f"Discount code applied ({valid_discount.percent}% off)."

    normalized_code = code.strip().upper()
    discount = (
        DiscountCode.objects.filter(hotel=hotel, code=normalized_code)
        .first()
    )

    if not discount:
        return False, None, "Discount code not found for this hotel."

    if not discount.is_active:
        return False, discount, "Discount code is inactive."

    if today < discount.valid_from:
        return False, discount, "Discount code is not active yet."

    if today > discount.valid_to:
        return False, discount, "Discount code has expired."

    if discount.max_uses is not None and discount.used_count >= discount.max_uses:
        return False, discount, "Discount code has reached its maximum redemptions."

    return False, discount, "Discount code is not valid."


def calculate_booking_quote(
    room_type: RoomType,
    check_in: date,
    check_out: date,
    rooms_count: int = 1,
    guests_count: int = 1,
    discount_code: Optional[str] = None,
    today: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Calculate booking quote details: nights, subtotal, discount, total, and availability.

    Raises:
        ValidationError if discount_code is invalid.
    """
    if check_out <= check_in:
        raise ValidationError({"check_out": "Check-out date must be after check-in date."})

    nights = (check_out - check_in).days
    subtotal = rooms_count * nights * room_type.price_per_night

    room_type_with_avail = (
        RoomType.objects.with_availability(check_in, check_out)
        .filter(id=room_type.id)
        .first()
    )
    available_count = room_type_with_avail.available_count if room_type_with_avail else 0
    available = available_count >= rooms_count

    discount_amount = 0
    discount_obj = None

    if discount_code:
        is_valid, discount_obj, reason = validate_discount_code(
            hotel=room_type.hotel,
            code=discount_code,
            today=today,
        )
        if not is_valid:
            raise ValidationError({"discount_code": reason})

        discount_amount = (subtotal * discount_obj.percent) // 100

    total_price = max(0, subtotal - discount_amount)

    return {
        "nights": nights,
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "total_price": total_price,
        "available": available,
        "available_count": available_count,
        "discount_obj": discount_obj,
    }


def create_booking(
    guest,
    room_type: RoomType,
    check_in: date,
    check_out: date,
    rooms_count: int = 1,
    guests_count: int = 1,
    discount_code: Optional[str] = None,
) -> Booking:
    """
    Create a confirmed booking atomically.

    Raises:
        AvailabilityConflictError: if requested rooms are not available (yields 409).
        ValidationError: if discount code is invalid or dates are invalid.
    """
    with transaction.atomic():
        quote = calculate_booking_quote(
            room_type=room_type,
            check_in=check_in,
            check_out=check_out,
            rooms_count=rooms_count,
            guests_count=guests_count,
            discount_code=discount_code,
        )

        if not quote["available"]:
            raise AvailabilityConflictError(
                f"Requested {rooms_count} room(s) not available for the selected dates (only {quote['available_count']} available)."
            )

        discount_obj = quote["discount_obj"]
        if discount_obj:
            DiscountCode.objects.filter(id=discount_obj.id).update(
                used_count=models.F("used_count") + 1
            )
            discount_obj.refresh_from_db()

        booking = Booking.objects.create(
            guest=guest,
            room_type=room_type,
            check_in=check_in,
            check_out=check_out,
            rooms_count=rooms_count,
            guests_count=guests_count,
            nights=quote["nights"],
            price_per_night_snapshot=room_type.price_per_night,
            subtotal=quote["subtotal"],
            discount_code=discount_obj,
            discount_amount=quote["discount_amount"],
            total_price=quote["total_price"],
            status=Booking.Status.CONFIRMED,
        )
        return booking


def cancel_booking(booking: Booking, user) -> Booking:
    """
    Cancel an existing booking atomically following business invariants.

    Raises:
        BookingCancellationError: if booking cannot be cancelled.
    """
    with transaction.atomic():
        if booking.guest_id != user.id:
            raise BookingCancellationError("You do not have permission to cancel this booking.")

        if booking.status != Booking.Status.CONFIRMED:
            raise BookingCancellationError("Booking is already cancelled.")

        today = timezone.localdate()
        if booking.check_in <= today:
            raise BookingCancellationError("Cannot cancel a booking on or after the check-in date.")

        booking.status = Booking.Status.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=["status", "cancelled_at"])

        if booking.discount_code_id:
            DiscountCode.objects.filter(
                id=booking.discount_code_id,
                used_count__gt=0,
            ).update(used_count=models.F("used_count") - 1)
            if booking.discount_code:
                booking.discount_code.refresh_from_db()

        return booking
