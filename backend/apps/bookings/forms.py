"""Forms and serializers for bookings, availability, and discount codes (guest and manager)."""

from typing import Any, Dict, Optional
from django import forms
from django.utils import timezone

from apps.bookings.models import Booking, DiscountCode
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


class DiscountCodeForm(forms.ModelForm):
    """Form for hotel manager creating or updating a DiscountCode."""

    class Meta:
        model = DiscountCode
        fields = [
            "code",
            "percent",
            "valid_from",
            "valid_to",
            "max_uses",
            "is_active",
        ]

    def __init__(self, *args, hotel=None, **kwargs):
        self.hotel = hotel or (kwargs.get("instance").hotel if kwargs.get("instance") else None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data.get("code", "")
        if code:
            code = code.strip().upper()
        if not code:
            raise forms.ValidationError("Discount code is required.")
        return code

    def clean_percent(self):
        percent = self.cleaned_data.get("percent")
        if percent is None or percent < 1 or percent > 100:
            raise forms.ValidationError("Percent must be between 1 and 100.")
        return percent

    def clean_max_uses(self):
        max_uses = self.cleaned_data.get("max_uses")
        if max_uses is not None and max_uses < 1:
            raise forms.ValidationError("max_uses must be at least 1.")
        return max_uses

    def clean_is_active(self):
        if "is_active" not in self.data:
            if self.instance and self.instance.pk:
                return self.instance.is_active
            return True
        return self.cleaned_data.get("is_active", True)

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("code")
        valid_from = cleaned_data.get("valid_from")
        valid_to = cleaned_data.get("valid_to")

        if valid_from and valid_to and valid_to < valid_from:
            self.add_error("valid_to", "valid_to must be greater than or equal to valid_from.")

        if code and self.hotel:
            qs = DiscountCode.objects.filter(hotel=self.hotel, code__iexact=code)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("code", "A discount code with this code already exists for this hotel.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.hotel and not getattr(instance, "hotel_id", None):
            instance.hotel = self.hotel
        if commit:
            instance.save()
        return instance


class ManagerAvailabilityFilterForm(forms.Form):
    """Validate query parameters for manager hotel availability calendar."""

    date_from = forms.DateField(required=True, input_formats=["%Y-%m-%d"])
    date_to = forms.DateField(required=True, input_formats=["%Y-%m-%d"])

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to:
            if date_to <= date_from:
                self.add_error("date_to", "date_to must be strictly after date_from.")
            elif (date_to - date_from).days > 90:
                self.add_error("date_to", "Date range cannot exceed 90 days.")

        return cleaned_data


class ManagerBookingFilterForm(forms.Form):
    """Validate optional query parameters for manager hotel bookings listing."""

    status = forms.ChoiceField(
        choices=[("", "All")] + list(Booking.Status.choices),
        required=False,
    )
    date_from = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    date_to = forms.DateField(required=False, input_formats=["%Y-%m-%d"])

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to and date_to < date_from:
            self.add_error("date_to", "date_to must be greater than or equal to date_from.")

        return cleaned_data


def discount_code_to_dict(discount_code: DiscountCode) -> Dict[str, Any]:
    """Serialize DiscountCode model instance to JSON-serializable dictionary."""
    return {
        "id": discount_code.id,
        "hotel_id": discount_code.hotel_id,
        "code": discount_code.code,
        "percent": discount_code.percent,
        "valid_from": discount_code.valid_from.isoformat() if discount_code.valid_from else None,
        "valid_to": discount_code.valid_to.isoformat() if discount_code.valid_to else None,
        "max_uses": discount_code.max_uses,
        "used_count": discount_code.used_count,
        "is_active": discount_code.is_active,
        "created_at": discount_code.created_at.isoformat() if discount_code.created_at else None,
    }


def booking_to_dict(booking: Booking) -> Dict[str, Any]:
    """Serialize Booking model instance to JSON-serializable dictionary."""
    guest_data = None
    if getattr(booking, "guest", None):
        guest_data = {
            "id": booking.guest.id,
            "username": booking.guest.username,
            "email": booking.guest.email,
            "first_name": booking.guest.first_name,
            "last_name": booking.guest.last_name,
        }

    room_type_data = None
    if getattr(booking, "room_type", None):
        room_type_data = {
            "id": booking.room_type.id,
            "title": booking.room_type.title,
            "hotel_id": booking.room_type.hotel_id,
        }
        if getattr(booking.room_type, "hotel", None):
            room_type_data["hotel"] = {
                "id": booking.room_type.hotel.id,
                "name": booking.room_type.hotel.name,
                "city": booking.room_type.hotel.city,
            }

    return {
        "id": booking.id,
        "guest": guest_data,
        "room_type": room_type_data,
        "check_in": booking.check_in.isoformat() if booking.check_in else None,
        "check_out": booking.check_out.isoformat() if booking.check_out else None,
        "rooms_count": booking.rooms_count,
        "guests_count": booking.guests_count,
        "nights": booking.nights,
        "price_per_night_snapshot": booking.price_per_night_snapshot,
        "subtotal": booking.subtotal,
        "discount_code": booking.discount_code.code if booking.discount_code else None,
        "discount_amount": booking.discount_amount,
        "total_price": booking.total_price,
        "status": booking.status,
        "created_at": booking.created_at.isoformat() if booking.created_at else None,
        "cancelled_at": booking.cancelled_at.isoformat() if booking.cancelled_at else None,
    }
