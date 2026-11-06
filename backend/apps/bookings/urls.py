"""URL routing configuration for guest bookings and discounts."""

from django.urls import path

from apps.bookings.views import (
    booking_cancel_view,
    booking_create_view,
    discount_validate_view,
    my_bookings_list_view,
    quote_view,
)

app_name = "bookings"

urlpatterns = [
    path("bookings/quote/", quote_view, name="quote"),
    path("discounts/validate/", discount_validate_view, name="discount-validate"),
    path("bookings/", booking_create_view, name="booking-create"),
    path("bookings/mine/", my_bookings_list_view, name="bookings-mine"),
    path("bookings/<int:booking_id>/cancel/", booking_cancel_view, name="booking-cancel"),
]
