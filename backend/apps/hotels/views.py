"""Hotel views for public search/detail and manager CRUD operations."""

import urllib.parse
from collections import defaultdict
from django.db.models import Q
from django.views.decorators.http import require_GET

from apps.bookings.models import Booking
from apps.core.decorators import role_required
from apps.core.forms import form_errors
from apps.core.http import json_error, json_ok, parse_json
from apps.hotels.forms import (
    HotelForm,
    RoomSearchForm,
    RoomTypeForm,
    SearchForm,
    amenity_to_dict,
    hotel_to_dict,
    room_type_to_dict,
)
from apps.hotels.models import Amenity, Hotel, RoomType
from apps.hotels.services import calculate_room_type_available_count


@require_GET
def cities_list_view(request):
    """Return distinct cities of active hotels."""
    cities = list(
        Hotel.objects.filter(is_active=True)
        .values_list("city", flat=True)
        .distinct()
        .order_by("city")
    )
    return json_ok(cities)


@require_GET
def hotels_list_view(request):
    """Search and filter public hotels."""
    form = SearchForm(request.GET)
    if not form.is_valid():
        return json_error("Invalid search parameters", errors=form_errors(form), status=400)

    cleaned = form.cleaned_data
    city = cleaned.get("city")
    check_in = cleaned.get("check_in")
    check_out = cleaned.get("check_out")
    guests = cleaned.get("guests") or 1
    min_price = cleaned.get("min_price")
    max_price = cleaned.get("max_price")
    q = cleaned.get("q")

    hotels_qs = Hotel.objects.filter(is_active=True).prefetch_related("room_types")

    if city:
        hotels_qs = hotels_qs.filter(city__iexact=city.strip())

    if q:
        query_val = q.strip()
        hotels_qs = hotels_qs.filter(
            Q(name__icontains=query_val)
            | Q(city__icontains=query_val)
            | Q(address__icontains=query_val)
            | Q(description__icontains=query_val)
        )

    hotels_list = list(hotels_qs)
    if not hotels_list:
        return json_ok([])

    all_room_types = [rt for h in hotels_list for rt in h.room_types.all()]

    bookings_by_room = defaultdict(list)
    if check_in and check_out and all_room_types:
        bookings = Booking.objects.filter(
            room_type__in=all_room_types,
            status=Booking.Status.CONFIRMED,
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        for b in bookings:
            bookings_by_room[b.room_type_id].append(b)

    results = []
    for hotel in hotels_list:
        rts = hotel.room_types.all()
        if not rts:
            # Hotel has no room types defined
            if not check_in and not min_price and not max_price:
                results.append(
                    {
                        "id": hotel.id,
                        "name": hotel.name,
                        "city": hotel.city,
                        "address": hotel.address,
                        "description": hotel.description,
                        "star_rating": hotel.star_rating,
                        "image_url": hotel.image_url,
                        "min_price": None,
                        "available": True,
                    }
                )
            continue

        prices = [rt.price_per_night for rt in rts]
        hotel_min_price = min(prices) if prices else None

        # Filter room types by capacity and price
        matching_room_types = []
        for rt in rts:
            if rt.capacity < guests:
                continue
            if min_price is not None and rt.price_per_night < min_price:
                continue
            if max_price is not None and rt.price_per_night > max_price:
                continue

            if check_in and check_out:
                avail_count = calculate_room_type_available_count(
                    rt,
                    check_in,
                    check_out,
                    bookings_by_room[rt.id],
                )
                if avail_count >= 1:
                    matching_room_types.append(rt)
            else:
                matching_room_types.append(rt)

        if check_in and check_out:
            # DoD: Searching with dates excludes hotels with no room type available
            if not matching_room_types:
                continue
            is_available = True
        else:
            if (min_price is not None or max_price is not None or guests > 1) and not matching_room_types:
                continue
            is_available = True

        results.append(
            {
                "id": hotel.id,
                "name": hotel.name,
                "city": hotel.city,
                "address": hotel.address,
                "description": hotel.description,
                "star_rating": hotel.star_rating,
                "image_url": hotel.image_url,
                "min_price": hotel_min_price,
                "available": is_available,
            }
        )

    response = json_ok(results)
    if city:
        response.set_cookie(
            "last_city",
            urllib.parse.quote(city.strip()),
            max_age=30 * 24 * 3600,
            samesite="Lax",
        )
    return response


@require_GET
def recent_hotels_view(request):
    """Return recently viewed hotels stored in user session."""
    recent_ids = request.session.get("recent_hotel_ids", [])
    if not recent_ids:
        return json_ok([])

    hotels = (
        Hotel.objects.filter(id__in=recent_ids, is_active=True)
        .prefetch_related("room_types")
    )
    hotels_by_id = {h.id: h for h in hotels}

    results = []
    for hid in recent_ids:
        hotel = hotels_by_id.get(hid)
        if not hotel:
            continue
        rts = hotel.room_types.all()
        prices = [rt.price_per_night for rt in rts]
        min_price = min(prices) if prices else None
        results.append(
            {
                "id": hotel.id,
                "name": hotel.name,
                "city": hotel.city,
                "address": hotel.address,
                "description": hotel.description,
                "star_rating": hotel.star_rating,
                "image_url": hotel.image_url,
                "min_price": min_price,
                "available": True,
            }
        )

    return json_ok(results)


@require_GET
def hotel_detail_view(request, hotel_id):
    """Return hotel detail with room types and amenities."""
    hotel = (
        Hotel.objects.filter(id=hotel_id, is_active=True)
        .prefetch_related("room_types__amenities")
        .first()
    )
    if not hotel:
        return json_error("Hotel not found", status=404)

    # Track recently viewed hotel id in session (LRU list, max 10)
    recent_ids = list(request.session.get("recent_hotel_ids", []))
    if hotel_id in recent_ids:
        recent_ids.remove(hotel_id)
    recent_ids.insert(0, hotel_id)
    request.session["recent_hotel_ids"] = recent_ids[:10]
    request.session.modified = True

    room_types_data = [
        {
            "id": rt.id,
            "title": rt.title,
            "description": rt.description,
            "capacity": rt.capacity,
            "price_per_night": rt.price_per_night,
            "quantity": rt.quantity,
            "amenities": [
                {"id": a.id, "name": a.name, "description": a.description}
                for a in rt.amenities.all()
            ],
        }
        for rt in hotel.room_types.all()
    ]

    data = {
        "id": hotel.id,
        "name": hotel.name,
        "city": hotel.city,
        "address": hotel.address,
        "description": hotel.description,
        "star_rating": hotel.star_rating,
        "latitude": float(hotel.latitude) if hotel.latitude is not None else None,
        "longitude": float(hotel.longitude) if hotel.longitude is not None else None,
        "image_url": hotel.image_url,
        "room_types": room_types_data,
    }
    return json_ok(data)


@require_GET
def hotel_rooms_view(request, hotel_id):
    """Return room types of a hotel with available_count for given dates and guests."""
    hotel = Hotel.objects.filter(id=hotel_id, is_active=True).first()
    if not hotel:
        return json_error("Hotel not found", status=404)

    form = RoomSearchForm(request.GET)
    if not form.is_valid():
        return json_error("Invalid parameters", errors=form_errors(form), status=400)

    check_in = form.cleaned_data.get("check_in")
    check_out = form.cleaned_data.get("check_out")
    guests = form.cleaned_data.get("guests") or 1

    room_types = list(hotel.room_types.prefetch_related("amenities").all())

    bookings_by_room = defaultdict(list)
    if check_in and check_out and room_types:
        bookings = Booking.objects.filter(
            room_type__in=room_types,
            status=Booking.Status.CONFIRMED,
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        for b in bookings:
            bookings_by_room[b.room_type_id].append(b)

    rooms_data = []
    for rt in room_types:
        avail_count = calculate_room_type_available_count(
            rt,
            check_in,
            check_out,
            bookings_by_room[rt.id],
        )
        is_available = avail_count >= 1 and rt.capacity >= guests

        rooms_data.append(
            {
                "id": rt.id,
                "title": rt.title,
                "description": rt.description,
                "capacity": rt.capacity,
                "price_per_night": rt.price_per_night,
                "quantity": rt.quantity,
                "available_count": avail_count,
                "available": is_available,
                "amenities": [
                    {"id": a.id, "name": a.name, "description": a.description}
                    for a in rt.amenities.all()
                ],
            }
        )

    return json_ok(rooms_data)


@require_GET
def room_detail_view(request, room_id):
    """Return room type detail with hotel summary and amenities."""
    room_type = (
        RoomType.objects.select_related("hotel")
        .prefetch_related("amenities")
        .filter(id=room_id, hotel__is_active=True)
        .first()
    )
    if not room_type:
        return json_error("Room type not found", status=404)

    data = {
        "id": room_type.id,
        "title": room_type.title,
        "description": room_type.description,
        "capacity": room_type.capacity,
        "price_per_night": room_type.price_per_night,
        "quantity": room_type.quantity,
        "hotel": {
            "id": room_type.hotel.id,
            "name": room_type.hotel.name,
            "city": room_type.hotel.city,
            "address": room_type.hotel.address,
            "star_rating": room_type.hotel.star_rating,
            "image_url": room_type.hotel.image_url,
        },
        "amenities": [
            {"id": a.id, "name": a.name, "description": a.description}
            for a in room_type.amenities.all()
        ],
    }
    return json_ok(data)


# ---------------------------------------------------------------------------
# Amenities Catalogue
# ---------------------------------------------------------------------------


@require_GET
def amenities_list_view(request):
    """Return list of all amenities for forms and displays."""
    amenities = Amenity.objects.all().order_by("name")
    return json_ok([amenity_to_dict(a) for a in amenities])


# ---------------------------------------------------------------------------
# Manager Views (Owner A)
# ---------------------------------------------------------------------------


@role_required("manager")
def manager_hotels_list_create_view(request):
    """List manager's own hotels (GET) or create a new hotel (POST)."""
    if request.method == "GET":
        hotels = Hotel.objects.filter(owner=request.user).order_by("-created_at")
        return json_ok([hotel_to_dict(h) for h in hotels])

    if request.method == "POST":
        try:
            data = parse_json(request)
        except ValueError as exc:
            return json_error(str(exc), status=400)

        form = HotelForm(data)
        if not form.is_valid():
            return json_error("Validation failed", errors=form_errors(form), status=400)

        hotel = form.save(commit=False)
        hotel.owner = request.user
        hotel.save()
        return json_ok(hotel_to_dict(hotel), status=201)

    return json_error("Method not allowed", status=405)


@role_required("manager")
def manager_hotel_detail_update_delete_view(request, hotel_id):
    """Retrieve (GET), update (PUT/PATCH), or delete (DELETE) a manager's own hotel."""
    hotel = Hotel.objects.filter(id=hotel_id, owner=request.user).first()
    if not hotel:
        return json_error("Hotel not found.", status=404)

    if request.method == "GET":
        return json_ok(hotel_to_dict(hotel, include_room_types=True))

    if request.method in ("PUT", "PATCH"):
        try:
            data = parse_json(request)
        except ValueError as exc:
            return json_error(str(exc), status=400)

        form = HotelForm(data, instance=hotel)
        if not form.is_valid():
            return json_error("Validation failed", errors=form_errors(form), status=400)

        hotel = form.save()
        return json_ok(hotel_to_dict(hotel, include_room_types=True))

    if request.method == "DELETE":
        hotel.delete()
        return json_ok({"message": "Hotel deleted successfully."})

    return json_error("Method not allowed", status=405)


@role_required("manager")
def manager_room_types_list_create_view(request, hotel_id):
    """List room types (GET) or create a room type (POST) for a manager's own hotel."""
    hotel = Hotel.objects.filter(id=hotel_id, owner=request.user).first()
    if not hotel:
        return json_error("Hotel not found.", status=404)

    if request.method == "GET":
        room_types = (
            hotel.room_types.prefetch_related("amenities")
            .all()
            .order_by("price_per_night")
        )
        return json_ok([room_type_to_dict(rt) for rt in room_types])

    if request.method == "POST":
        try:
            data = parse_json(request)
        except ValueError as exc:
            return json_error(str(exc), status=400)

        form = RoomTypeForm(data, hotel=hotel)
        if not form.is_valid():
            return json_error("Validation failed", errors=form_errors(form), status=400)

        room_type = form.save()
        return json_ok(room_type_to_dict(room_type), status=201)

    return json_error("Method not allowed", status=405)


@role_required("manager")
def manager_room_type_detail_update_delete_view(request, room_type_id):
    """Retrieve (GET), update (PUT/PATCH), or delete (DELETE) a manager's own room type."""
    room_type = (
        RoomType.objects.select_related("hotel")
        .prefetch_related("amenities")
        .filter(id=room_type_id, hotel__owner=request.user)
        .first()
    )
    if not room_type:
        return json_error("Room type not found.", status=404)

    if request.method == "GET":
        return json_ok(room_type_to_dict(room_type))

    if request.method in ("PUT", "PATCH"):
        try:
            data = parse_json(request)
        except ValueError as exc:
            return json_error(str(exc), status=400)

        form = RoomTypeForm(data, instance=room_type, hotel=room_type.hotel)
        if not form.is_valid():
            return json_error("Validation failed", errors=form_errors(form), status=400)

        room_type = form.save()
        return json_ok(room_type_to_dict(room_type))

    if request.method == "DELETE":
        room_type.delete()
        return json_ok({"message": "Room type deleted successfully."})

    return json_error("Method not allowed", status=405)
