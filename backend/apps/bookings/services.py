"""Domain and business logic services for guest bookings and discounts."""

from datetime import date
import logging
from typing import Any, Dict, Optional, Tuple
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from apps.bookings.models import Booking, DiscountCode
from apps.hotels.models import RoomType

logger = logging.getLogger(__name__)


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
    hotel_id = getattr(hotel, "id", hotel)
    if not code:
        logger.info("Discount code validation failed: empty code for hotel_id=%s", hotel_id)
        return False, None, "Discount code cannot be empty."

    if today is None:
        today = timezone.localdate()

    valid_discount = DiscountCode.objects.get_valid(hotel=hotel, code=code, today=today)
    if valid_discount:
        logger.info(
            "Discount code applied: code='%s' hotel_id=%s discount_id=%s percent=%d",
            valid_discount.code,
            hotel_id,
            valid_discount.id,
            valid_discount.percent,
        )
        return True, valid_discount, f"Discount code applied ({valid_discount.percent}% off)."

    normalized_code = code.strip().upper()
    discount = (
        DiscountCode.objects.filter(hotel=hotel, code=normalized_code)
        .first()
    )

    if not discount:
        reason = "Discount code not found for this hotel."
        logger.info("Discount code rejected: code='%s' hotel_id=%s reason='%s'", normalized_code, hotel_id, reason)
        return False, None, reason

    if not discount.is_active:
        reason = "Discount code is inactive."
        logger.info("Discount code rejected: code='%s' hotel_id=%s reason='%s'", normalized_code, hotel_id, reason)
        return False, discount, reason

    if today < discount.valid_from:
        reason = "Discount code is not active yet."
        logger.info("Discount code rejected: code='%s' hotel_id=%s reason='%s'", normalized_code, hotel_id, reason)
        return False, discount, reason

    if today > discount.valid_to:
        reason = "Discount code has expired."
        logger.info("Discount code rejected: code='%s' hotel_id=%s reason='%s'", normalized_code, hotel_id, reason)
        return False, discount, reason

    if discount.max_uses is not None and discount.used_count >= discount.max_uses:
        reason = "Discount code has reached its maximum redemptions."
        logger.info("Discount code rejected: code='%s' hotel_id=%s reason='%s'", normalized_code, hotel_id, reason)
        return False, discount, reason

    reason = "Discount code is not valid."
    logger.info("Discount code rejected: code='%s' hotel_id=%s reason='%s'", normalized_code, hotel_id, reason)
    return False, discount, reason


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
        logger.warning(
            "Quote calculation failed: invalid dates check_in=%s check_out=%s room_type_id=%s",
            check_in,
            check_out,
            getattr(room_type, "id", None),
        )
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
            logger.info(
                "Quote rejected invalid discount code='%s' for room_type_id=%s: %s",
                discount_code,
                room_type.id,
                reason,
            )
            raise ValidationError({"discount_code": reason})

        discount_amount = (subtotal * discount_obj.percent) // 100

    total_price = max(0, subtotal - discount_amount)

    logger.debug(
        "Quote calculated: room_type_id=%s check_in=%s check_out=%s rooms=%d nights=%d subtotal=%d discount=%d total=%d available=%s",
        room_type.id,
        check_in,
        check_out,
        rooms_count,
        nights,
        subtotal,
        discount_amount,
        total_price,
        available,
    )

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
    Create a confirmed booking atomically with pessimistic concurrency protection.

    Serializes concurrent booking requests for the same room type using
    `select_for_update()` on the RoomType row to prevent overbooking races.

    Raises:
        AvailabilityConflictError: if requested rooms are not available (yields 409).
        ValidationError: if discount code is invalid or dates are invalid.
    """
    with transaction.atomic():
        locked_room_type = RoomType.objects.select_for_update().get(id=room_type.id)

        # Also lock the discount code row if supplied to prevent race on max_uses
        if discount_code:
            code_str = discount_code.strip().upper()
            DiscountCode.objects.select_for_update().filter(
                hotel=locked_room_type.hotel,
                code=code_str,
            ).first()

        quote = calculate_booking_quote(
            room_type=locked_room_type,
            check_in=check_in,
            check_out=check_out,
            rooms_count=rooms_count,
            guests_count=guests_count,
            discount_code=discount_code,
        )

        if not quote["available"]:
            logger.warning(
                "Booking conflict: requested %d room(s) unavailable for room_type_id=%s hotel_id=%s check_in=%s check_out=%s available=%d guest_id=%s",
                rooms_count,
                locked_room_type.id,
                locked_room_type.hotel_id,
                check_in,
                check_out,
                quote["available_count"],
                guest.id,
            )
            raise AvailabilityConflictError(
                f"Requested {rooms_count} room(s) not available for the selected dates (only {quote['available_count']} available)."
            )

        discount_obj = quote["discount_obj"]
        if discount_obj:
            if discount_obj.max_uses is not None and discount_obj.used_count >= discount_obj.max_uses:
                logger.warning(
                    "Booking creation rejected: discount code max redemptions reached code='%s' discount_id=%s guest_id=%s",
                    discount_obj.code,
                    discount_obj.id,
                    guest.id,
                )
                raise ValidationError({"discount_code": "Discount code has reached its maximum redemptions."})

            DiscountCode.objects.filter(id=discount_obj.id).update(
                used_count=models.F("used_count") + 1
            )
            discount_obj.refresh_from_db()

        booking = Booking.objects.create(
            guest=guest,
            room_type=locked_room_type,
            check_in=check_in,
            check_out=check_out,
            rooms_count=rooms_count,
            guests_count=guests_count,
            nights=quote["nights"],
            price_per_night_snapshot=locked_room_type.price_per_night,
            subtotal=quote["subtotal"],
            discount_code=discount_obj,
            discount_amount=quote["discount_amount"],
            total_price=quote["total_price"],
            status=Booking.Status.CONFIRMED,
        )
        logger.info(
            "Booking created: booking_id=%s guest_id=%s room_type_id=%s hotel_id=%s check_in=%s check_out=%s rooms=%d total_price=%d discount_id=%s",
            booking.id,
            guest.id,
            locked_room_type.id,
            locked_room_type.hotel_id,
            check_in,
            check_out,
            rooms_count,
            booking.total_price,
            booking.discount_code_id,
        )
        return booking


def cancel_booking(booking: Booking, user) -> Booking:
    """
    Cancel an existing booking atomically following business invariants.

    Raises:
        BookingCancellationError: if booking cannot be cancelled.
    """
    with transaction.atomic():
        locked_booking = (
            Booking.objects.select_for_update()
            .filter(id=booking.id)
            .first()
        )
        if not locked_booking:
            logger.warning("Booking cancellation failed: booking_id=%s not found", booking.id)
            raise BookingCancellationError("Booking not found.")

        if locked_booking.guest_id != user.id:
            logger.warning(
                "Booking cancellation forbidden: booking_id=%s belongs to user_id=%s, attempted by user_id=%s",
                locked_booking.id,
                locked_booking.guest_id,
                user.id,
            )
            raise BookingCancellationError("You do not have permission to cancel this booking.")

        if locked_booking.status != Booking.Status.CONFIRMED:
            logger.warning(
                "Booking cancellation rejected: booking_id=%s status is already '%s'",
                locked_booking.id,
                locked_booking.status,
            )
            raise BookingCancellationError("Booking is already cancelled.")

        today = timezone.localdate()
        if locked_booking.check_in <= today:
            logger.warning(
                "Booking cancellation rejected: booking_id=%s check_in=%s is today or in the past (today=%s)",
                locked_booking.id,
                locked_booking.check_in,
                today,
            )
            raise BookingCancellationError("Cannot cancel a booking on or after the check-in date.")

        locked_booking.status = Booking.Status.CANCELLED
        locked_booking.cancelled_at = timezone.now()
        locked_booking.save(update_fields=["status", "cancelled_at"])

        if locked_booking.discount_code_id:
            DiscountCode.objects.filter(
                id=locked_booking.discount_code_id,
                used_count__gt=0,
            ).update(used_count=models.F("used_count") - 1)
            if locked_booking.discount_code:
                locked_booking.discount_code.refresh_from_db()

        logger.info(
            "Booking cancelled successfully: booking_id=%s guest_id=%s room_type_id=%s restored_discount_id=%s",
            locked_booking.id,
            user.id,
            locked_booking.room_type_id,
            locked_booking.discount_code_id,
        )
        return locked_booking
