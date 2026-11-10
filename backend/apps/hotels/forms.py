"""Forms and serializers for hotel management, search, and filtering."""

from django import forms
from django.utils import timezone

from apps.hotels.models import Amenity, Hotel, RoomType


class HotelForm(forms.ModelForm):
    """Form for manager creating or updating a Hotel."""

    class Meta:
        model = Hotel
        fields = [
            "name",
            "city",
            "address",
            "description",
            "star_rating",
            "latitude",
            "longitude",
            "image_url",
            "is_active",
        ]

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        if name:
            name = name.strip()
        if not name:
            raise forms.ValidationError("Hotel name is required.")
        return name

    def clean_city(self):
        city = self.cleaned_data.get("city", "")
        if city:
            city = city.strip()
        if not city:
            raise forms.ValidationError("City is required.")
        return city

    def clean_address(self):
        address = self.cleaned_data.get("address", "")
        if address:
            address = address.strip()
        if not address:
            raise forms.ValidationError("Address is required.")
        return address

    def clean_is_active(self):
        if "is_active" not in self.data:
            if self.instance and self.instance.pk:
                return self.instance.is_active
            return True
        return self.cleaned_data.get("is_active", True)


class RoomTypeForm(forms.ModelForm):
    """Form for manager creating or updating a RoomType."""

    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        required=False,
    )

    class Meta:
        model = RoomType
        fields = [
            "title",
            "description",
            "capacity",
            "price_per_night",
            "quantity",
            "amenities",
        ]

    def __init__(self, *args, hotel=None, **kwargs):
        self.hotel = hotel or (kwargs.get("instance").hotel if kwargs.get("instance") else None)
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        if title:
            title = title.strip()
        if not title:
            raise forms.ValidationError("Room type title is required.")
        return title

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        if title and self.hotel:
            qs = RoomType.objects.filter(hotel=self.hotel, title__iexact=title)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("title", "A room type with this title already exists in this hotel.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.hotel:
            instance.hotel = self.hotel
        if commit:
            instance.save()
            self.save_m2m()
        return instance


def amenity_to_dict(amenity: Amenity) -> dict:
    """Serialize Amenity instance to dict."""
    return {
        "id": amenity.id,
        "name": amenity.name,
        "description": amenity.description,
    }


def room_type_to_dict(room_type: RoomType) -> dict:
    """Serialize RoomType instance to dict matching API contract."""
    return {
        "id": room_type.id,
        "hotel_id": room_type.hotel_id,
        "title": room_type.title,
        "description": room_type.description,
        "capacity": room_type.capacity,
        "price_per_night": room_type.price_per_night,
        "quantity": room_type.quantity,
        "amenities": [
            amenity_to_dict(a) for a in room_type.amenities.all()
        ],
        "created_at": room_type.created_at.isoformat() if room_type.created_at else None,
    }


def hotel_to_dict(hotel: Hotel, include_room_types: bool = False) -> dict:
    """Serialize Hotel instance to dict matching API contract."""
    data = {
        "id": hotel.id,
        "owner_id": hotel.owner_id,
        "name": hotel.name,
        "city": hotel.city,
        "address": hotel.address,
        "description": hotel.description,
        "star_rating": hotel.star_rating,
        "latitude": float(hotel.latitude) if hotel.latitude is not None else None,
        "longitude": float(hotel.longitude) if hotel.longitude is not None else None,
        "image_url": hotel.image_url,
        "is_active": hotel.is_active,
        "created_at": hotel.created_at.isoformat() if hotel.created_at else None,
    }
    if include_room_types:
        data["room_types"] = [
            room_type_to_dict(rt)
            for rt in hotel.room_types.prefetch_related("amenities").all()
        ]
    return data


class SearchForm(forms.Form):
    """Validate query parameters for public hotel search."""

    city = forms.CharField(required=False, max_length=100)
    check_in = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    check_out = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    guests = forms.IntegerField(required=False, min_value=1, initial=1)
    min_price = forms.IntegerField(required=False, min_value=0)
    max_price = forms.IntegerField(required=False, min_value=0)
    q = forms.CharField(required=False, max_length=255)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")

        # Either both check_in and check_out are provided or neither
        if bool(check_in) ^ bool(check_out):
            self.add_error(
                "check_out" if check_in else "check_in",
                "Both check_in and check_out are required when filtering by dates.",
            )

        if check_in and check_out:
            today = timezone.localdate()
            if check_in < today:
                self.add_error("check_in", "Check-in date cannot be in the past.")
            if check_out <= check_in:
                self.add_error("check_out", "Check-out date must be after check-in date.")

        if min_price is not None and max_price is not None:
            if min_price > max_price:
                self.add_error("min_price", "min_price cannot exceed max_price.")

        return cleaned_data


class RoomSearchForm(forms.Form):
    """Validate query parameters for hotel room types availability check."""

    check_in = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    check_out = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    guests = forms.IntegerField(required=False, min_value=1, initial=1)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")

        if bool(check_in) ^ bool(check_out):
            self.add_error(
                "check_out" if check_in else "check_in",
                "Both check_in and check_out are required when checking availability.",
            )

        if check_in and check_out:
            today = timezone.localdate()
            if check_in < today:
                self.add_error("check_in", "Check-in date cannot be in the past.")
            if check_out <= check_in:
                self.add_error("check_out", "Check-out date must be after check-in date.")

        return cleaned_data
