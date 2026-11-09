import json
from datetime import date, timedelta
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.bookings.models import Booking
from apps.hotels.forms import RoomSearchForm, SearchForm
from apps.hotels.services import calculate_room_type_available_count
from .admin import AmenityAdmin, HotelAdmin, RoomTypeAdmin, RoomTypeInline
from .models import Amenity, Hotel, RoomType

User = get_user_model()

# Compatibility fix for Python 3.15+ with Django 5.x template context copy in tests
try:
    from django.template.context import BaseContext, Context
    Context().__copy__()
except AttributeError:
    def _patched_copy(self):
        duplicate = object.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _patched_copy


class HotelModelsTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="test_manager",
            email="manager@hotel.com",
            password="securepassword123",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.wifi = Amenity.objects.create(name="WiFi", description="High-speed internet")
        self.pool = Amenity.objects.create(name="Swimming Pool", description="Indoor heated pool")

    def test_amenity_creation_and_str(self):
        self.assertEqual(str(self.wifi), "WiFi")
        with self.assertRaises(IntegrityError):
            Amenity.objects.create(name="WiFi")

    def test_hotel_creation_and_str(self):
        hotel = Hotel.objects.create(
            owner=self.manager,
            name="Grand Hotel",
            city="Tehran",
            address="Valiasr Ave.",
            star_rating=5,
        )
        self.assertEqual(str(hotel), "Grand Hotel (Tehran)")
        self.assertTrue(hotel.is_active)
        self.assertEqual(hotel.owner, self.manager)
        self.assertIn(hotel, self.manager.hotels.all())

    def test_room_type_creation_with_amenities(self):
        hotel = Hotel.objects.create(
            owner=self.manager,
            name="Espinas Palace",
            city="Tehran",
            address="Saadat Abad",
        )
        room_type = RoomType.objects.create(
            hotel=hotel,
            title="Deluxe Suite",
            capacity=2,
            price_per_night=2500000,
            quantity=5,
        )
        room_type.amenities.add(self.wifi, self.pool)

        self.assertEqual(str(room_type), "Espinas Palace - Deluxe Suite")
        self.assertEqual(room_type.amenities.count(), 2)
        self.assertIn(room_type, hotel.room_types.all())

    def test_room_type_unique_title_per_hotel(self):
        hotel = Hotel.objects.create(
            owner=self.manager,
            name="Parsian Hotel",
            city="Isfahan",
            address="Chaharbagh",
        )
        RoomType.objects.create(
            hotel=hotel,
            title="Standard Double",
            capacity=2,
            price_per_night=1500000,
            quantity=3,
        )
        with self.assertRaises(IntegrityError):
            RoomType.objects.create(
                hotel=hotel,
                title="Standard Double",
                capacity=2,
                price_per_night=1600000,
                quantity=2,
            )

    def test_same_room_title_in_different_hotels_allowed(self):
        hotel1 = Hotel.objects.create(
            owner=self.manager,
            name="Hotel A",
            city="Shiraz",
            address="Zand St.",
        )
        hotel2 = Hotel.objects.create(
            owner=self.manager,
            name="Hotel B",
            city="Shiraz",
            address="Eram St.",
        )
        r1 = RoomType.objects.create(
            hotel=hotel1,
            title="Deluxe Room",
            capacity=2,
            price_per_night=2000000,
            quantity=4,
        )
        r2 = RoomType.objects.create(
            hotel=hotel2,
            title="Deluxe Room",
            capacity=2,
            price_per_night=2200000,
            quantity=3,
        )
        self.assertEqual(r1.title, r2.title)
        self.assertNotEqual(r1.hotel, r2.hotel)


class HotelAdminTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_hotel",
            email="admin_hotel@example.com",
            password="adminpassword123",
        )
        self.client.login(username="admin_hotel", password="adminpassword123")

    def test_admin_registration_and_configuration(self):
        self.assertIn(Amenity, site._registry)
        self.assertIn(Hotel, site._registry)
        self.assertIn(RoomType, site._registry)

        amenity_admin = site._registry[Amenity]
        self.assertIsInstance(amenity_admin, AmenityAdmin)
        self.assertIn("name", amenity_admin.list_display)
        self.assertIn("created_at", amenity_admin.list_filter)
        self.assertIn("name", amenity_admin.search_fields)

        hotel_admin = site._registry[Hotel]
        self.assertIsInstance(hotel_admin, HotelAdmin)
        self.assertIn("name", hotel_admin.list_display)
        self.assertIn("city", hotel_admin.list_filter)
        self.assertIn("name", hotel_admin.search_fields)
        self.assertEqual(hotel_admin.inlines, [RoomTypeInline])
        self.assertIn("owner", hotel_admin.autocomplete_fields)

        room_type_admin = site._registry[RoomType]
        self.assertIsInstance(room_type_admin, RoomTypeAdmin)
        self.assertIn("title", room_type_admin.list_display)
        self.assertIn("capacity", room_type_admin.list_filter)
        self.assertIn("title", room_type_admin.search_fields)
        self.assertIn("amenities", room_type_admin.filter_horizontal)
        self.assertIn("hotel", room_type_admin.autocomplete_fields)

    def test_admin_changelist_views_render_successfully(self):
        for model_name in ["amenity", "hotel", "roomtype"]:
            url = reverse(f"admin:hotels_{model_name}_changelist")
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                200,
                f"Changelist for hotels.{model_name} returned status {response.status_code}",
            )


