from django.contrib import admin
from .models import Amenity, Hotel, RoomType


class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 0
    fields = ("title", "capacity", "price_per_night", "quantity")
    show_change_link = True


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "city",
        "star_rating",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "city", "star_rating", "created_at")
    search_fields = ("name", "city", "address", "owner__username", "owner__email")
    autocomplete_fields = ("owner",)
    inlines = [RoomTypeInline]


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "hotel",
        "capacity",
        "price_per_night",
        "quantity",
        "created_at",
    )
    list_filter = ("capacity", "created_at", "hotel")
    search_fields = ("title", "hotel__name", "hotel__city")
    filter_horizontal = ("amenities",)
    autocomplete_fields = ("hotel",)
