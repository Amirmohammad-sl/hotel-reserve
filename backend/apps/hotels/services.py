"""Availability calculation services for hotels and room types."""

from datetime import timedelta
from typing import Dict, List, Optional
from django.db.models import Min, Q
from apps.bookings.models import Booking


def calculate_room_type_available_count(
    room_type,
    check_in=None,
    check_out=None,
    overlapping_bookings=None,
) -> int:
    """Calculate the number of available physical rooms for a room type in [check_in, check_out).

    If check_in and check_out are not provided, returns total physical quantity.
    """
    if not check_in or not check_out:
        return room_type.quantity

    if overlapping_bookings is None:
        overlapping_bookings = list(
            Booking.objects.filter(
                room_type=room_type,
                status=Booking.Status.CONFIRMED,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
        )

    curr_day = check_in
    max_booked = 0
    while curr_day < check_out:
        booked_for_day = sum(
            b.rooms_count
            for b in overlapping_bookings
            if b.check_in <= curr_day < b.check_out
        )
        if booked_for_day > max_booked:
            max_booked = booked_for_day
        curr_day += timedelta(days=1)

    available = room_type.quantity - max_booked
    return max(0, available)
