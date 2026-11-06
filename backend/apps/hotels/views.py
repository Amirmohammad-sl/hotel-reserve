"""Public hotel search and detail views."""

from collections import defaultdict
from django.db.models import Q
from django.views.decorators.http import require_GET

from apps.core.forms import form_errors
from apps.core.http import json_error, json_ok
from apps.bookings.models import Booking
from apps.hotels.forms import RoomSearchForm, SearchForm
from apps.hotels.models import Hotel, RoomType
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
