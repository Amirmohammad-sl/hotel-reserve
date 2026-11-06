"""Forms and serializers for guest bookings and discount validations."""

from typing import Any, Dict
from django import forms
from django.utils import timezone

from apps.bookings.models import Booking
from apps.hotels.models import Hotel, RoomType


class BookingQuoteForm(forms.Form):
    """Form to validate booking quote and booking creation payload."""

    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.filter(hotel__is_active=True).select_related("hotel"),
        error_messages={
            "required": "Room type is required.",
            "invalid_choice": "Selected room type does not exist or is inactive.",
        },
    )
    check_in = forms.DateField(
        error_messages={
            "required": "Check-in date is required.",
            "invalid": "Enter a valid date in YYYY-MM-DD format.",
        }
    )
    check_out = forms.DateField(
        error_messages={
            "required": "Check-out date is required.",
            "invalid": "Enter a valid date in YYYY-MM-DD format.",
        }
    )
    rooms_count = forms.IntegerField(
        min_value=1,
        initial=1,
        required=False,
        error_messages={
            "min_value": "Rooms count must be at least 1.",
            "invalid": "Rooms count must be an integer.",
        },
    )
    guests_count = forms.IntegerField(
        min_value=1,
        initial=1,
        required=False,
        error_messages={
            "min_value": "Guests count must be at least 1.",
            "invalid": "Guests count must be an integer.",
        },
    )
    discount_code = forms.CharField(
        max_length=50,
        required=False,
        strip=True,
    )

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        rooms_count = cleaned_data.get("rooms_count") or 1
        guests_count = cleaned_data.get("guests_count") or 1
        cleaned_data["rooms_count"] = rooms_count
        cleaned_data["guests_count"] = guests_count

        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        today = timezone.localdate()

        if check_in and check_in < today:
            self.add_error("check_in", "Check-in date cannot be in the past.")

        if check_in and check_out and check_out <= check_in:
            self.add_error(
                "check_out",
                "Check-out date must be strictly after check-in date.",
            )

        room_type = cleaned_data.get("room_type")
        if room_type and rooms_count:
            total_capacity = room_type.capacity * rooms_count
            if guests_count > total_capacity:
                self.add_error(
                    "guests_count",
                    f"Total guests ({guests_count}) exceed the capacity of {rooms_count} room(s) (max {total_capacity} guests).",
                )

        discount_code = cleaned_data.get("discount_code")
        if discount_code:
            cleaned_data["discount_code"] = discount_code.strip().upper()

        return cleaned_data


class DiscountValidateForm(forms.Form):
    """Form to validate discount code validation request payload."""

    hotel = forms.ModelChoiceField(
        queryset=Hotel.objects.filter(is_active=True),
        error_messages={
            "required": "Hotel ID is required.",
            "invalid_choice": "Selected hotel does not exist or is inactive.",
        },
    )
    code = forms.CharField(
        max_length=50,
        required=True,
        strip=True,
        error_messages={
            "required": "Discount code is required.",
        },
    )

    def clean_code(self) -> str:
        code = self.cleaned_data.get("code", "")
        return code.strip().upper()


def booking_to_dict(booking: Booking) -> Dict[str, Any]:
    """Serialize a Booking model instance into JSON-friendly dictionary."""
    return {
        "id": booking.id,
        "room_type": {
            "id": booking.room_type.id,
            "title": booking.room_type.title,
            "hotel": {
                "id": booking.room_type.hotel.id,
                "name": booking.room_type.hotel.name,
                "city": booking.room_type.hotel.city,
            },
        },
        "check_in": booking.check_in.isoformat(),
        "check_out": booking.check_out.isoformat(),
        "rooms_count": booking.rooms_count,
        "guests_count": booking.guests_count,
        "nights": booking.nights,
        "price_per_night_snapshot": booking.price_per_night_snapshot,
        "subtotal": booking.subtotal,
        "discount_code": booking.discount_code.code if booking.discount_code else None,
        "discount_amount": booking.discount_amount,
        "total_price": booking.total_price,
        "status": booking.status,
        "created_at": booking.created_at.isoformat(),
        "cancelled_at": booking.cancelled_at.isoformat() if booking.cancelled_at else None,
    }
