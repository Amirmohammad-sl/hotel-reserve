"""Views for bookings, manager availability calendar, guest booking flow, and discount codes."""

from collections import defaultdict
from datetime import timedelta
import logging
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET, require_POST

from apps.bookings.forms import (
    BookingQuoteForm,
    DiscountCodeForm,
    DiscountValidateForm,
    ManagerAvailabilityFilterForm,
    ManagerBookingFilterForm,
    booking_to_dict,
    discount_code_to_dict,
)
from apps.bookings.models import Booking, DiscountCode
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
from apps.hotels.models import Hotel, RoomType

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("apps.security")


# ---------------------------------------------------------------------------
# Guest Booking Workflow (Owner B per docs/API_CONTRACT.md)
# ---------------------------------------------------------------------------


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
        logger.warning("Booking quote failed: invalid JSON payload from user_id=%s: %s", request.user.id, exc)
        return json_error(str(exc), status=400)

    form = BookingQuoteForm(data)
    if not form.is_valid():
        logger.warning("Booking quote validation failed for user_id=%s: %s", request.user.id, form_errors(form))
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
        logger.warning("Booking quote calculation error for user_id=%s: %s", request.user.id, errs)
        return json_error("Invalid booking parameters.", errors=errs, status=400)

    logger.debug(
        "Booking quote generated: user_id=%s room_type_id=%s check_in=%s check_out=%s rooms=%d total_price=%d available=%s",
        request.user.id,
        cleaned["room_type"].id,
        cleaned["check_in"],
        cleaned["check_out"],
        cleaned["rooms_count"],
        quote["total_price"],
        quote["available"],
    )
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
        logger.warning("Discount validate failed: invalid JSON payload from user_id=%s: %s", request.user.id, exc)
        return json_error(str(exc), status=400)

    form = DiscountValidateForm(data)
    if not form.is_valid():
        logger.warning("Discount validate form error for user_id=%s: %s", request.user.id, form_errors(form))
        return json_error("Invalid parameters.", errors=form_errors(form), status=400)

    cleaned = form.cleaned_data
    is_valid, discount_obj, message = validate_discount_code(
        hotel=cleaned["hotel"],
        code=cleaned["code"],
    )

    logger.info(
        "Discount validation completed: user_id=%s hotel_id=%s code='%s' valid=%s percent=%d",
        request.user.id,
        cleaned["hotel"].id,
        cleaned["code"],
        is_valid,
        discount_obj.percent if (discount_obj and is_valid) else 0,
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
        logger.warning("Booking create failed: invalid JSON payload from user_id=%s: %s", request.user.id, exc)
        return json_error(str(exc), status=400)

    form = BookingQuoteForm(data)
    if not form.is_valid():
        logger.warning("Booking create validation failed for user_id=%s: %s", request.user.id, form_errors(form))
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
        logger.warning("Booking create conflict for user_id=%s room_type_id=%s: %s", request.user.id, cleaned["room_type"].id, exc)
        return json_error(str(exc), status=409)
    except ValidationError as exc:
        errs = exc.message_dict if hasattr(exc, "message_dict") else {"__all__": [str(exc)]}
        logger.warning("Booking create validation error for user_id=%s: %s", request.user.id, errs)
        return json_error("Invalid booking parameters.", errors=errs, status=400)

    logger.info(
        "Booking created successfully: booking_id=%s guest_id=%s room_type_id=%s total_price=%d",
        booking.id,
        request.user.id,
        booking.room_type_id,
        booking.total_price,
    )
    return json_ok(booking_to_dict(booking), status=201)


@role_required("guest")
@require_GET
def my_bookings_list_view(request):
    """
    GET /api/bookings/mine/
    List all reservations booked by the current authenticated guest user.
    """
    bookings = (
        Booking.objects.for_guest(request.user)
        .select_related("guest", "room_type", "room_type__hotel", "discount_code")
        .order_by("-created_at")
    )
    bookings_list = list(bookings)
    logger.debug("Guest bookings listed: user_id=%s count=%d", request.user.id, len(bookings_list))
    return json_ok([booking_to_dict(b) for b in bookings_list])


@role_required("guest")
@require_POST
def booking_cancel_view(request, booking_id):
    """
    POST /api/bookings/{id}/cancel/
    Cancel a confirmed reservation before check-in date and restore room availability.
    """
    booking = (
        Booking.objects.for_guest(request.user)
        .filter(id=booking_id)
        .select_related("guest", "room_type", "room_type__hotel", "discount_code")
        .first()
    )
    if not booking:
        security_logger.warning("Booking cancel denied or not found: booking_id=%s user_id=%s", booking_id, request.user.id)
        return json_error("Booking not found.", status=404)

    try:
        cancelled = cancel_booking(booking=booking, user=request.user)
    except BookingCancellationError as exc:
        logger.warning("Booking cancel failed for booking_id=%s user_id=%s: %s", booking_id, request.user.id, exc)
        return json_error(str(exc), status=400)

    logger.info("Booking cancelled by guest: booking_id=%s user_id=%s", cancelled.id, request.user.id)
    return json_ok(booking_to_dict(cancelled))


# ---------------------------------------------------------------------------
# Manager Discount Codes CRUD (Owner A per docs/API_CONTRACT.md)
# ---------------------------------------------------------------------------


@role_required("manager")
def manager_discounts_list_create_view(request, hotel_id):
    """List discount codes (GET) or create a discount code (POST) for a manager's own hotel."""
    hotel = Hotel.objects.owned_by(request.user).filter(id=hotel_id).first()
    if not hotel:
        security_logger.warning("Manager discounts hotel access denied or not found: hotel_id=%s user_id=%s", hotel_id, request.user.id)
        return json_error("Hotel not found.", status=404)

    if request.method == "GET":
        discounts = DiscountCode.objects.for_hotel(hotel).order_by("-created_at")
        logger.debug("Manager discounts listed: hotel_id=%s count=%d user_id=%s", hotel_id, len(discounts), request.user.id)
        return json_ok([discount_code_to_dict(dc) for dc in discounts])

    if request.method == "POST":
        try:
            data = parse_json(request)
        except ValueError as exc:
            logger.warning("Manager discount create failed: invalid JSON for hotel_id=%s user_id=%s error=%s", hotel_id, request.user.id, exc)
            return json_error(str(exc), status=400)

        form = DiscountCodeForm(data, hotel=hotel)
        if not form.is_valid():
            logger.warning("Manager discount create validation failed for hotel_id=%s user_id=%s: %s", hotel_id, request.user.id, form_errors(form))
            return json_error("Validation failed", errors=form_errors(form), status=400)

        discount_code = form.save()
        logger.info(
            "Manager created discount code: discount_id=%s code='%s' hotel_id=%s user_id=%s",
            discount_code.id,
            discount_code.code,
            hotel_id,
            request.user.id,
        )
        return json_ok(discount_code_to_dict(discount_code), status=201)

    return json_error("Method not allowed", status=405)


@role_required("manager")
def manager_discount_detail_update_delete_view(request, discount_id):
    """Retrieve (GET), update (PUT/PATCH), or delete (DELETE) a manager's own discount code."""
    discount_code = (
        DiscountCode.objects.owned_by(request.user)
        .select_related("hotel")
        .filter(id=discount_id)
        .first()
    )
    if not discount_code:
        security_logger.warning("Manager discount access denied or not found: discount_id=%s user_id=%s", discount_id, request.user.id)
        return json_error("Discount code not found.", status=404)

    if request.method == "GET":
        logger.debug("Manager discount viewed: discount_id=%s user_id=%s", discount_id, request.user.id)
        return json_ok(discount_code_to_dict(discount_code))

    if request.method in ("PUT", "PATCH"):
        try:
            data = parse_json(request)
        except ValueError as exc:
            logger.warning("Manager discount update failed: invalid JSON for discount_id=%s user_id=%s error=%s", discount_id, request.user.id, exc)
            return json_error(str(exc), status=400)

        form = DiscountCodeForm(data, instance=discount_code, hotel=discount_code.hotel)
        if not form.is_valid():
            logger.warning("Manager discount update validation failed for discount_id=%s user_id=%s: %s", discount_id, request.user.id, form_errors(form))
            return json_error("Validation failed", errors=form_errors(form), status=400)

        discount_code = form.save()
        logger.info("Manager updated discount code: discount_id=%s code='%s' user_id=%s", discount_code.id, discount_code.code, request.user.id)
        return json_ok(discount_code_to_dict(discount_code))

    if request.method == "DELETE":
        code_str = discount_code.code
        hotel_id = discount_code.hotel.id
        discount_code.delete()
        logger.info("Manager deleted discount code: discount_id=%s code='%s' hotel_id=%s user_id=%s", discount_id, code_str, hotel_id, request.user.id)
        return json_ok({"message": "Discount code deleted successfully."})

    return json_error("Method not allowed", status=405)


# ---------------------------------------------------------------------------
# Manager Bookings and Availability Views (Owner A per docs/API_CONTRACT.md)
# ---------------------------------------------------------------------------


@require_GET
@role_required("manager")
def manager_hotel_bookings_list_view(request, hotel_id):
    """List bookings for a manager's own hotel with optional status and date filters."""
    hotel = Hotel.objects.owned_by(request.user).filter(id=hotel_id).first()
    if not hotel:
        security_logger.warning("Manager bookings hotel access denied or not found: hotel_id=%s user_id=%s", hotel_id, request.user.id)
        return json_error("Hotel not found.", status=404)

    form = ManagerBookingFilterForm(request.GET)
    if not form.is_valid():
        logger.info("Manager bookings filter validation failed for hotel_id=%s: %s", hotel_id, form_errors(form))
        return json_error("Invalid filter parameters", errors=form_errors(form), status=400)

    status_filter = form.cleaned_data.get("status")
    date_from = form.cleaned_data.get("date_from")
    date_to = form.cleaned_data.get("date_to")

    bookings_qs = (
        Booking.objects.for_hotel(hotel)
        .select_related("guest", "room_type", "room_type__hotel", "discount_code")
        .order_by("-created_at")
    )

    if status_filter:
        bookings_qs = bookings_qs.filter(status=status_filter)

    if date_from and date_to:
        bookings_qs = bookings_qs.filter(check_in__lte=date_to, check_out__gte=date_from)
    elif date_from:
        bookings_qs = bookings_qs.filter(check_out__gte=date_from)
    elif date_to:
        bookings_qs = bookings_qs.filter(check_in__lte=date_to)

    bookings_list = list(bookings_qs)
    logger.debug("Manager hotel bookings listed: hotel_id=%s count=%d user_id=%s", hotel_id, len(bookings_list), request.user.id)
    return json_ok([booking_to_dict(b) for b in bookings_list])


@require_GET
@role_required("manager")
def manager_hotel_availability_view(request, hotel_id):
    """Return availability breakdown (total, reserved, free) per room type per day for a manager's own hotel."""
    hotel = Hotel.objects.owned_by(request.user).filter(id=hotel_id).first()
    if not hotel:
        security_logger.warning("Manager availability hotel access denied or not found: hotel_id=%s user_id=%s", hotel_id, request.user.id)
        return json_error("Hotel not found.", status=404)

    form = ManagerAvailabilityFilterForm(request.GET)
    if not form.is_valid():
        logger.info("Manager availability filter validation failed for hotel_id=%s: %s", hotel_id, form_errors(form))
        return json_error("Invalid date parameters", errors=form_errors(form), status=400)

    date_from = form.cleaned_data["date_from"]
    date_to = form.cleaned_data["date_to"]

    room_types = list(RoomType.objects.for_hotel(hotel).order_by("price_per_night"))
    if not room_types:
        return json_ok([])

    # Query all confirmed overlapping bookings within the requested range
    overlapping_bookings = list(
        Booking.objects.active()
        .for_hotel(hotel)
        .overlapping(date_from, date_to)
    )

    bookings_by_room = defaultdict(list)
    for booking in overlapping_bookings:
        bookings_by_room[booking.room_type_id].append(booking)

    results = []
    for rt in room_types:
        rt_bookings = bookings_by_room[rt.id]
        daily_list = []
        curr_day = date_from
        while curr_day < date_to:
            reserved_count = sum(
                b.rooms_count
                for b in rt_bookings
                if b.check_in <= curr_day < b.check_out
            )
            free_count = max(0, rt.quantity - reserved_count)
            daily_list.append(
                {
                    "date": curr_day.isoformat(),
                    "total": rt.quantity,
                    "reserved": reserved_count,
                    "free": free_count,
                }
            )
            curr_day += timedelta(days=1)

        results.append(
            {
                "room_type_id": rt.id,
                "room_type_title": rt.title,
                "total_quantity": rt.quantity,
                "daily_availability": daily_list,
            }
        )

    logger.debug("Manager hotel availability computed: hotel_id=%s date_from=%s date_to=%s user_id=%s", hotel_id, date_from, date_to, request.user.id)
    return json_ok(results)
