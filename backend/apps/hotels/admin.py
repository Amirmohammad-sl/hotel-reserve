from django.contrib import admin
from .models import Amenity, Hotel, RoomType


class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1
    fields = ("title", "capacity", "price_per_night", "quantity")


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


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
    list_filter = ("is_active", "city", "star_rating")
    search_fields = ("name", "city", "owner__username", "owner__email")
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
    list_filter = ("hotel", "capacity")
    search_fields = ("title", "hotel__name")
    filter_horizontal = ("amenities",)
