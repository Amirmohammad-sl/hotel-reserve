from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from .admin import AmenityAdmin, HotelAdmin, RoomTypeAdmin
from .models import Amenity, Hotel, RoomType

User = get_user_model()


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
    def test_admin_registration(self):
        self.assertIn(Amenity, site._registry)
        self.assertIn(Hotel, site._registry)
        self.assertIn(RoomType, site._registry)
        self.assertIsInstance(site._registry[Amenity], AmenityAdmin)
        self.assertIsInstance(site._registry[Hotel], HotelAdmin)
        self.assertIsInstance(site._registry[RoomType], RoomTypeAdmin)
