from django.urls import path
from apps.hotels import views

app_name = "hotels"

urlpatterns = [
    # Public browsing
    path("cities/", views.cities_list_view, name="cities_list"),
    path("hotels/", views.hotels_list_view, name="hotels_list"),
    path("hotels/<int:hotel_id>/", views.hotel_detail_view, name="hotel_detail"),
    path("hotels/<int:hotel_id>/rooms/", views.hotel_rooms_view, name="hotel_rooms"),
    path("rooms/<int:room_id>/", views.room_detail_view, name="room_detail"),

    # Amenities catalogue (for forms and displays)
    path("amenities/", views.amenities_list_view, name="amenities_list"),

    # Manager endpoints
    path("manager/hotels/", views.manager_hotels_list_create_view, name="manager_hotels_list_create"),
    path("manager/hotels/<int:hotel_id>/", views.manager_hotel_detail_update_delete_view, name="manager_hotel_detail"),
    path("manager/hotels/<int:hotel_id>/room-types/", views.manager_room_types_list_create_view, name="manager_room_types_list_create"),
    path("manager/room-types/<int:room_type_id>/", views.manager_room_type_detail_update_delete_view, name="manager_room_type_detail"),
]
