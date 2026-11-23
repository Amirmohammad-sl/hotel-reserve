"""URL routing configuration for bookings app (guest and manager endpoints)."""

from django.urls import path
from apps.bookings import views

app_name = "bookings"

urlpatterns = [
    # Guest endpoints (Owner B per docs/API_CONTRACT.md)
    path("bookings/quote/", views.quote_view, name="quote"),
    path("discounts/validate/", views.discount_validate_view, name="discount-validate"),
    path("bookings/", views.booking_create_view, name="booking-create"),
    path("bookings/mine/", views.my_bookings_list_view, name="bookings-mine"),
    path("bookings/<int:booking_id>/cancel/", views.booking_cancel_view, name="booking-cancel"),

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
