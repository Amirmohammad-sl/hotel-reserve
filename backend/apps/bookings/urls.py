"""URL configuration for bookings app."""

from django.urls import path
from apps.bookings import views

app_name = "bookings"

urlpatterns = [
    # Manager endpoints (Owner A per docs/API_CONTRACT.md)
    path(
        "manager/hotels/<int:hotel_id>/discounts/",
        views.manager_discounts_list_create_view,
        name="manager_hotel_discounts",
    ),
    path(
        "manager/discounts/<int:discount_id>/",
        views.manager_discount_detail_update_delete_view,
        name="manager_discount_detail",
    ),
    path(
        "manager/hotels/<int:hotel_id>/bookings/",
        views.manager_hotel_bookings_list_view,
        name="manager_hotel_bookings",
    ),
    path(
        "manager/hotels/<int:hotel_id>/availability/",
        views.manager_hotel_availability_view,
        name="manager_hotel_availability",
    ),
]
