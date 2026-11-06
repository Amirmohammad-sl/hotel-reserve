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
