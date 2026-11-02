from django import forms
from django.contrib import admin
from .models import Booking, DiscountCode


class BookingAdminForm(forms.ModelForm):
    """Admin form for Booking that auto-calculates nights if omitted."""

    class Meta:
        model = Booking
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        nights = cleaned_data.get("nights")
        if check_in and check_out and check_out > check_in and not nights:
            cleaned_data["nights"] = (check_out - check_in).days
        return cleaned_data


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "hotel",
        "percent",
        "valid_from",
        "valid_to",
        "used_count",
        "max_uses",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "percent", "valid_from", "valid_to", "hotel")
    search_fields = ("code", "hotel__name")
    autocomplete_fields = ("hotel",)
    readonly_fields = ("created_at",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm
    list_display = (
        "id",
        "guest",
        "room_type",
        "check_in",
        "check_out",
        "nights",
        "rooms_count",
        "guests_count",
        "total_price",
        "status",
        "created_at",
    )
    list_filter = ("status", "check_in", "check_out", "created_at")
    search_fields = (
        "id",
        "guest__username",
        "guest__email",
        "room_type__title",
        "room_type__hotel__name",
    )
    autocomplete_fields = ("guest", "room_type", "discount_code")
    readonly_fields = ("created_at", "cancelled_at")
    date_hierarchy = "check_in"
