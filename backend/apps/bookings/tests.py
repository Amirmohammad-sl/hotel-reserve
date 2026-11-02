import datetime
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from apps.bookings.admin import BookingAdmin, BookingAdminForm, DiscountCodeAdmin
from apps.bookings.models import Booking, DiscountCode
from apps.hotels.models import Hotel, RoomType

User = get_user_model()


class BookingModelTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="testmanager",
            email="manager@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest = User.objects.create_user(
            username="testguest",
            email="guest@example.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="Espinas Palace",
            city="Tehran",
            address="Saadat Abad",
        )
        self.hotel2 = Hotel.objects.create(
            owner=self.manager,
            name="Parsian Azadi",
            city="Tehran",
            address="Chamran Expwy",
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            title="Junior Suite",
            capacity=2,
            price_per_night=3_000_000,
            quantity=5,
        )

    def test_discount_code_creation_and_uppercase(self):
        discount = DiscountCode.objects.create(
            hotel=self.hotel,
            code="norooz1403",
            percent=20,
            valid_from=datetime.date(2026, 3, 20),
            valid_to=datetime.date(2026, 4, 5),
            max_uses=50,
        )
        self.assertEqual(discount.code, "NOROOZ1403")
        self.assertEqual(discount.percent, 20)
        self.assertIn("NOROOZ1403", str(discount))
        self.assertIn("Espinas Palace", str(discount))

    def test_discount_code_unique_per_hotel(self):
        DiscountCode.objects.create(
            hotel=self.hotel,
            code="VIP10",
            percent=10,
            valid_from=datetime.date(2026, 1, 1),
            valid_to=datetime.date(2026, 12, 31),
        )
        # Same code for same hotel should fail DB unique constraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DiscountCode.objects.create(
                    hotel=self.hotel,
                    code="VIP10",
                    percent=15,
                    valid_from=datetime.date(2026, 1, 1),
                    valid_to=datetime.date(2026, 12, 31),
                )

        # Same code for different hotel should succeed
        diff_hotel_discount = DiscountCode.objects.create(
            hotel=self.hotel2,
            code="VIP10",
            percent=15,
            valid_from=datetime.date(2026, 1, 1),
            valid_to=datetime.date(2026, 12, 31),
        )
        self.assertEqual(diff_hotel_discount.code, "VIP10")

    def test_discount_code_percent_check_constraint(self):
        # percent = 0 should violate CheckConstraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DiscountCode.objects.create(
                    hotel=self.hotel,
                    code="ZERO",
                    percent=0,
                    valid_from=datetime.date(2026, 1, 1),
                    valid_to=datetime.date(2026, 12, 31),
                )
        # percent = 101 should violate CheckConstraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DiscountCode.objects.create(
                    hotel=self.hotel,
                    code="OVER100",
                    percent=101,
                    valid_from=datetime.date(2026, 1, 1),
                    valid_to=datetime.date(2026, 12, 31),
                )

    def test_calculate_nights_pure_function(self):
        booking = Booking(
            check_in=datetime.date(2026, 6, 10),
            check_out=datetime.date(2026, 6, 15),
        )
        self.assertEqual(booking.calculate_nights(), 5)

        # Invalid/zero nights
        invalid_booking = Booking(
            check_in=datetime.date(2026, 6, 15),
            check_out=datetime.date(2026, 6, 10),
        )
        self.assertEqual(invalid_booking.calculate_nights(), 0)

    def test_booking_creation_and_auto_nights(self):
        booking = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 7, 1),
            check_out=datetime.date(2026, 7, 4),
            rooms_count=1,
            guests_count=2,
            price_per_night_snapshot=3_000_000,
            subtotal=9_000_000,
            discount_amount=0,
            total_price=9_000_000,
        )
        self.assertEqual(booking.nights, 3)
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)
        self.assertIn("Junior Suite", str(booking))
        self.assertIn("testguest", str(booking))

    def test_booking_check_out_gt_check_in_constraint(self):
        # check_out == check_in violates check constraint check_out > check_in
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    guest=self.guest,
                    room_type=self.room_type,
                    check_in=datetime.date(2026, 7, 1),
                    check_out=datetime.date(2026, 7, 1),
                    rooms_count=1,
                    guests_count=1,
                    nights=1,
                    price_per_night_snapshot=3_000_000,
                    subtotal=3_000_000,
                    discount_amount=0,
                    total_price=3_000_000,
                )

        # check_out < check_in violates check constraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    guest=self.guest,
                    room_type=self.room_type,
                    check_in=datetime.date(2026, 7, 5),
                    check_out=datetime.date(2026, 7, 1),
                    rooms_count=1,
                    guests_count=1,
                    nights=1,
                    price_per_night_snapshot=3_000_000,
                    subtotal=3_000_000,
                    discount_amount=0,
                    total_price=3_000_000,
                )

    def test_booking_validation_clean_raises_for_invalid_dates(self):
        booking = Booking(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 7, 5),
            check_out=datetime.date(2026, 7, 2),
            rooms_count=1,
            guests_count=1,
            price_per_night_snapshot=3_000_000,
            subtotal=3_000_000,
            total_price=3_000_000,
        )
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_booking_positive_constraints(self):
        # rooms_count < 1 violates constraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    guest=self.guest,
                    room_type=self.room_type,
                    check_in=datetime.date(2026, 7, 1),
                    check_out=datetime.date(2026, 7, 3),
                    rooms_count=0,
                    guests_count=1,
                    nights=2,
                    price_per_night_snapshot=3_000_000,
                    subtotal=6_000_000,
                    total_price=6_000_000,
                )

        # guests_count < 1 violates constraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    guest=self.guest,
                    room_type=self.room_type,
                    check_in=datetime.date(2026, 7, 1),
                    check_out=datetime.date(2026, 7, 3),
                    rooms_count=1,
                    guests_count=0,
                    nights=2,
                    price_per_night_snapshot=3_000_000,
                    subtotal=6_000_000,
                    total_price=6_000_000,
                )

    def test_booking_protects_guest_and_room_type(self):
        booking = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 7, 1),
            check_out=datetime.date(2026, 7, 3),
            rooms_count=1,
            guests_count=2,
            nights=2,
            price_per_night_snapshot=3_000_000,
            subtotal=6_000_000,
            total_price=6_000_000,
        )
        # Attempting to delete guest must fail due to on_delete=PROTECT
        with self.assertRaises(ProtectedError):
            self.guest.delete()

        # Attempting to delete room_type must fail due to on_delete=PROTECT
        with self.assertRaises(ProtectedError):
            self.room_type.delete()

    def test_booking_set_null_on_discount_code_deletion(self):
        discount = DiscountCode.objects.create(
            hotel=self.hotel,
            code="SPECIAL15",
            percent=15,
            valid_from=datetime.date(2026, 6, 1),
            valid_to=datetime.date(2026, 8, 1),
        )
        booking = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 7, 1),
            check_out=datetime.date(2026, 7, 3),
            rooms_count=1,
            guests_count=2,
            nights=2,
            price_per_night_snapshot=3_000_000,
            subtotal=6_000_000,
            discount_code=discount,
            discount_amount=900_000,
            total_price=5_100_000,
        )
        self.assertEqual(booking.discount_code, discount)

        # Deleting discount code sets booking.discount_code to NULL (SET_NULL)
        discount.delete()
        booking.refresh_from_db()
        self.assertIsNone(booking.discount_code)


class BookingAdminTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_booking",
            email="admin_booking@example.com",
            password="adminpassword123",
        )
        self.manager = User.objects.create_user(
            username="mgr_booking",
            email="mgr_booking@example.com",
            password="password123",
            role=User.Role.MANAGER,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="Test Hotel Admin",
            city="Shiraz",
            address="Some street",
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            title="Single Room",
            capacity=1,
            price_per_night=1_000_000,
            quantity=3,
        )
        self.client.login(username="admin_booking", password="adminpassword123")

    def test_admin_registration_and_configuration(self):
        self.assertIn(DiscountCode, site._registry)
        self.assertIn(Booking, site._registry)

        discount_admin = site._registry[DiscountCode]
        self.assertIsInstance(discount_admin, DiscountCodeAdmin)
        self.assertIn("code", discount_admin.list_display)
        self.assertIn("is_active", discount_admin.list_filter)
        self.assertIn("code", discount_admin.search_fields)
        self.assertIn("hotel", discount_admin.autocomplete_fields)

        booking_admin = site._registry[Booking]
        self.assertIsInstance(booking_admin, BookingAdmin)
        self.assertIn("status", booking_admin.list_display)
        self.assertIn("status", booking_admin.list_filter)
        self.assertIn("id", booking_admin.search_fields)
        self.assertIn("guest", booking_admin.autocomplete_fields)
        self.assertIn("room_type", booking_admin.autocomplete_fields)
        self.assertEqual(booking_admin.date_hierarchy, "check_in")

    def test_booking_admin_form_auto_nights(self):
        form_data = {
            "guest": self.superuser.pk,
            "room_type": self.room_type.pk,
            "check_in": "2026-09-01",
            "check_out": "2026-09-05",
            "rooms_count": 1,
            "guests_count": 1,
            "nights": "",  # omitted to test auto calculation
            "price_per_night_snapshot": 1_000_000,
            "subtotal": 4_000_000,
            "discount_amount": 0,
            "total_price": 4_000_000,
            "status": Booking.Status.CONFIRMED,
        }
        form = BookingAdminForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        booking = form.save()
        self.assertEqual(booking.nights, 4)

    def test_admin_changelist_views_render_successfully(self):
        for model_name in ["discountcode", "booking"]:
            url = reverse(f"admin:bookings_{model_name}_changelist")
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                200,
                f"Changelist for bookings.{model_name} returned status {response.status_code}",
            )
