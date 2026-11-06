"""Views for guest booking workflow and discount code validation."""

from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET, require_POST

from apps.bookings.forms import (
    BookingQuoteForm,
    DiscountValidateForm,
    booking_to_dict,
)
from apps.bookings.models import Booking
from apps.bookings.services import (
    AvailabilityConflictError,
    BookingCancellationError,
    calculate_booking_quote,
    cancel_booking,
    create_booking,
    validate_discount_code,
)
from apps.core.decorators import role_required
from apps.core.forms import form_errors
from apps.core.http import json_error, json_ok, parse_json


@role_required("guest")
def quote_view(request):
    """
    POST /api/bookings/quote/
    Calculate price quote and availability without persisting a reservation.
    """
    if request.method != "POST":
        return json_error("Method not allowed.", status=405)

    try:
        data = parse_json(request)
    except ValueError as exc:
        return json_error(str(exc), status=400)

    form = BookingQuoteForm(data)
    if not form.is_valid():
        return json_error("Invalid booking parameters.", errors=form_errors(form), status=400)

    cleaned = form.cleaned_data
    try:
        quote = calculate_booking_quote(
            room_type=cleaned["room_type"],
            check_in=cleaned["check_in"],
            check_out=cleaned["check_out"],
            rooms_count=cleaned["rooms_count"],
            guests_count=cleaned["guests_count"],
            discount_code=cleaned.get("discount_code"),
        )
    except ValidationError as exc:
        errs = exc.message_dict if hasattr(exc, "message_dict") else {"__all__": [str(exc)]}
        return json_error("Invalid booking parameters.", errors=errs, status=400)

    return json_ok(
        {
            "nights": quote["nights"],
            "subtotal": quote["subtotal"],
            "discount_amount": quote["discount_amount"],
            "total_price": quote["total_price"],
            "available": quote["available"],
        }
    )


@role_required("guest")
def discount_validate_view(request):
    """
    POST /api/discounts/validate/
    Validate promotional coupon code for a hotel and return eligibility status.
    """
    if request.method != "POST":
        return json_error("Method not allowed.", status=405)

    try:
        data = parse_json(request)
    except ValueError as exc:
        return json_error(str(exc), status=400)

    form = DiscountValidateForm(data)
    if not form.is_valid():
        return json_error("Invalid parameters.", errors=form_errors(form), status=400)

    cleaned = form.cleaned_data
    is_valid, discount_obj, message = validate_discount_code(
        hotel=cleaned["hotel"],
        code=cleaned["code"],
    )

    return json_ok(
        {
            "valid": is_valid,
            "percent": discount_obj.percent if (discount_obj and is_valid) else 0,
            "message": message,
        }
    )


@role_required("guest")
def booking_create_view(request):
    """
    POST /api/bookings/
    Create a new confirmed booking.
    Returns HTTP 201 on success or HTTP 409 Conflict if room stock is unavailable.
    """
    if request.method != "POST":
        return json_error("Method not allowed.", status=405)

    try:
        data = parse_json(request)
    except ValueError as exc:
        return json_error(str(exc), status=400)

    form = BookingQuoteForm(data)
    if not form.is_valid():
        return json_error("Invalid booking parameters.", errors=form_errors(form), status=400)

    cleaned = form.cleaned_data
    try:
        booking = create_booking(
            guest=request.user,
            room_type=cleaned["room_type"],
            check_in=cleaned["check_in"],
            check_out=cleaned["check_out"],
            rooms_count=cleaned["rooms_count"],
            guests_count=cleaned["guests_count"],
            discount_code=cleaned.get("discount_code"),
        )
    except AvailabilityConflictError as exc:
        return json_error(str(exc), status=409)
    except ValidationError as exc:
        errs = exc.message_dict if hasattr(exc, "message_dict") else {"__all__": [str(exc)]}
        return json_error("Invalid booking parameters.", errors=errs, status=400)

    return json_ok(booking_to_dict(booking), status=201)


@role_required("guest")
@require_GET
def my_bookings_list_view(request):
    """
    GET /api/bookings/mine/
    List all reservations booked by the current authenticated guest user.
    """
    bookings = (
        Booking.objects.filter(guest=request.user)
        .select_related("room_type", "room_type__hotel", "discount_code")
        .order_by("-created_at")
    )
    return json_ok([booking_to_dict(b) for b in bookings])


@role_required("guest")
@require_POST
def booking_cancel_view(request, booking_id):
    """
    POST /api/bookings/{id}/cancel/
    Cancel a confirmed reservation before check-in date and restore room availability.
    """
    booking = (
        Booking.objects.filter(id=booking_id, guest=request.user)
        .select_related("room_type", "room_type__hotel", "discount_code")
        .first()
    )
    if not booking:
        return json_error("Booking not found.", status=404)

    try:
        cancelled = cancel_booking(booking=booking, user=request.user)
    except BookingCancellationError as exc:
        return json_error(str(exc), status=400)

    return json_ok(booking_to_dict(cancelled))