class HotelFormsTestCase(TestCase):
    def test_search_form_valid(self):
        today = timezone.localdate()
        form = SearchForm(
            data={
                "city": "Tehran",
                "check_in": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "check_out": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                "guests": 2,
                "min_price": 1000000,
                "max_price": 5000000,
                "q": "Grand",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_search_form_missing_one_date(self):
        today = timezone.localdate()
        form = SearchForm(data={"check_in": (today + timedelta(days=1)).strftime("%Y-%m-%d")})
        self.assertFalse(form.is_valid())
        self.assertIn("check_out", form.errors)

    def test_search_form_past_check_in(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        tomorrow = timezone.localdate() + timedelta(days=1)
        form = SearchForm(
            data={
                "check_in": yesterday.strftime("%Y-%m-%d"),
                "check_out": tomorrow.strftime("%Y-%m-%d"),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("check_in", form.errors)

    def test_search_form_check_out_not_after_check_in(self):
        today = timezone.localdate()
        form = SearchForm(
            data={
                "check_in": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                "check_out": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("check_out", form.errors)

    def test_search_form_min_price_greater_than_max_price(self):
        form = SearchForm(data={"min_price": 5000, "max_price": 1000})
        self.assertFalse(form.is_valid())
        self.assertIn("min_price", form.errors)

    def test_room_search_form_valid(self):
        today = timezone.localdate()
        form = RoomSearchForm(
            data={
                "check_in": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "check_out": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                "guests": 3,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)


class RoomAvailabilityCalculationTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="mgr_avail",
            email="mgr_avail@hotel.com",
            password="pass",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.guest = User.objects.create_user(
            username="guest_avail",
            email="guest_avail@hotel.com",
            password="pass",
            role=User.Role.GUEST,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="Avail Hotel",
            city="Isfahan",
            address="Abbasi St.",
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            title="Double Room",
            capacity=2,
            price_per_night=1000000,
            quantity=3,
        )

    def test_availability_without_bookings(self):
        today = timezone.localdate()
        avail = calculate_room_type_available_count(
            self.room_type,
            check_in=today + timedelta(days=1),
            check_out=today + timedelta(days=4),
        )
        self.assertEqual(avail, 3)

    def test_availability_with_confirmed_overlapping_bookings(self):
        today = timezone.localdate()
        d1 = today + timedelta(days=1)
        d3 = today + timedelta(days=3)
        d5 = today + timedelta(days=5)

        # Booking 1: d1 to d3 takes 2 rooms
        Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=d1,
            check_out=d3,
            rooms_count=2,
            guests_count=2,
            price_per_night_snapshot=1000000,
            subtotal=4000000,
            total_price=4000000,
            status=Booking.Status.CONFIRMED,
        )

        # In [d1, d3), 2 rooms taken out of 3 -> available = 1
        self.assertEqual(calculate_room_type_available_count(self.room_type, d1, d3), 1)

        # In [d3, d5), 0 rooms taken -> available = 3
        self.assertEqual(calculate_room_type_available_count(self.room_type, d3, d5), 3)

        # In [d1, d5), worst day (d1-d3) has 2 rooms taken -> available = 1
        self.assertEqual(calculate_room_type_available_count(self.room_type, d1, d5), 1)

    def test_cancelled_booking_does_not_reduce_availability(self):
        today = timezone.localdate()
        d1 = today + timedelta(days=1)
        d3 = today + timedelta(days=3)

        Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=d1,
            check_out=d3,
            rooms_count=3,
            guests_count=2,
            price_per_night_snapshot=1000000,
            subtotal=6000000,
            total_price=6000000,
            status=Booking.Status.CANCELLED,
        )
        self.assertEqual(calculate_room_type_available_count(self.room_type, d1, d3), 3)


class PublicHotelViewsTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="hotel_owner",
            email="owner@hotel.com",
            password="pass",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.guest = User.objects.create_user(
            username="traveler",
            email="traveler@guest.com",
            password="pass",
            role=User.Role.GUEST,
        )
        self.wifi = Amenity.objects.create(name="Free WiFi", description="High speed")
        self.breakfast = Amenity.objects.create(name="Breakfast", description="Buffet")

        # Hotel 1 (Tehran) - active
        self.hotel1 = Hotel.objects.create(
            owner=self.manager,
            name="Tehran Grand Hotel",
            city="Tehran",
            address="Motahari St.",
            description="Luxury downtown hotel",
            star_rating=5,
            latitude=35.72,
            longitude=51.41,
            is_active=True,
        )
        self.rt1_1 = RoomType.objects.create(
            hotel=self.hotel1,
            title="Single Standard",
            capacity=1,
            price_per_night=1000000,
            quantity=2,
        )
        self.rt1_1.amenities.add(self.wifi)

        self.rt1_2 = RoomType.objects.create(
            hotel=self.hotel1,
            title="Double Deluxe",
            capacity=2,
            price_per_night=2000000,
            quantity=1,
        )
        self.rt1_2.amenities.add(self.wifi, self.breakfast)

        # Hotel 2 (Shiraz) - active
        self.hotel2 = Hotel.objects.create(
            owner=self.manager,
            name="Shiraz Boutique Hotel",
            city="Shiraz",
            address="Eram Garden Ave.",
            star_rating=4,
            is_active=True,
        )
        self.rt2 = RoomType.objects.create(
            hotel=self.hotel2,
            title="Suite Garden View",
            capacity=4,
            price_per_night=3500000,
            quantity=2,
        )

        # Hotel 3 (Tabriz) - inactive
        self.hotel3 = Hotel.objects.create(
            owner=self.manager,
            name="Tabriz Inactive Inn",
            city="Tabriz",
            address="Bazaar",
            is_active=False,
        )

    def test_cities_list_view(self):
        url = reverse("hotels:cities_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        # Should include Tehran and Shiraz, but not Tabriz (inactive)
        self.assertIn("Tehran", data)
        self.assertIn("Shiraz", data)
        self.assertNotIn("Tabriz", data)

    def test_hotels_list_no_filter(self):
        url = reverse("hotels:hotels_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 2)
        names = [h["name"] for h in data]
        self.assertIn("Tehran Grand Hotel", names)
        self.assertIn("Shiraz Boutique Hotel", names)

        # Check min_price
        h1 = next(h for h in data if h["id"] == self.hotel1.id)
        self.assertEqual(h1["min_price"], 1000000)

    def test_hotels_list_filter_city(self):
        url = reverse("hotels:hotels_list")
        res = self.client.get(url, {"city": "shiraz"})
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.hotel2.id)

    def test_hotels_list_filter_q(self):
        url = reverse("hotels:hotels_list")
        res = self.client.get(url, {"q": "boutique"})
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.hotel2.id)

    def test_hotels_list_filter_price_range(self):
        url = reverse("hotels:hotels_list")
        # rt1_1: 1M, rt1_2: 2M, rt2: 3.5M
        res = self.client.get(url, {"min_price": 1500000, "max_price": 2500000})
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.hotel1.id)

    def test_hotels_list_with_dates_excludes_fully_booked_hotels(self):
        """DoD requirement: searching with dates excludes hotels with no room type available."""
        today = timezone.localdate()
        d_in = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        d_out = (today + timedelta(days=4)).strftime("%Y-%m-%d")

        # Fully book hotel2's only room type (quantity 2)
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt2,
            check_in=today + timedelta(days=2),
            check_out=today + timedelta(days=4),
            rooms_count=2,
            guests_count=4,
            price_per_night_snapshot=3500000,
            subtotal=14000000,
            total_price=14000000,
            status=Booking.Status.CONFIRMED,
        )

        url = reverse("hotels:hotels_list")
        res = self.client.get(url, {"check_in": d_in, "check_out": d_out})
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")

        # hotel1 has available rooms -> included
        # hotel2 is fully booked -> excluded
        hotel_ids = [h["id"] for h in data]
        self.assertIn(self.hotel1.id, hotel_ids)
        self.assertNotIn(self.hotel2.id, hotel_ids)

    def test_hotels_list_invalid_dates_return_400(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (timezone.localdate() + timedelta(days=1)).strftime("%Y-%m-%d")
        url = reverse("hotels:hotels_list")
        res = self.client.get(url, {"check_in": yesterday, "check_out": tomorrow})
        self.assertEqual(res.status_code, 400)
        self.assertIn("errors", res.json())

    def test_hotel_detail_view_success(self):
        url = reverse("hotels:hotel_detail", kwargs={"hotel_id": self.hotel1.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(data["name"], "Tehran Grand Hotel")
        self.assertEqual(len(data["room_types"]), 2)
        rt_titles = [rt["title"] for rt in data["room_types"]]
        self.assertIn("Single Standard", rt_titles)
        self.assertIn("Double Deluxe", rt_titles)

    def test_hotel_detail_view_not_found(self):
        # Inactive hotel returns 404
        url = reverse("hotels:hotel_detail", kwargs={"hotel_id": self.hotel3.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

        # Non-existent id returns 404
        url_nonexistent = reverse("hotels:hotel_detail", kwargs={"hotel_id": 99999})
        res_nonexistent = self.client.get(url_nonexistent)
        self.assertEqual(res_nonexistent.status_code, 404)

    def test_hotel_rooms_view_availability(self):
        today = timezone.localdate()
        d_in = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        d_out = (today + timedelta(days=3)).strftime("%Y-%m-%d")

        # Book 1 room of rt1_1 (quantity 2)
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt1_1,
            check_in=today + timedelta(days=1),
            check_out=today + timedelta(days=3),
            rooms_count=1,
            guests_count=1,
            price_per_night_snapshot=1000000,
            subtotal=2000000,
            total_price=2000000,
            status=Booking.Status.CONFIRMED,
        )

        url = reverse("hotels:hotel_rooms", kwargs={"hotel_id": self.hotel1.id})
        res = self.client.get(url, {"check_in": d_in, "check_out": d_out, "guests": 1})
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 2)

        rt1_1_data = next(r for r in data if r["id"] == self.rt1_1.id)
        # 1 booked out of 2 -> 1 remaining available
        self.assertEqual(rt1_1_data["available_count"], 1)
        self.assertTrue(rt1_1_data["available"])

        rt1_2_data = next(r for r in data if r["id"] == self.rt1_2.id)
        # 0 booked out of 1 -> 1 available
        self.assertEqual(rt1_2_data["available_count"], 1)
        self.assertTrue(rt1_2_data["available"])

    def test_room_detail_view_success(self):
        url = reverse("hotels:room_detail", kwargs={"room_id": self.rt1_2.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(data["title"], "Double Deluxe")
        self.assertEqual(data["capacity"], 2)
        self.assertEqual(data["hotel"]["name"], "Tehran Grand Hotel")
        amenity_names = [a["name"] for a in data["amenities"]]
        self.assertIn("Free WiFi", amenity_names)
        self.assertIn("Breakfast", amenity_names)

    def test_room_detail_view_not_found(self):
        url = reverse("hotels:room_detail", kwargs={"room_id": 99999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)


# ===========================================================================
# P2-03: Manager Hotel & Room-Type CRUD & DoD Isolation Tests
# ===========================================================================

from apps.hotels.forms import (
    HotelForm,
    RoomTypeForm,
    amenity_to_dict,
    hotel_to_dict,
    room_type_to_dict,
)


class HotelFormsTestCase(TestCase):
    """Tests for HotelForm, RoomTypeForm, and serializer helpers."""

    def setUp(self):
        self.manager = User.objects.create_user(
            username="form_manager",
            email="form_manager@hotel.com",
            password="securepassword123",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="Form Hotel",
            city="Isfahan",
            address="Chaharbagh Abbasi",
            star_rating=4,
        )
        self.wifi = Amenity.objects.create(name="WiFi", description="High-speed internet")
        self.pool = Amenity.objects.create(name="Pool", description="Indoor pool")

    def test_hotel_form_valid(self):
        form = HotelForm(
            data={
                "name": "Shiraz Boutique Hotel",
                "city": "Shiraz",
                "address": "Zand St.",
                "description": "Historical hotel",
                "star_rating": 5,
                "latitude": "29.610000",
                "longitude": "52.540000",
                "image_url": "https://example.com/hotel.jpg",
                "is_active": True,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        hotel = form.save(commit=False)
        hotel.owner = self.manager
        hotel.save()
        self.assertEqual(hotel.name, "Shiraz Boutique Hotel")
        self.assertEqual(hotel.city, "Shiraz")
        self.assertTrue(hotel.is_active)

    def test_hotel_form_required_fields_and_strip(self):
        form = HotelForm(data={"name": "   ", "city": " ", "address": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("city", form.errors)
        self.assertIn("address", form.errors)

    def test_hotel_form_star_rating_range(self):
        form_high = HotelForm(
            data={"name": "H", "city": "C", "address": "A", "star_rating": 6}
        )
        self.assertFalse(form_high.is_valid())
        self.assertIn("star_rating", form_high.errors)

        form_zero = HotelForm(
            data={"name": "H", "city": "C", "address": "A", "star_rating": 0}
        )
        self.assertFalse(form_zero.is_valid())
        self.assertIn("star_rating", form_zero.errors)

    def test_hotel_form_is_active_default_and_preserve(self):
        # On create without is_active -> defaults True
        form = HotelForm(data={"name": "H", "city": "C", "address": "A"})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data["is_active"])

        # Explicitly False
        form_inactive = HotelForm(
            data={"name": "H", "city": "C", "address": "A", "is_active": False}
        )
        self.assertTrue(form_inactive.is_valid())
        self.assertFalse(form_inactive.cleaned_data["is_active"])

        # On update without is_active in data -> preserves instance is_active
        self.hotel.is_active = False
        self.hotel.save()
        form_update = HotelForm(
            data={"name": "Updated H", "city": "Isfahan", "address": "Addr"},
            instance=self.hotel,
        )
        self.assertTrue(form_update.is_valid())
        self.assertFalse(form_update.cleaned_data["is_active"])

    def test_room_type_form_valid_with_amenities(self):
        form = RoomTypeForm(
            data={
                "title": "Deluxe Suite",
                "description": "Spacious suite",
                "capacity": 3,
                "price_per_night": 2000000,
                "quantity": 5,
                "amenities": [self.wifi.id, self.pool.id],
            },
            hotel=self.hotel,
        )
        self.assertTrue(form.is_valid(), form.errors)
        rt = form.save()
        self.assertEqual(rt.hotel, self.hotel)
        self.assertEqual(rt.title, "Deluxe Suite")
        self.assertEqual(rt.amenities.count(), 2)

    def test_room_type_form_unique_title_per_hotel(self):
        RoomType.objects.create(
            hotel=self.hotel,
            title="Standard Room",
            capacity=2,
            price_per_night=1000000,
            quantity=4,
        )
        # Attempt to create room type with same title in same hotel
        form = RoomTypeForm(
            data={
                "title": "Standard Room",
                "capacity": 2,
                "price_per_night": 1200000,
                "quantity": 2,
            },
            hotel=self.hotel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_room_type_form_capacity_and_quantity_min_value(self):
        form = RoomTypeForm(
            data={
                "title": "Invalid Room",
                "capacity": 0,
                "price_per_night": 1000000,
                "quantity": 0,
            },
            hotel=self.hotel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("capacity", form.errors)
        self.assertIn("quantity", form.errors)

    def test_serializers(self):
        rt = RoomType.objects.create(
            hotel=self.hotel,
            title="King Room",
            capacity=2,
            price_per_night=1500000,
            quantity=3,
        )
        rt.amenities.add(self.wifi)

        amenity_dict = amenity_to_dict(self.wifi)
        self.assertEqual(amenity_dict["id"], self.wifi.id)
        self.assertEqual(amenity_dict["name"], "WiFi")

        rt_dict = room_type_to_dict(rt)
        self.assertEqual(rt_dict["id"], rt.id)
        self.assertEqual(rt_dict["title"], "King Room")
        self.assertEqual(len(rt_dict["amenities"]), 1)

        hotel_dict = hotel_to_dict(self.hotel, include_room_types=True)
        self.assertEqual(hotel_dict["id"], self.hotel.id)
        self.assertEqual(hotel_dict["owner_id"], self.manager.id)
        self.assertEqual(len(hotel_dict["room_types"]), 1)


class ManagerHotelsViewsTestCase(TestCase):
    """Integration tests for manager hotels and room-types CRUD endpoints and DoD isolation."""

    def setUp(self):
        self.manager_a = User.objects.create_user(
            username="manager_a",
            email="manager_a@hotel.com",
            password="securepassword123",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.manager_b = User.objects.create_user(
            username="manager_b",
            email="manager_b@hotel.com",
            password="securepassword123",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.guest = User.objects.create_user(
            username="guest_user",
            email="guest@hotel.com",
            password="securepassword123",
            role=User.Role.GUEST,
        )

        self.wifi = Amenity.objects.create(name="WiFi", description="Wireless Internet")
        self.breakfast = Amenity.objects.create(name="Breakfast", description="Buffet breakfast")

        self.hotel_a = Hotel.objects.create(
            owner=self.manager_a,
            name="Hotel A (Alpha)",
            city="Tehran",
            address="Valiasr St.",
            star_rating=5,
            is_active=True,
        )
        self.hotel_b = Hotel.objects.create(
            owner=self.manager_b,
            name="Hotel B (Beta)",
            city="Isfahan",
            address="Zayandeh Rood",
            star_rating=4,
            is_active=True,
        )

        self.rt_a = RoomType.objects.create(
            hotel=self.hotel_a,
            title="Suite Alpha",
            capacity=2,
            price_per_night=3000000,
            quantity=5,
        )
        self.rt_a.amenities.add(self.wifi)

        self.rt_b = RoomType.objects.create(
            hotel=self.hotel_b,
            title="Suite Beta",
            capacity=3,
            price_per_night=2500000,
            quantity=3,
        )
        self.rt_b.amenities.add(self.breakfast)

    # -----------------------------------------------------------------------
    # Public Amenities Catalogue
    # -----------------------------------------------------------------------
    def test_amenities_list_view_public(self):
        url = reverse("hotels:amenities_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertGreaterEqual(len(data), 2)
        names = [a["name"] for a in data]
        self.assertIn("WiFi", names)
        self.assertIn("Breakfast", names)

    # -----------------------------------------------------------------------
    # Authentication & Role Guard Checks
    # -----------------------------------------------------------------------
    def test_manager_endpoints_unauthenticated_returns_401(self):
        urls = [
            reverse("hotels:manager_hotels_list_create"),
            reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel_a.id}),
            reverse("hotels:manager_room_types_list_create", kwargs={"hotel_id": self.hotel_a.id}),
            reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": self.rt_a.id}),
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 401, f"URL {url} did not return 401 unauthenticated")

    def test_manager_endpoints_guest_role_returns_403(self):
        self.client.force_login(self.guest)
        urls = [
            reverse("hotels:manager_hotels_list_create"),
            reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel_a.id}),
            reverse("hotels:manager_room_types_list_create", kwargs={"hotel_id": self.hotel_a.id}),
            reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": self.rt_a.id}),
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 403, f"URL {url} did not return 403 for guest role")

    # -----------------------------------------------------------------------
    # Manager Hotels List & Create
    # -----------------------------------------------------------------------
    def test_manager_list_own_hotels_only(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotels_list_create")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        hotel_ids = [h["id"] for h in data]
        self.assertIn(self.hotel_a.id, hotel_ids)
        self.assertNotIn(self.hotel_b.id, hotel_ids)

    def test_manager_create_hotel_success(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotels_list_create")
        payload = {
            "name": "New Luxury Palace",
            "city": "Shiraz",
            "address": "Eram Garden Ave.",
            "description": "5-star palace hotel",
            "star_rating": 5,
            "latitude": 29.630000,
            "longitude": 52.520000,
            "image_url": "https://example.com/palace.jpg",
            "is_active": True,
        }
        res = self.client.post(url, payload, content_type="application/json")
        self.assertEqual(res.status_code, 201)
        data = res.json().get("data")
        self.assertEqual(data["name"], "New Luxury Palace")
        self.assertEqual(data["owner_id"], self.manager_a.id)
        self.assertTrue(Hotel.objects.filter(name="New Luxury Palace", owner=self.manager_a).exists())

    def test_manager_create_hotel_validation_error(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotels_list_create")
        # Missing required fields
        res = self.client.post(url, {"star_rating": 5}, content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("errors", res.json())
        errors = res.json()["errors"]
        self.assertIn("name", errors)
        self.assertIn("city", errors)
        self.assertIn("address", errors)

    def test_manager_create_hotel_invalid_json(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotels_list_create")
        res = self.client.post(url, "invalid-json-content", content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("message", res.json())

    # -----------------------------------------------------------------------
    # Manager Hotel Detail, Update, Delete
    # -----------------------------------------------------------------------
    def test_manager_get_own_hotel_detail(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(data["id"], self.hotel_a.id)
        self.assertEqual(data["name"], "Hotel A (Alpha)")
        self.assertEqual(len(data["room_types"]), 1)
        self.assertEqual(data["room_types"][0]["title"], "Suite Alpha")

    def test_manager_update_own_hotel(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel_a.id})
        payload = {
            "name": "Hotel A Renovated",
            "city": "Tehran",
            "address": "New Valiasr St.",
            "star_rating": 4,
            "is_active": False,
        }
        res = self.client.put(url, payload, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(data["name"], "Hotel A Renovated")
        self.assertFalse(data["is_active"])
        self.hotel_a.refresh_from_db()
        self.assertEqual(self.hotel_a.name, "Hotel A Renovated")
        self.assertFalse(self.hotel_a.is_active)

    def test_manager_delete_own_hotel(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel_a.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Hotel.objects.filter(id=self.hotel_a.id).exists())

    # -----------------------------------------------------------------------
    # CRITICAL DoD: Manager A cannot read/edit/delete Manager B's hotel
    # -----------------------------------------------------------------------
    def test_manager_a_cannot_read_manager_b_hotel_returns_404(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel_b.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404, "Manager A reading Manager B hotel must return 404")

    def test_manager_a_cannot_update_manager_b_hotel_returns_404(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel_b.id})
        payload = {
            "name": "Hacked Hotel Name",
            "city": "Tehran",
            "address": "Hacked",
            "is_active": False,
        }
        res = self.client.put(url, payload, content_type="application/json")
        self.assertEqual(res.status_code, 404, "Manager A updating Manager B hotel must return 404")
        self.hotel_b.refresh_from_db()
        self.assertEqual(self.hotel_b.name, "Hotel B (Beta)")

    def test_manager_a_cannot_delete_manager_b_hotel_returns_404(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel_b.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 404, "Manager A deleting Manager B hotel must return 404")
        self.assertTrue(Hotel.objects.filter(id=self.hotel_b.id).exists())

    def test_manager_a_cannot_create_room_type_for_manager_b_hotel_returns_404(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_types_list_create", kwargs={"hotel_id": self.hotel_b.id})
        payload = {
            "title": "Unauthorized Room",
            "capacity": 2,
            "price_per_night": 1000000,
            "quantity": 1,
        }
        res = self.client.post(url, payload, content_type="application/json")
        self.assertEqual(res.status_code, 404, "Creating room type on another manager's hotel must return 404")
        self.assertFalse(RoomType.objects.filter(title="Unauthorized Room").exists())

    def test_manager_a_cannot_read_manager_b_room_type_returns_404(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": self.rt_b.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404, "Manager A reading Manager B room type must return 404")

    def test_manager_a_cannot_update_manager_b_room_type_returns_404(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": self.rt_b.id})
        payload = {
            "title": "Hacked Room Type",
            "capacity": 2,
            "price_per_night": 500000,
            "quantity": 10,
        }
        res = self.client.put(url, payload, content_type="application/json")
        self.assertEqual(res.status_code, 404, "Manager A updating Manager B room type must return 404")
        self.rt_b.refresh_from_db()
        self.assertEqual(self.rt_b.title, "Suite Beta")

    def test_manager_a_cannot_delete_manager_b_room_type_returns_404(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": self.rt_b.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 404, "Manager A deleting Manager B room type must return 404")
        self.assertTrue(RoomType.objects.filter(id=self.rt_b.id).exists())

    # -----------------------------------------------------------------------
    # Manager Room Types List & Create
    # -----------------------------------------------------------------------
    def test_manager_list_own_room_types(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_types_list_create", kwargs={"hotel_id": self.hotel_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.rt_a.id)

    def test_manager_create_room_type_success(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_types_list_create", kwargs={"hotel_id": self.hotel_a.id})
        payload = {
            "title": "Presidential Suite",
            "description": "Top floor VIP suite",
            "capacity": 4,
            "price_per_night": 7000000,
            "quantity": 2,
            "amenities": [self.wifi.id, self.breakfast.id],
        }
        res = self.client.post(url, payload, content_type="application/json")
        self.assertEqual(res.status_code, 201)
        data = res.json().get("data")
        self.assertEqual(data["title"], "Presidential Suite")
        self.assertEqual(data["capacity"], 4)
        self.assertEqual(len(data["amenities"]), 2)
        self.assertTrue(RoomType.objects.filter(title="Presidential Suite", hotel=self.hotel_a).exists())

    def test_manager_create_duplicate_room_type_title_returns_400(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_types_list_create", kwargs={"hotel_id": self.hotel_a.id})
        payload = {
            "title": "Suite Alpha",  # already exists in hotel_a
            "capacity": 2,
            "price_per_night": 3500000,
            "quantity": 1,
        }
        res = self.client.post(url, payload, content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("errors", res.json())
        self.assertIn("title", res.json()["errors"])

    # -----------------------------------------------------------------------
    # Manager Room Type Detail, Update, Delete
    # -----------------------------------------------------------------------
    def test_manager_get_own_room_type(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": self.rt_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(data["id"], self.rt_a.id)
        self.assertEqual(data["title"], "Suite Alpha")

    def test_manager_update_own_room_type(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": self.rt_a.id})
        payload = {
            "title": "Suite Alpha Superior",
            "capacity": 3,
            "price_per_night": 3200000,
            "quantity": 6,
            "amenities": [self.wifi.id, self.breakfast.id],
        }
        res = self.client.put(url, payload, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(data["title"], "Suite Alpha Superior")
        self.assertEqual(data["capacity"], 3)
        self.assertEqual(len(data["amenities"]), 2)
        self.rt_a.refresh_from_db()
        self.assertEqual(self.rt_a.title, "Suite Alpha Superior")
        self.assertEqual(self.rt_a.capacity, 3)

    def test_manager_delete_own_room_type(self):
        self.client.force_login(self.manager_a)
        url = reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": self.rt_a.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(RoomType.objects.filter(id=self.rt_a.id).exists())



# ===========================================================================
# P3-07: Cookies and Recent Hotels Test Suites
# ===========================================================================
class RecentHotelsAndCookiesTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="owner_p307",
            email="owner_p307@hotel.com",
            password="pass",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.hotel1 = Hotel.objects.create(
            owner=self.manager,
            name="Tehran Grand Palace",
            city="تهران",
            address="Valiasr St.",
            description="Classic hotel in Tehran",
            star_rating=5,
            is_active=True,
        )
        self.rt1 = RoomType.objects.create(
            hotel=self.hotel1,
            title="Deluxe Suite",
            capacity=2,
            price_per_night=2500000,
            quantity=5,
        )
        self.hotel2 = Hotel.objects.create(
            owner=self.manager,
            name="Shiraz Garden Hotel",
            city="شیراز",
            address="Zand St.",
            description="Garden hotel in Shiraz",
            star_rating=4,
            is_active=True,
        )
        self.rt2 = RoomType.objects.create(
            hotel=self.hotel2,
            title="Standard Room",
            capacity=2,
            price_per_night=1800000,
            quantity=3,
        )

    def test_hotels_list_sets_last_city_cookie(self):
        url = reverse("hotels:hotels_list")
        res = self.client.get(url, {"city": "تهران"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("last_city", res.cookies)
        cookie_val = res.cookies["last_city"].value
        import urllib.parse
        self.assertEqual(urllib.parse.unquote(cookie_val), "تهران")

    def test_hotels_list_without_city_does_not_set_cookie(self):
        url = reverse("hotels:hotels_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("last_city", res.cookies)

    def test_hotel_detail_records_session_history(self):
        url1 = reverse("hotels:hotel_detail", kwargs={"hotel_id": self.hotel1.id})
        url2 = reverse("hotels:hotel_detail", kwargs={"hotel_id": self.hotel2.id})

        # Visit hotel 1
        res1 = self.client.get(url1)
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(self.client.session.get("recent_hotel_ids"), [self.hotel1.id])

        # Visit hotel 2
        res2 = self.client.get(url2)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(self.client.session.get("recent_hotel_ids"), [self.hotel2.id, self.hotel1.id])

        # Visit hotel 1 again (should move hotel 1 to top)
        res3 = self.client.get(url1)
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(self.client.session.get("recent_hotel_ids"), [self.hotel1.id, self.hotel2.id])

    def test_recent_hotels_view_empty_session(self):
        url = reverse("hotels:recent_hotels")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("data"), [])

    def test_recent_hotels_view_returns_ordered_hotels(self):
        # Visit hotel 2 then hotel 1
        url2 = reverse("hotels:hotel_detail", kwargs={"hotel_id": self.hotel2.id})
        url1 = reverse("hotels:hotel_detail", kwargs={"hotel_id": self.hotel1.id})
        self.client.get(url2)
        self.client.get(url1)

        recent_url = reverse("hotels:recent_hotels")
        res = self.client.get(recent_url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], self.hotel1.id)
        self.assertEqual(data[0]["name"], "Tehran Grand Palace")
        self.assertEqual(data[0]["min_price"], 2500000)
        self.assertEqual(data[1]["id"], self.hotel2.id)
        self.assertEqual(data[1]["name"], "Shiraz Garden Hotel")
        self.assertEqual(data[1]["min_price"], 1800000)

    def test_recent_hotels_view_ignores_inactive_hotels(self):
        url1 = reverse("hotels:hotel_detail", kwargs={"hotel_id": self.hotel1.id})
        self.client.get(url1)

        # Deactivate hotel 1
        self.hotel1.is_active = False
        self.hotel1.save()

        recent_url = reverse("hotels:recent_hotels")
        res = self.client.get(recent_url)
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 0)


# ===========================================================================
# P3-02: RoomTypeQuerySet Availability Test Suites
# ===========================================================================


class RoomTypeQuerySetAvailabilityTests(TestCase):
    """Test suite for RoomTypeQuerySet.with_availability and available_in_range (P3-02)."""

    def setUp(self):
        self.manager = User.objects.create_user(
            username="p3_hotel_mgr",
            email="p3_hotel_mgr@test.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.guest = User.objects.create_user(
            username="p3_hotel_guest",
            email="p3_hotel_guest@test.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="P3 Luxury Hotel",
            city="Tabriz",
            address="Shahgoli",
            is_active=True,
        )
        self.rt1 = RoomType.objects.create(
            hotel=self.hotel,
            title="Deluxe Double",
            capacity=2,
            price_per_night=2_500_000,
            quantity=4,
        )
        self.rt2 = RoomType.objects.create(
            hotel=self.hotel,
            title="Presidential Suite",
            capacity=4,
            price_per_night=8_000_000,
            quantity=1,
        )

    def test_with_availability_without_dates_returns_full_inventory(self):
        """When check_in or check_out is None, reserved is 0 and available_count is quantity."""
        qs = RoomType.objects.filter(hotel=self.hotel).with_availability()
        for rt in qs:
            self.assertEqual(rt.reserved, 0)
            self.assertEqual(rt.available_count, rt.quantity)

    def test_with_availability_with_confirmed_bookings(self):
        """Confirmed overlapping bookings increment reserved and decrement available_count."""
        # Book 3 rooms of rt1 from Sep 10 to Sep 15
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt1,
            check_in=date(2026, 9, 10),
            check_out=date(2026, 9, 15),
            rooms_count=3,
            guests_count=3,
            nights=5,
            price_per_night_snapshot=2_500_000,
            subtotal=37_500_000,
            total_price=37_500_000,
            status=Booking.Status.CONFIRMED,
        )

        qs = RoomType.objects.filter(hotel=self.hotel).with_availability(
            check_in=date(2026, 9, 12),
            check_out=date(2026, 9, 14),
        )
        rt1_res = qs.get(id=self.rt1.id)
        rt2_res = qs.get(id=self.rt2.id)

        # rt1: 4 total - 3 reserved = 1 available
        self.assertEqual(rt1_res.reserved, 3)
        self.assertEqual(rt1_res.available_count, 1)

        # rt2: 1 total - 0 reserved = 1 available
        self.assertEqual(rt2_res.reserved, 0)
        self.assertEqual(rt2_res.available_count, 1)

    def test_with_availability_cancelled_booking_does_not_reduce_inventory(self):
        """Cancelled bookings must not consume inventory."""
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt2,
            check_in=date(2026, 9, 10),
            check_out=date(2026, 9, 15),
            rooms_count=1,
            guests_count=2,
            nights=5,
            price_per_night_snapshot=8_000_000,
            subtotal=40_000_000,
            total_price=40_000_000,
            status=Booking.Status.CANCELLED,
        )

        qs = RoomType.objects.filter(id=self.rt2.id).with_availability(
            check_in=date(2026, 9, 10),
            check_out=date(2026, 9, 15),
        )
        rt2_res = qs.get()
        self.assertEqual(rt2_res.reserved, 0)
        self.assertEqual(rt2_res.available_count, 1)

    def test_with_availability_same_day_turnover_dod(self):
        """
        DoD: Same-day turnover (out on 5th, in on 5th) is available.
        A booking checking out on Sep 5 does not block an arrival on Sep 5.
        """
        # Book ALL 4 rooms of rt1 from Sep 1 to Sep 5
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt1,
            check_in=date(2026, 9, 1),
            check_out=date(2026, 9, 5),
            rooms_count=4,
            guests_count=4,
            nights=4,
            price_per_night_snapshot=2_500_000,
            subtotal=40_000_000,
            total_price=40_000_000,
            status=Booking.Status.CONFIRMED,
        )

        # Query for arrival on Sep 5 to Sep 10
        qs_after = RoomType.objects.filter(id=self.rt1.id).with_availability(
            check_in=date(2026, 9, 5),
            check_out=date(2026, 9, 10),
        )
        res_after = qs_after.get()
        self.assertEqual(res_after.reserved, 0, "Departing guests on 5th should not reserve morning of 5th arrival.")
        self.assertEqual(res_after.available_count, 4)

        # Query for departure on Sep 1
        qs_before = RoomType.objects.filter(id=self.rt1.id).with_availability(
            check_in=date(2026, 8, 25),
            check_out=date(2026, 9, 1),
        )
        res_before = qs_before.get()
        self.assertEqual(res_before.reserved, 0, "Arriving guests on 1st should not block departure on 1st.")
        self.assertEqual(res_before.available_count, 4)

    def test_available_in_range_filter(self):
        """available_in_range() filters room types matching requested room quantity."""
        # Book 3 rooms of rt1 (leaving 1)
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt1,
            check_in=date(2026, 11, 1),
            check_out=date(2026, 11, 5),
            rooms_count=3,
            guests_count=3,
            nights=4,
            price_per_night_snapshot=2_500_000,
            subtotal=30_000_000,
            total_price=30_000_000,
            status=Booking.Status.CONFIRMED,
        )

        # Requesting 1 room: both rt1 (1 left) and rt2 (1 left) are available
        qs_1 = RoomType.objects.filter(hotel=self.hotel).available_in_range(
            check_in=date(2026, 11, 1),
            check_out=date(2026, 11, 5),
            rooms_count=1,
        )
        self.assertEqual(qs_1.count(), 2)

        # Requesting 2 rooms: neither rt1 (only 1 left) nor rt2 (only 1 left) qualify
        qs_2 = RoomType.objects.filter(hotel=self.hotel).available_in_range(
            check_in=date(2026, 11, 1),
            check_out=date(2026, 11, 5),
            rooms_count=2,
        )
        self.assertEqual(qs_2.count(), 0)

    def test_for_hotel_and_owned_by(self):
        """RoomTypeQuerySet.for_hotel and .owned_by correctly scope room types (P3-03)."""
        other_mgr = User.objects.create_user(
            username="p3_other_hotel_mgr",
            email="p3_other_hotel_mgr@test.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        other_hotel = Hotel.objects.create(
            owner=other_mgr,
            name="Other Hotel",
            city="Tabriz",
            address="Elgoli",
            is_active=True,
        )
        other_rt = RoomType.objects.create(
            hotel=other_hotel,
            title="Single Room",
            capacity=1,
            price_per_night=1_000_000,
            quantity=2,
        )

        hotel_rts = RoomType.objects.for_hotel(self.hotel)
        self.assertIn(self.rt1, hotel_rts)
        self.assertIn(self.rt2, hotel_rts)
        self.assertNotIn(other_rt, hotel_rts)

        hotel_rts_id = RoomType.objects.for_hotel(self.hotel.id)
        self.assertIn(self.rt1, hotel_rts_id)
        self.assertNotIn(other_rt, hotel_rts_id)

        mgr_rts = RoomType.objects.owned_by(self.manager)
        self.assertIn(self.rt1, mgr_rts)
        self.assertIn(self.rt2, mgr_rts)
        self.assertNotIn(other_rt, mgr_rts)

        other_mgr_rts = RoomType.objects.owned_by(other_mgr)
        self.assertIn(other_rt, other_mgr_rts)
        self.assertNotIn(self.rt1, other_mgr_rts)



class HotelQuerySetTestCase(TestCase):
    def setUp(self):
        self.manager1 = User.objects.create_user(
            username="manager_qs_1",
            email="m_qs1@example.com",
            password="password123",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.manager2 = User.objects.create_user(
            username="manager_qs_2",
            email="m_qs2@example.com",
            password="password123",
            role=User.Role.MANAGER,
            email_verified=True,
        )

        self.hotel1 = Hotel.objects.create(
            owner=self.manager1,
            name="Tehran Grand Hotel",
            city="Tehran",
            address="Valiasr St",
            is_active=True,
        )
        self.hotel2 = Hotel.objects.create(
            owner=self.manager1,
            name="Tehran Inactive Hotel",
            city="Tehran",
            address="Enghelab St",
            is_active=False,
        )
        self.hotel3 = Hotel.objects.create(
            owner=self.manager2,
            name="Isfahan Palace",
            city="Isfahan",
            address="Chaharbagh St",
            is_active=True,
        )

        # Room types for hotel1 (min price: 100,000, max: 300,000)
        RoomType.objects.create(
            hotel=self.hotel1,
            title="Single",
            capacity=1,
            price_per_night=100000,
            quantity=5,
        )
        RoomType.objects.create(
            hotel=self.hotel1,
            title="Double",
            capacity=2,
            price_per_night=300000,
            quantity=3,
        )

        # Room types for hotel3 (min price: 500,000)
        RoomType.objects.create(
            hotel=self.hotel3,
            title="Suite",
            capacity=4,
            price_per_night=500000,
            quantity=2,
        )
        # hotel2 has no room types

    def test_active_filter(self):
        active_ids = list(Hotel.objects.active().values_list("id", flat=True))
        self.assertIn(self.hotel1.id, active_ids)
        self.assertIn(self.hotel3.id, active_ids)
        self.assertNotIn(self.hotel2.id, active_ids)

    def test_in_city_filter(self):
        # Case insensitive and stripped
        tehran_hotels = list(Hotel.objects.in_city("tehran").values_list("id", flat=True))
        self.assertCountEqual(tehran_hotels, [self.hotel1.id, self.hotel2.id])

        tehran_padded = list(Hotel.objects.in_city("  TEHRAN  ").values_list("id", flat=True))
        self.assertCountEqual(tehran_padded, [self.hotel1.id, self.hotel2.id])

        isfahan_hotels = list(Hotel.objects.in_city("Isfahan").values_list("id", flat=True))
        self.assertEqual(isfahan_hotels, [self.hotel3.id])

        # Empty/None city returns all
        self.assertEqual(Hotel.objects.in_city("").count(), 3)
        self.assertEqual(Hotel.objects.in_city(None).count(), 3)

    def test_owned_by_filter(self):
        m1_hotels = list(Hotel.objects.owned_by(self.manager1).values_list("id", flat=True))
        m2_hotels = list(Hotel.objects.owned_by(self.manager2).values_list("id", flat=True))
        self.assertCountEqual(m1_hotels, [self.hotel1.id, self.hotel2.id])
        self.assertEqual(m2_hotels, [self.hotel3.id])

    def test_with_min_price_annotation(self):
        hotels = {h.id: h.min_price for h in Hotel.objects.with_min_price()}
        self.assertEqual(hotels[self.hotel1.id], 100000)
        self.assertIsNone(hotels[self.hotel2.id])
        self.assertEqual(hotels[self.hotel3.id], 500000)

    def test_priced_between_filter(self):
        # Between 50,000 and 150,000: only hotel1 (has room at 100,000)
        qs1 = list(Hotel.objects.priced_between(50000, 150000).values_list("id", flat=True))
        self.assertEqual(qs1, [self.hotel1.id])

        # Between 400,000 and 600,000: only hotel3 (has room at 500,000)
        qs2 = list(Hotel.objects.priced_between(400000, 600000).values_list("id", flat=True))
        self.assertEqual(qs2, [self.hotel3.id])

        # Between 100,000 and 500,000: both hotel1 and hotel3
        qs3 = list(Hotel.objects.priced_between(100000, 500000).values_list("id", flat=True))
        self.assertCountEqual(qs3, [self.hotel1.id, self.hotel3.id])

        # Higher than available
        qs4 = list(Hotel.objects.priced_between(min_price=600000).values_list("id", flat=True))
        self.assertEqual(qs4, [])

        # None bounds returns all
        self.assertEqual(Hotel.objects.priced_between().count(), 3)

    def test_chained_queryset_methods(self):
        # Chaining: active + in_city + with_min_price + priced_between
        results = Hotel.objects.active().in_city("tehran").with_min_price().priced_between(50000, 200000)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.hotel1.id)
        self.assertEqual(results[0].min_price, 100000)


class GuestViewsManagerRefactorTests(TestCase):
    """Verify that guest hotel views correctly use Hotel and RoomType managers (P3-04)."""

    def setUp(self):
        self.manager = User.objects.create_user(
            username="p304_mgr",
            email="p304_mgr@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.guest = User.objects.create_user(
            username="p304_guest",
            email="p304_guest@example.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="Refactored Boutique Hotel",
            city="Isfahan",
            address="Chaharbagh Abbasi",
            star_rating=5,
            is_active=True,
        )
        self.rt_deluxe = RoomType.objects.create(
            hotel=self.hotel,
            title="Deluxe Suite",
            capacity=2,
            price_per_night=2_500_000,
            quantity=3,
        )
        self.rt_standard = RoomType.objects.create(
            hotel=self.hotel,
            title="Standard Room",
            capacity=2,
            price_per_night=1_500_000,
            quantity=2,
        )

    def test_hotels_list_annotated_min_price_and_availability(self):
        """hotels_list_view uses with_min_price and with_availability via Prefetch."""
        today = timezone.localdate()
        d_in = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        d_out = (today + timedelta(days=8)).strftime("%Y-%m-%d")

        # Book 2 of 2 Standard rooms in range
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt_standard,
            check_in=today + timedelta(days=5),
            check_out=today + timedelta(days=8),
            rooms_count=2,
            guests_count=2,
            price_per_night_snapshot=1_500_000,
            subtotal=9_000_000,
            total_price=9_000_000,
            status=Booking.Status.CONFIRMED,
        )

        url = reverse("hotels:hotels_list")
        res = self.client.get(url, {"city": "Isfahan", "check_in": d_in, "check_out": d_out})
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data")
        self.assertEqual(len(data), 1)
        hotel_data = data[0]
        self.assertEqual(hotel_data["id"], self.hotel.id)
        # min_price comes from with_min_price()
        self.assertEqual(hotel_data["min_price"], 1_500_000)
        self.assertTrue(hotel_data["available"])

    def test_hotel_rooms_view_uses_roomtype_with_availability(self):
        """hotel_rooms_view directly returns room availability annotated by RoomTypeQuerySet."""
        today = timezone.localdate()
        d_in = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        d_out = (today + timedelta(days=5)).strftime("%Y-%m-%d")

        # Book 1 Deluxe room
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt_deluxe,
            check_in=today + timedelta(days=2),
            check_out=today + timedelta(days=5),
            rooms_count=1,
            guests_count=2,
            price_per_night_snapshot=2_500_000,
            subtotal=7_500_000,
            total_price=7_500_000,
            status=Booking.Status.CONFIRMED,
        )

        url = reverse("hotels:hotel_rooms", kwargs={"hotel_id": self.hotel.id})
        res = self.client.get(url, {"check_in": d_in, "check_out": d_out, "guests": 2})
        self.assertEqual(res.status_code, 200)
        rooms = res.json().get("data")
        deluxe = next(r for r in rooms if r["id"] == self.rt_deluxe.id)
        standard = next(r for r in rooms if r["id"] == self.rt_standard.id)

        # Deluxe: quantity 3 - 1 reserved = 2 available
        self.assertEqual(deluxe["available_count"], 2)
        self.assertTrue(deluxe["available"])

        # Standard: quantity 2 - 0 reserved = 2 available
        self.assertEqual(standard["available_count"], 2)
        self.assertTrue(standard["available"])



class HotelLoggingCoverageTests(TestCase):
    """Tests verifying logging coverage in hotels views (P3-09)."""

    def setUp(self):
        self.manager = User.objects.create_user(
            username="hotel_log_mgr",
            email="hotel_log_mgr@example.com",
            password="StrongPassword123!",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.other_manager = User.objects.create_user(
            username="other_mgr",
            email="other_mgr@example.com",
            password="StrongPassword123!",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.hotel = Hotel.objects.create(
            name="Log Test Hotel",
            city="Shiraz",
            address="Zand St",
            owner=self.manager,
        )

    def test_manager_hotel_crud_logging(self):
        self.client.force_login(self.manager)

        # 1. Create hotel
        payload = {
            "name": "Audit Grand Hotel",
            "city": "Tehran",
            "address": "Valiasr St",
            "description": "Luxury audit hotel",
            "star_rating": 5,
        }
        with self.assertLogs("apps.hotels.views", level="INFO") as cm:
            res = self.client.post(
                reverse("hotels:manager_hotels_list_create"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 201)
            hotel_id = res.json()["data"]["id"]
            self.assertTrue(any("Manager created hotel" in m and "Audit Grand Hotel" in m for m in cm.output))

        # 2. Update hotel
        update_payload = {
            "name": "Audit Grand Hotel Renovated",
            "city": "Tehran",
            "address": "Valiasr St",
            "description": "Luxury audit hotel updated",
            "star_rating": 5,
        }
        with self.assertLogs("apps.hotels.views", level="INFO") as cm:
            res = self.client.put(
                reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": hotel_id}),
                data=json.dumps(update_payload),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 200)
            self.assertTrue(any("Manager updated hotel" in m and "Audit Grand Hotel Renovated" in m for m in cm.output))

        # 3. Delete hotel
        with self.assertLogs("apps.hotels.views", level="INFO") as cm:
            res = self.client.delete(reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": hotel_id}))
            self.assertEqual(res.status_code, 200)
            self.assertTrue(any("Manager deleted hotel" in m and str(hotel_id) in m for m in cm.output))

    def test_manager_hotel_unauthorized_access_logging(self):
        self.client.force_login(self.other_manager)
        with self.assertLogs("apps.security", level="WARNING") as cm:
            res = self.client.get(reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": self.hotel.id}))
            self.assertEqual(res.status_code, 404)
            self.assertTrue(any("Manager hotel access denied or not found" in m and str(self.hotel.id) in m for m in cm.output))

    def test_manager_room_type_crud_logging(self):
        self.client.force_login(self.manager)
        payload = {
            "title": "Audit Suite",
            "capacity": 2,
            "price_per_night": 2000000,
            "quantity": 5,
        }
        with self.assertLogs("apps.hotels.views", level="INFO") as cm:
            res = self.client.post(
                reverse("hotels:manager_room_types_list_create", kwargs={"hotel_id": self.hotel.id}),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 201)
            rt_id = res.json()["data"]["id"]
            self.assertTrue(any("Manager created room type" in m and "Audit Suite" in m for m in cm.output))

        with self.assertLogs("apps.hotels.views", level="INFO") as cm:
            res = self.client.delete(reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": rt_id}))
            self.assertEqual(res.status_code, 200)
            self.assertTrue(any("Manager deleted room type" in m and str(rt_id) in m for m in cm.output))

    def test_public_views_logging(self):
        # 1. Validation failure on invalid search
        with self.assertLogs("apps.hotels.views", level="INFO") as cm:
            res = self.client.get(reverse("hotels:hotels_list"), {"check_in": "2020-01-01", "check_out": "2020-01-05"})
            self.assertEqual(res.status_code, 400)
            self.assertTrue(any("Hotel search validation failed" in m for m in cm.output))

        # 2. Not found hotel
        with self.assertLogs("apps.hotels.views", level="INFO") as cm:
            res = self.client.get(reverse("hotels:hotel_detail", kwargs={"hotel_id": 999999}))
            self.assertEqual(res.status_code, 404)
            self.assertTrue(any("Hotel not found: hotel_id=999999" in m for m in cm.output))


class HotelQueryAndTemplateOptimizationTests(TestCase):
    """
    Performance and template caching tests (P4-06).
    Verifies O(1) queries on hotel search and template deduplication/caching.
    """

    def setUp(self):
        super().setUp()
        self.manager = User.objects.create_user(
            username="hotel_perf_mgr",
            email="hotel_perf@example.com",
            password="password123",
            role="manager",
            email_verified=True,
        )

    def test_hotels_list_query_count_is_constant(self):
        """
        Verify hotels_list_view executes O(1) queries regardless of number of hotels.
        Before optimization: redundant prefetch of amenities added 1 extra query.
        After optimization: exactly 2 queries total (1 hotels with min_price + 1 room types).
        """
        # Create 1 hotel with room types
        h1 = Hotel.objects.create(
            name="Perf City Hotel 1",
            city="Qom",
            address="Street 1",
            owner=self.manager,
        )
        RoomType.objects.create(
            hotel=h1,
            title="Standard Room",
            capacity=2,
            price_per_night=800000,
            quantity=5,
        )

        url = reverse("hotels:hotels_list") + "?city=Qom"

        with self.assertNumQueries(2):
            res1 = self.client.get(url)
            self.assertEqual(res1.status_code, 200)
            self.assertEqual(len(res1.json()["data"]), 1)

        # Create 4 more hotels with room types in the same city (total 5 hotels)
        for i in range(2, 6):
            hi = Hotel.objects.create(
                name=f"Perf City Hotel {i}",
                city="Qom",
                address=f"Street {i}",
                owner=self.manager,
            )
            RoomType.objects.create(
                hotel=hi,
                title=f"Room Type {i}",
                capacity=2,
                price_per_night=800000 + i * 50000,
                quantity=5,
            )

        # Query count MUST STILL be exactly 2 queries for 5 hotels
        with self.assertNumQueries(2):
            res5 = self.client.get(url)
            self.assertEqual(res5.status_code, 200)
            self.assertEqual(len(res5.json()["data"]), 5)

    def test_email_template_inheritance_and_deduplication(self):
        """
        Verify that child email templates inherit from base.html and base.txt,
        demonstrating template deduplication (P4-06).
        """
        from django.template.loader import render_to_string

        context = {
            "recipient_name": "سارا احمدی",
            "message_body": "رزرو شما تایید شد.",
            "action_url": "https://example.com/reservation/100",
            "action_text": "مشاهده جزییات",
        }

        # HTML template extends emails/base.html
        html = render_to_string("emails/sample_notification.html", context)
        self.assertIn("سارا احمدی", html)
        self.assertIn("سامانه رزرواسیون هتل", html)
        self.assertIn("dir=\"rtl\"", html)
        self.assertIn("مشاهده جزییات", html)

        # TXT template extends emails/base.txt
        txt = render_to_string("emails/sample_notification.txt", context)
        self.assertIn("سارا احمدی", txt)
        self.assertIn("سامانه رزرواسیون هتل", txt)
        self.assertIn("https://example.com/reservation/100", txt)

    def test_cached_template_loader_configured_in_production(self):
        """
        Verify that when DEBUG=False, Django uses django.template.loaders.cached.Loader.
        """
        from django.conf import settings
        from django.template.loader import get_template

        # Test with settings check
        templates_setting = settings.TEMPLATES[0]
        # Check that when DEBUG is False in config/settings.py, cached loader is specified
        import config.settings as app_settings
        # Simulate non-debug configuration logic
        if not app_settings.DEBUG:
            self.assertFalse(templates_setting.get("APP_DIRS"))
            self.assertTrue(any(
                loader[0] == "django.template.loaders.cached.Loader"
                for loader in templates_setting.get("OPTIONS", {}).get("loaders", [])
            ))

        # Ensure index.html and base.html can be loaded without error
        tmpl_index = get_template("index.html")
        self.assertIsNotNone(tmpl_index)
        tmpl_email = get_template("emails/base.html")
        self.assertIsNotNone(tmpl_email)
