import datetime
import json
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from apps.bookings.admin import BookingAdmin, BookingAdminForm, DiscountCodeAdmin
from apps.bookings.forms import (
    DiscountCodeForm,
    ManagerAvailabilityFilterForm,
    ManagerBookingFilterForm,
    booking_to_dict,
    discount_code_to_dict,
)
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


class DiscountCodeFormAndSerializerTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="form_mgr",
            email="form_mgr@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="Test Form Hotel",
            city="Isfahan",
            address="Chaharbagh",
        )
        self.hotel2 = Hotel.objects.create(
            owner=self.manager,
            name="Test Form Hotel 2",
            city="Yazd",
            address="Kashani",
        )

    def test_discount_code_form_valid(self):
        data = {
            "code": "autumn2026",
            "percent": 25,
            "valid_from": "2026-10-01",
            "valid_to": "2026-10-31",
            "max_uses": 100,
        }
        form = DiscountCodeForm(data=data, hotel=self.hotel)
        self.assertTrue(form.is_valid(), form.errors)
        discount = form.save()
        self.assertEqual(discount.code, "AUTUMN2026")
        self.assertEqual(discount.percent, 25)
        self.assertEqual(discount.hotel, self.hotel)
        self.assertTrue(discount.is_active)

    def test_discount_code_form_invalid_percent(self):
        # percent > 100
        form = DiscountCodeForm(
            data={"code": "HIGH", "percent": 150, "valid_from": "2026-10-01", "valid_to": "2026-10-31"},
            hotel=self.hotel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("percent", form.errors)

        # percent < 1
        form = DiscountCodeForm(
            data={"code": "ZERO", "percent": 0, "valid_from": "2026-10-01", "valid_to": "2026-10-31"},
            hotel=self.hotel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("percent", form.errors)

    def test_discount_code_form_invalid_dates(self):
        form = DiscountCodeForm(
            data={"code": "INV_DATE", "percent": 20, "valid_from": "2026-10-31", "valid_to": "2026-10-01"},
            hotel=self.hotel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("valid_to", form.errors)

    def test_discount_code_form_duplicate_per_hotel(self):
        DiscountCode.objects.create(
            hotel=self.hotel,
            code="EXISTING",
            percent=10,
            valid_from=datetime.date(2026, 1, 1),
            valid_to=datetime.date(2026, 12, 31),
        )
        form = DiscountCodeForm(
            data={"code": "existing", "percent": 15, "valid_from": "2026-02-01", "valid_to": "2026-03-01"},
            hotel=self.hotel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)

        # Same code for different hotel must succeed
        form2 = DiscountCodeForm(
            data={"code": "existing", "percent": 15, "valid_from": "2026-02-01", "valid_to": "2026-03-01"},
            hotel=self.hotel2,
        )
        self.assertTrue(form2.is_valid(), form2.errors)

    def test_discount_code_form_preserves_is_active_on_update(self):
        discount = DiscountCode.objects.create(
            hotel=self.hotel,
            code="DEACTIVATE",
            percent=10,
            valid_from=datetime.date(2026, 1, 1),
            valid_to=datetime.date(2026, 12, 31),
            is_active=False,
        )
        # Update without is_active in payload
        form = DiscountCodeForm(
            data={"code": "DEACTIVATE", "percent": 12, "valid_from": "2026-01-01", "valid_to": "2026-12-31"},
            instance=discount,
            hotel=self.hotel,
        )
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertFalse(updated.is_active)

    def test_discount_code_to_dict_serializer(self):
        discount = DiscountCode.objects.create(
            hotel=self.hotel,
            code="DICT10",
            percent=10,
            valid_from=datetime.date(2026, 1, 1),
            valid_to=datetime.date(2026, 12, 31),
            max_uses=50,
        )
        d = discount_code_to_dict(discount)
        self.assertEqual(d["id"], discount.id)
        self.assertEqual(d["hotel_id"], self.hotel.id)
        self.assertEqual(d["code"], "DICT10")
        self.assertEqual(d["percent"], 10)
        self.assertEqual(d["valid_from"], "2026-01-01")
        self.assertEqual(d["valid_to"], "2026-12-31")
        self.assertEqual(d["max_uses"], 50)
        self.assertEqual(d["used_count"], 0)
        self.assertTrue(d["is_active"])

    def test_booking_to_dict_serializer(self):
        guest = User.objects.create_user(
            username="dictguest",
            email="dictguest@example.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        rt = RoomType.objects.create(
            hotel=self.hotel,
            title="Dict Suite",
            capacity=2,
            price_per_night=2_000_000,
            quantity=3,
        )
        booking = Booking.objects.create(
            guest=guest,
            room_type=rt,
            check_in=datetime.date(2026, 8, 10),
            check_out=datetime.date(2026, 8, 12),
            rooms_count=1,
            guests_count=2,
            price_per_night_snapshot=2_000_000,
            subtotal=4_000_000,
            total_price=4_000_000,
        )
        d = booking_to_dict(booking)
        self.assertEqual(d["id"], booking.id)
        self.assertEqual(d["guest"]["id"], guest.id)
        self.assertEqual(d["guest"]["username"], "dictguest")
        self.assertEqual(d["room_type"]["id"], rt.id)
        self.assertEqual(d["check_in"], "2026-08-10")
        self.assertEqual(d["check_out"], "2026-08-12")
        self.assertEqual(d["nights"], 2)
        self.assertEqual(d["status"], "confirmed")


class ManagerDiscountViewsTests(TestCase):
    def setUp(self):
        self.manager1 = User.objects.create_user(
            username="mgr_one",
            email="mgr1@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.manager2 = User.objects.create_user(
            username="mgr_two",
            email="mgr2@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest = User.objects.create_user(
            username="guest_user",
            email="guest@example.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel1 = Hotel.objects.create(
            owner=self.manager1,
            name="Hotel One",
            city="Tehran",
            address="Valiasr",
        )
        self.hotel2 = Hotel.objects.create(
            owner=self.manager2,
            name="Hotel Two",
            city="Mashhad",
            address="Imam Reza",
        )
        self.discount1 = DiscountCode.objects.create(
            hotel=self.hotel1,
            code="SUMMER10",
            percent=10,
            valid_from=datetime.date(2026, 6, 1),
            valid_to=datetime.date(2026, 8, 31),
        )

    def test_unauthenticated_and_guest_role_forbidden(self):
        url = reverse("bookings:manager_hotel_discounts", kwargs={"hotel_id": self.hotel1.id})
        # Unauthenticated -> 401
        res = self.client.get(url)
        self.assertEqual(res.status_code, 401)

        # Guest role -> 403
        self.client.login(username="guest_user", password="passWORD123!")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

    def test_manager_list_and_create_discounts(self):
        self.client.login(username="mgr_one", password="passWORD123!")
        url = reverse("bookings:manager_hotel_discounts", kwargs={"hotel_id": self.hotel1.id})

        # GET discounts list
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["code"], "SUMMER10")

        # POST create new discount
        payload = {
            "code": "WINTER20",
            "percent": 20,
            "valid_from": "2026-12-01",
            "valid_to": "2026-12-31",
            "max_uses": 50,
        }
        res = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 201)
        created = res.json()["data"]
        self.assertEqual(created["code"], "WINTER20")
        self.assertEqual(created["percent"], 20)
        self.assertTrue(DiscountCode.objects.filter(hotel=self.hotel1, code="WINTER20").exists())

    def test_manager_create_discount_validation_error(self):
        self.client.login(username="mgr_one", password="passWORD123!")
        url = reverse("bookings:manager_hotel_discounts", kwargs={"hotel_id": self.hotel1.id})
        # Duplicate code SUMMER10
        payload = {
            "code": "SUMMER10",
            "percent": 15,
            "valid_from": "2026-07-01",
            "valid_to": "2026-07-31",
        }
        res = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 400)
        errors = res.json().get("errors", {})
        self.assertIn("code", errors)

    def test_manager_cannot_access_or_modify_other_managers_discounts_returns_404(self):
        # Manager 1 tries to list/create discounts for Manager 2's hotel -> 404
        self.client.login(username="mgr_one", password="passWORD123!")
        url_foreign_hotel = reverse("bookings:manager_hotel_discounts", kwargs={"hotel_id": self.hotel2.id})
        res = self.client.get(url_foreign_hotel)
        self.assertEqual(res.status_code, 404)

        res = self.client.post(
            url_foreign_hotel,
            data=json.dumps({"code": "HACK", "percent": 50, "valid_from": "2026-01-01", "valid_to": "2026-12-31"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 404)

        # Manager 2 tries to GET, PUT, DELETE Manager 1's discount -> 404
        self.client.login(username="mgr_two", password="passWORD123!")
        url_foreign_discount = reverse("bookings:manager_discount_detail", kwargs={"discount_id": self.discount1.id})

        self.assertEqual(self.client.get(url_foreign_discount).status_code, 404)
        self.assertEqual(
            self.client.put(
                url_foreign_discount,
                data=json.dumps({"code": "SUMMER10", "percent": 25, "valid_from": "2026-06-01", "valid_to": "2026-08-31"}),
                content_type="application/json",
            ).status_code,
            404,
        )
        self.assertEqual(self.client.delete(url_foreign_discount).status_code, 404)

    def test_manager_discount_detail_update_delete(self):
        self.client.login(username="mgr_one", password="passWORD123!")
        url = reverse("bookings:manager_discount_detail", kwargs={"discount_id": self.discount1.id})

        # GET detail
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["code"], "SUMMER10")

        # PUT update
        update_payload = {
            "code": "SUMMER15",
            "percent": 15,
            "valid_from": "2026-06-01",
            "valid_to": "2026-08-31",
            "max_uses": 200,
        }
        res = self.client.put(url, data=json.dumps(update_payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["code"], "SUMMER15")
        self.assertEqual(res.json()["data"]["percent"], 15)

        # DELETE
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(DiscountCode.objects.filter(id=self.discount1.id).exists())


class ManagerBookingsViewTests(TestCase):
    def setUp(self):
        self.manager1 = User.objects.create_user(
            username="mgr_b1",
            email="mgr_b1@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.manager2 = User.objects.create_user(
            username="mgr_b2",
            email="mgr_b2@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest = User.objects.create_user(
            username="guest_b",
            email="guest_b@example.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel1 = Hotel.objects.create(
            owner=self.manager1,
            name="Hotel Bookings 1",
            city="Shiraz",
            address="Zand",
        )
        self.hotel2 = Hotel.objects.create(
            owner=self.manager2,
            name="Hotel Bookings 2",
            city="Tabriz",
            address="Saat Sq",
        )
        self.rt1 = RoomType.objects.create(
            hotel=self.hotel1,
            title="Deluxe",
            capacity=2,
            price_per_night=2_000_000,
            quantity=5,
        )
        self.rt2 = RoomType.objects.create(
            hotel=self.hotel2,
            title="Standard",
            capacity=2,
            price_per_night=1_500_000,
            quantity=3,
        )
        self.b1 = Booking.objects.create(
            guest=self.guest,
            room_type=self.rt1,
            check_in=datetime.date(2026, 9, 1),
            check_out=datetime.date(2026, 9, 5),
            rooms_count=1,
            guests_count=2,
            price_per_night_snapshot=2_000_000,
            subtotal=8_000_000,
            total_price=8_000_000,
            status=Booking.Status.CONFIRMED,
        )
        self.b2 = Booking.objects.create(
            guest=self.guest,
            room_type=self.rt1,
            check_in=datetime.date(2026, 9, 10),
            check_out=datetime.date(2026, 9, 15),
            rooms_count=2,
            guests_count=4,
            price_per_night_snapshot=2_000_000,
            subtotal=20_000_000,
            total_price=20_000_000,
            status=Booking.Status.CANCELLED,
        )

    def test_manager_list_bookings_own_hotel_and_filters(self):
        self.client.login(username="mgr_b1", password="passWORD123!")
        url = reverse("bookings:manager_hotel_bookings", kwargs={"hotel_id": self.hotel1.id})

        # List all
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["data"]), 2)

        # Filter by status=confirmed
        res = self.client.get(f"{url}?status=confirmed")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.b1.id)

        # Filter by status=cancelled
        res = self.client.get(f"{url}?status=cancelled")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.b2.id)

        # Filter by date range matching only b1
        res = self.client.get(f"{url}?date_from=2026-09-01&date_to=2026-09-04")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.b1.id)

    def test_manager_cannot_view_other_managers_bookings_returns_404(self):
        self.client.login(username="mgr_b1", password="passWORD123!")
        url = reverse("bookings:manager_hotel_bookings", kwargs={"hotel_id": self.hotel2.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)


class ManagerAvailabilityViewTests(TestCase):
    def setUp(self):
        self.manager1 = User.objects.create_user(
            username="mgr_avail1",
            email="mgr_avail1@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.manager2 = User.objects.create_user(
            username="mgr_avail2",
            email="mgr_avail2@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest = User.objects.create_user(
            username="guest_avail",
            email="guest_avail@example.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel1 = Hotel.objects.create(
            owner=self.manager1,
            name="Availability Hotel",
            city="Kish",
            address="Coast Rd",
        )
        self.hotel2 = Hotel.objects.create(
            owner=self.manager2,
            name="Other Hotel",
            city="Qom",
            address="Central",
        )
        # 10 rooms of Deluxe Suite
        self.rt = RoomType.objects.create(
            hotel=self.hotel1,
            title="Deluxe Suite",
            capacity=2,
            price_per_night=5_000_000,
            quantity=10,
        )

    def test_availability_requires_valid_date_range(self):
        self.client.login(username="mgr_avail1", password="passWORD123!")
        url = reverse("bookings:manager_hotel_availability", kwargs={"hotel_id": self.hotel1.id})

        # Missing params -> 400
        res = self.client.get(url)
        self.assertEqual(res.status_code, 400)

        # date_to <= date_from -> 400
        res = self.client.get(f"{url}?date_from=2026-10-05&date_to=2026-10-01")
        self.assertEqual(res.status_code, 400)

        # Range > 90 days -> 400
        res = self.client.get(f"{url}?date_from=2026-01-01&date_to=2026-05-01")
        self.assertEqual(res.status_code, 400)

    def test_availability_foreign_hotel_returns_404(self):
        self.client.login(username="mgr_avail1", password="passWORD123!")
        url = reverse("bookings:manager_hotel_availability", kwargs={"hotel_id": self.hotel2.id})
        res = self.client.get(f"{url}?date_from=2026-10-01&date_to=2026-10-06")
        self.assertEqual(res.status_code, 404)

    def test_availability_hand_computed_3_overlapping_bookings_dod(self):
        """
        DoD: Availability numbers match hand-computed example with 3 overlapping bookings.

        Setup:
        - RoomType quantity: 10
        - Target date range: 2026-10-01 to 2026-10-06 (5 nights)

        Bookings:
        - Booking 1: 2026-10-01 to 2026-10-04 (nights 1, 2, 3), rooms_count=3, confirmed
        - Booking 2: 2026-10-02 to 2026-10-05 (nights 2, 3, 4), rooms_count=4, confirmed
        - Booking 3: 2026-10-03 to 2026-10-06 (nights 3, 4, 5), rooms_count=2, confirmed
        - Booking 4 (cancelled): 2026-10-02 to 2026-10-04, rooms_count=5, cancelled (must be ignored!)

        Hand calculation per night:
        - 2026-10-01: B1(3)                      => reserved = 3, free = 10 - 3 = 7
        - 2026-10-02: B1(3) + B2(4)              => reserved = 7, free = 10 - 7 = 3
        - 2026-10-03: B1(3) + B2(4) + B3(2)      => reserved = 9, free = 10 - 9 = 1 (all 3 overlap!)
        - 2026-10-04: B2(4) + B3(2)              => reserved = 6, free = 10 - 6 = 4 (B1 checked out)
        - 2026-10-05: B3(2)                      => reserved = 2, free = 10 - 2 = 8 (B2 checked out)
        """
        # Booking 1
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt,
            check_in=datetime.date(2026, 10, 1),
            check_out=datetime.date(2026, 10, 4),
            rooms_count=3,
            guests_count=3,
            price_per_night_snapshot=5_000_000,
            subtotal=45_000_000,
            total_price=45_000_000,
            status=Booking.Status.CONFIRMED,
        )
        # Booking 2
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt,
            check_in=datetime.date(2026, 10, 2),
            check_out=datetime.date(2026, 10, 5),
            rooms_count=4,
            guests_count=4,
            price_per_night_snapshot=5_000_000,
            subtotal=60_000_000,
            total_price=60_000_000,
            status=Booking.Status.CONFIRMED,
        )
        # Booking 3
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt,
            check_in=datetime.date(2026, 10, 3),
            check_out=datetime.date(2026, 10, 6),
            rooms_count=2,
            guests_count=2,
            price_per_night_snapshot=5_000_000,
            subtotal=30_000_000,
            total_price=30_000_000,
            status=Booking.Status.CONFIRMED,
        )
        # Booking 4 (cancelled -> must not affect availability)
        Booking.objects.create(
            guest=self.guest,
            room_type=self.rt,
            check_in=datetime.date(2026, 10, 2),
            check_out=datetime.date(2026, 10, 4),
            rooms_count=5,
            guests_count=5,
            price_per_night_snapshot=5_000_000,
            subtotal=50_000_000,
            total_price=50_000_000,
            status=Booking.Status.CANCELLED,
        )

        self.client.login(username="mgr_avail1", password="passWORD123!")
        url = reverse("bookings:manager_hotel_availability", kwargs={"hotel_id": self.hotel1.id})
        res = self.client.get(f"{url}?date_from=2026-10-01&date_to=2026-10-06")
        self.assertEqual(res.status_code, 200)

        data = res.json()["data"]
        self.assertEqual(len(data), 1)

        rt_data = data[0]
        self.assertEqual(rt_data["room_type_id"], self.rt.id)
        self.assertEqual(rt_data["room_type_title"], "Deluxe Suite")
        self.assertEqual(rt_data["total_quantity"], 10)

        daily = rt_data["daily_availability"]
        self.assertEqual(len(daily), 5)

        # Expected hand-computed numbers:
        expected = [
            {"date": "2026-10-01", "total": 10, "reserved": 3, "free": 7},
            {"date": "2026-10-02", "total": 10, "reserved": 7, "free": 3},
            {"date": "2026-10-03", "total": 10, "reserved": 9, "free": 1},
            {"date": "2026-10-04", "total": 10, "reserved": 6, "free": 4},
            {"date": "2026-10-05", "total": 10, "reserved": 2, "free": 8},
        ]

        for idx, exp in enumerate(expected):
            with self.subTest(date=exp["date"]):
                self.assertEqual(daily[idx]["date"], exp["date"])
                self.assertEqual(daily[idx]["total"], exp["total"])
                self.assertEqual(daily[idx]["reserved"], exp["reserved"])
                self.assertEqual(daily[idx]["free"], exp["free"])
