"""Views for bookings, manager availability calendar, and discount codes."""

from collections import defaultdict
from datetime import timedelta
from django.views.decorators.http import require_GET

from apps.bookings.forms import (
    DiscountCodeForm,
    ManagerAvailabilityFilterForm,
    ManagerBookingFilterForm,
    booking_to_dict,
    discount_code_to_dict,
)
from apps.bookings.models import Booking, DiscountCode
from apps.core.decorators import role_required
from apps.core.forms import form_errors
from apps.core.http import json_error, json_ok, parse_json
from apps.hotels.models import Hotel, RoomType


# ---------------------------------------------------------------------------
# Manager Discount Codes CRUD (Owner A)
# ---------------------------------------------------------------------------


@role_required("manager")
def manager_discounts_list_create_view(request, hotel_id):
    """List discount codes (GET) or create a discount code (POST) for a manager's own hotel."""
    hotel = Hotel.objects.filter(id=hotel_id, owner=request.user).first()
    if not hotel:
        return json_error("Hotel not found.", status=404)

    if request.method == "GET":
        discounts = hotel.discount_codes.all().order_by("-created_at")
        return json_ok([discount_code_to_dict(dc) for dc in discounts])

    if request.method == "POST":
        try:
            data = parse_json(request)
        except ValueError as exc:
            return json_error(str(exc), status=400)

        form = DiscountCodeForm(data, hotel=hotel)
        if not form.is_valid():
            return json_error("Validation failed", errors=form_errors(form), status=400)

        discount_code = form.save()
        return json_ok(discount_code_to_dict(discount_code), status=201)

    return json_error("Method not allowed", status=405)


@role_required("manager")
def manager_discount_detail_update_delete_view(request, discount_id):
    """Retrieve (GET), update (PUT/PATCH), or delete (DELETE) a manager's own discount code."""
    discount_code = (
        DiscountCode.objects.select_related("hotel")
        .filter(id=discount_id, hotel__owner=request.user)
        .first()
    )
    if not discount_code:
        return json_error("Discount code not found.", status=404)

    if request.method == "GET":
        return json_ok(discount_code_to_dict(discount_code))

    if request.method in ("PUT", "PATCH"):
        try:
            data = parse_json(request)
        except ValueError as exc:
            return json_error(str(exc), status=400)

        form = DiscountCodeForm(data, instance=discount_code, hotel=discount_code.hotel)
        if not form.is_valid():
            return json_error("Validation failed", errors=form_errors(form), status=400)

        discount_code = form.save()
        return json_ok(discount_code_to_dict(discount_code))

    if request.method == "DELETE":
        discount_code.delete()
        return json_ok({"message": "Discount code deleted successfully."})

    return json_error("Method not allowed", status=405)


# ---------------------------------------------------------------------------
# Manager Bookings and Availability Views (Owner A)
# ---------------------------------------------------------------------------


@require_GET
@role_required("manager")
def manager_hotel_bookings_list_view(request, hotel_id):
    """List bookings for a manager's own hotel with optional status and date filters."""
    hotel = Hotel.objects.filter(id=hotel_id, owner=request.user).first()
    if not hotel:
        return json_error("Hotel not found.", status=404)

    form = ManagerBookingFilterForm(request.GET)
    if not form.is_valid():
        return json_error("Invalid filter parameters", errors=form_errors(form), status=400)

    status_filter = form.cleaned_data.get("status")
    date_from = form.cleaned_data.get("date_from")
    date_to = form.cleaned_data.get("date_to")

    bookings_qs = (
        Booking.objects.filter(room_type__hotel=hotel)
        .select_related("guest", "room_type", "discount_code")
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

    return json_ok([booking_to_dict(b) for b in bookings_qs])


@require_GET
@role_required("manager")
def manager_hotel_availability_view(request, hotel_id):
    """Return availability breakdown (total, reserved, free) per room type per day for a manager's own hotel."""
    hotel = Hotel.objects.filter(id=hotel_id, owner=request.user).first()
    if not hotel:
        return json_error("Hotel not found.", status=404)

    form = ManagerAvailabilityFilterForm(request.GET)
    if not form.is_valid():
        return json_error("Invalid date parameters", errors=form_errors(form), status=400)

    date_from = form.cleaned_data["date_from"]
    date_to = form.cleaned_data["date_to"]

    room_types = list(hotel.room_types.all().order_by("price_per_night"))
    if not room_types:
        return json_ok([])

    # Query all confirmed overlapping bookings within the requested range
    overlapping_bookings = list(
        Booking.objects.filter(
            room_type__in=room_types,
            status=Booking.Status.CONFIRMED,
            check_in__lt=date_to,
            check_out__gt=date_from,
        )
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

    return json_ok(results)
