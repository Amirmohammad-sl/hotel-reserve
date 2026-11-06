from django.urls import path
from apps.hotels import views

app_name = "hotels"

urlpatterns = [
    path("cities/", views.cities_list_view, name="cities_list"),
    path("hotels/", views.hotels_list_view, name="hotels_list"),
    path("hotels/<int:hotel_id>/", views.hotel_detail_view, name="hotel_detail"),
    path("hotels/<int:hotel_id>/rooms/", views.hotel_rooms_view, name="hotel_rooms"),
    path("rooms/<int:room_id>/", views.room_detail_view, name="room_detail"),
]
