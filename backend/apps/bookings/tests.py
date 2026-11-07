import datetime
import json
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.bookings.admin import BookingAdmin, BookingAdminForm, DiscountCodeAdmin
from apps.bookings.forms import (
    BookingQuoteForm,
    DiscountCodeForm,
    DiscountValidateForm,
    ManagerAvailabilityFilterForm,
    ManagerBookingFilterForm,
    booking_to_dict,
    discount_code_to_dict,
)
from apps.bookings.models import Booking, DiscountCode
from apps.bookings.services import (
    AvailabilityConflictError,
    BookingCancellationError,
    calculate_booking_quote,
    cancel_booking,
    create_booking,
    validate_discount_code,
)
from apps.hotels.models import Hotel, RoomType

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



# ===========================================================================
# P2-06: Forms, Services, Views and DoD Test Suites
# ===========================================================================

import json
from django.utils import timezone
from apps.bookings.forms import BookingQuoteForm, DiscountValidateForm, booking_to_dict
from apps.bookings.services import (
    AvailabilityConflictError,
    BookingCancellationError,
    calculate_booking_quote,
    cancel_booking,
    create_booking,
    validate_discount_code,
)


# ===========================================================================
# Manager Tests (P2-04)
# ===========================================================================

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


# ===========================================================================
# Guest Booking Tests (P2-06)
# ===========================================================================

class BookingFormsTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="form_mgr",
            email="form_mgr@test.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="Form Hotel",
            city="Isfahan",
            address="Abbasi St",
            is_active=True,
        )
        self.inactive_hotel = Hotel.objects.create(
            owner=self.manager,
            name="Inactive Hotel",
            city="Shiraz",
            address="Zand St",
            is_active=False,
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            title="Deluxe Double",
            capacity=2,
            price_per_night=2_000_000,
            quantity=5,
        )
        self.inactive_room_type = RoomType.objects.create(
            hotel=self.inactive_hotel,
            title="Old Room",
            capacity=2,
            price_per_night=1_000_000,
            quantity=1,
        )

    def test_valid_booking_quote_form(self):
        today = timezone.localdate()
        form_data = {
            "room_type": self.room_type.id,
            "check_in": (today + datetime.timedelta(days=2)).isoformat(),
            "check_out": (today + datetime.timedelta(days=5)).isoformat(),
            "rooms_count": 2,
            "guests_count": 4,
            "discount_code": " spring20 ",
        }
        form = BookingQuoteForm(form_data)
        self.assertTrue(form.is_valid(), f"Errors: {form.errors}")
        cleaned = form.cleaned_data
        self.assertEqual(cleaned["rooms_count"], 2)
        self.assertEqual(cleaned["guests_count"], 4)
        self.assertEqual(cleaned["discount_code"], "SPRING20")

    def test_past_check_in_rejected(self):
        today = timezone.localdate()
        form_data = {
            "room_type": self.room_type.id,
            "check_in": (today - datetime.timedelta(days=1)).isoformat(),
            "check_out": (today + datetime.timedelta(days=2)).isoformat(),
            "rooms_count": 1,
            "guests_count": 1,
        }
        form = BookingQuoteForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("check_in", form.errors)
        self.assertIn("past", form.errors["check_in"][0].lower())

    def test_check_out_must_be_strictly_after_check_in(self):
        today = timezone.localdate()
        form_data = {
            "room_type": self.room_type.id,
            "check_in": (today + datetime.timedelta(days=3)).isoformat(),
            "check_out": (today + datetime.timedelta(days=3)).isoformat(),
            "rooms_count": 1,
            "guests_count": 1,
        }
        form = BookingQuoteForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("check_out", form.errors)

    def test_capacity_exceeded_rejected(self):
        today = timezone.localdate()
        form_data = {
            "room_type": self.room_type.id,
            "check_in": (today + datetime.timedelta(days=2)).isoformat(),
            "check_out": (today + datetime.timedelta(days=4)).isoformat(),
            "rooms_count": 1,
            "guests_count": 3,
        }
        form = BookingQuoteForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("guests_count", form.errors)
        self.assertIn("capacity", form.errors["guests_count"][0].lower())

    def test_inactive_hotel_room_rejected(self):
        today = timezone.localdate()
        form_data = {
            "room_type": self.inactive_room_type.id,
            "check_in": (today + datetime.timedelta(days=1)).isoformat(),
            "check_out": (today + datetime.timedelta(days=3)).isoformat(),
        }
        form = BookingQuoteForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("room_type", form.errors)

    def test_discount_validate_form(self):
        form = DiscountValidateForm({"hotel": self.hotel.id, "code": " welcome10 "})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["code"], "WELCOME10")

        bad_form = DiscountValidateForm({"hotel": self.inactive_hotel.id, "code": "TEST"})
        self.assertFalse(bad_form.is_valid())
        self.assertIn("hotel", bad_form.errors)


class BookingServicesTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="srv_mgr",
            email="srv_mgr@test.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest = User.objects.create_user(
            username="srv_guest",
            email="srv_guest@test.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="Service Hotel",
            city="Tabriz",
            address="El Goli",
            is_active=True,
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            title="Standard Room",
            capacity=2,
            price_per_night=1_500_000,
            quantity=3,
        )
        today = timezone.localdate()
        self.discount = DiscountCode.objects.create(
            hotel=self.hotel,
            code="TABRIZ20",
            percent=20,
            valid_from=today - datetime.timedelta(days=2),
            valid_to=today + datetime.timedelta(days=10),
            max_uses=2,
            used_count=0,
            is_active=True,
        )

    def test_validate_discount_code_conditions(self):
        today = timezone.localdate()
        is_valid, obj, msg = validate_discount_code(self.hotel, "TABRIZ20", today=today)
        self.assertTrue(is_valid)
        self.assertEqual(obj, self.discount)

        self.discount.is_active = False
        self.discount.save()
        is_valid, obj, msg = validate_discount_code(self.hotel, "TABRIZ20", today=today)
        self.assertFalse(is_valid)
        self.assertIn("inactive", msg)

        self.discount.is_active = True
        self.discount.valid_to = today - datetime.timedelta(days=1)
        self.discount.save()
        is_valid, obj, msg = validate_discount_code(self.hotel, "TABRIZ20", today=today)
        self.assertFalse(is_valid)
        self.assertIn("expired", msg)

        self.discount.valid_to = today + datetime.timedelta(days=10)
        self.discount.used_count = 2
        self.discount.save()
        is_valid, obj, msg = validate_discount_code(self.hotel, "TABRIZ20", today=today)
        self.assertFalse(is_valid)
        self.assertIn("maximum", msg)

    def test_calculate_booking_quote(self):
        today = timezone.localdate()
        in_date = today + datetime.timedelta(days=3)
        out_date = today + datetime.timedelta(days=6)

        quote = calculate_booking_quote(
            room_type=self.room_type,
            check_in=in_date,
            check_out=out_date,
            rooms_count=2,
            guests_count=4,
            discount_code="TABRIZ20",
        )
        self.assertEqual(quote["nights"], 3)
        self.assertEqual(quote["subtotal"], 9_000_000)
        self.assertEqual(quote["discount_amount"], 1_800_000)
        self.assertEqual(quote["total_price"], 7_200_000)
        self.assertTrue(quote["available"])

    def test_create_and_cancel_booking(self):
        today = timezone.localdate()
        in_date = today + datetime.timedelta(days=4)
        out_date = today + datetime.timedelta(days=7)

        booking = create_booking(
            guest=self.guest,
            room_type=self.room_type,
            check_in=in_date,
            check_out=out_date,
            rooms_count=2,
            guests_count=3,
            discount_code="TABRIZ20",
        )
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)
        self.assertEqual(booking.price_per_night_snapshot, 1_500_000)
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.used_count, 1)

        cancelled = cancel_booking(booking, self.guest)
        self.assertEqual(cancelled.status, Booking.Status.CANCELLED)
        self.assertIsNotNone(cancelled.cancelled_at)
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.used_count, 0)


class BookingViewsTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="view_mgr",
            email="view_mgr@test.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest = User.objects.create_user(
            username="view_guest",
            email="view_guest@test.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.other_guest = User.objects.create_user(
            username="other_guest",
            email="other_guest@test.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="View Palace",
            city="Kish",
            address="Persian Gulf",
            is_active=True,
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            title="Sea View Suite",
            capacity=2,
            price_per_night=2_500_000,
            quantity=2,
        )
        today = timezone.localdate()
        self.discount = DiscountCode.objects.create(
            hotel=self.hotel,
            code="KISH30",
            percent=30,
            valid_from=today - datetime.timedelta(days=1),
            valid_to=today + datetime.timedelta(days=15),
            max_uses=5,
            used_count=0,
            is_active=True,
        )

    def test_guest_role_permission_enforcement(self):
        quote_url = reverse("bookings:quote")
        res = self.client.post(quote_url, {}, content_type="application/json")
        self.assertEqual(res.status_code, 401)

        self.client.force_login(self.manager)
        res = self.client.post(quote_url, {}, content_type="application/json")
        self.assertEqual(res.status_code, 403)

    def test_quote_endpoint_success(self):
        self.client.force_login(self.guest)
        today = timezone.localdate()
        payload = {
            "room_type": self.room_type.id,
            "check_in": (today + datetime.timedelta(days=5)).isoformat(),
            "check_out": (today + datetime.timedelta(days=7)).isoformat(),
            "rooms_count": 1,
            "guests_count": 2,
            "discount_code": "KISH30",
        }
        res = self.client.post(reverse("bookings:quote"), payload, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(data["nights"], 2)
        self.assertEqual(data["subtotal"], 5_000_000)
        self.assertEqual(data["discount_amount"], 1_500_000)
        self.assertEqual(data["total_price"], 3_500_000)
        self.assertTrue(data["available"])

    def test_discounts_validate_endpoint(self):
        self.client.force_login(self.guest)
        res = self.client.post(
            reverse("bookings:discount-validate"),
            {"hotel": self.hotel.id, "code": "KISH30"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["data"]["valid"])
        self.assertEqual(res.json()["data"]["percent"], 30)

        res_invalid = self.client.post(
            reverse("bookings:discount-validate"),
            {"hotel": self.hotel.id, "code": "NONEXISTENT"},
            content_type="application/json",
        )
        self.assertEqual(res_invalid.status_code, 200)
        self.assertFalse(res_invalid.json()["data"]["valid"])
        self.assertEqual(res_invalid.json()["data"]["percent"], 0)

    def test_my_bookings_list_isolation(self):
        self.client.force_login(self.guest)
        today = timezone.localdate()
        b1 = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=today + datetime.timedelta(days=1),
            check_out=today + datetime.timedelta(days=3),
            rooms_count=1,
            guests_count=1,
            nights=2,
            price_per_night_snapshot=2_500_000,
            subtotal=5_000_000,
            total_price=5_000_000,
        )
        b2 = Booking.objects.create(
            guest=self.other_guest,
            room_type=self.room_type,
            check_in=today + datetime.timedelta(days=10),
            check_out=today + datetime.timedelta(days=12),
            rooms_count=1,
            guests_count=1,
            nights=2,
            price_per_night_snapshot=2_500_000,
            subtotal=5_000_000,
            total_price=5_000_000,
        )

        res = self.client.get(reverse("bookings:bookings-mine"))
        self.assertEqual(res.status_code, 200)
        items = res.json()["data"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], b1.id)


class BookingDoDTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="dod_mgr",
            email="dod_mgr@test.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest1 = User.objects.create_user(
            username="dod_guest1",
            email="dod_guest1@test.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.guest2 = User.objects.create_user(
            username="dod_guest2",
            email="dod_guest2@test.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="DoD Grand",
            city="Shiraz",
            address="Eram Garden",
            is_active=True,
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            title="Royal Suite",
            capacity=2,
            price_per_night=4_000_000,
            quantity=2,
        )
        today = timezone.localdate()
        self.discount = DiscountCode.objects.create(
            hotel=self.hotel,
            code="DOD50",
            percent=50,
            valid_from=today - datetime.timedelta(days=1),
            valid_to=today + datetime.timedelta(days=20),
            max_uses=10,
            used_count=0,
            is_active=True,
        )

    def test_full_returns_409_and_cancel_frees_rooms_and_discount_counter(self):
        today = timezone.localdate()
        in_date = (today + datetime.timedelta(days=5)).isoformat()
        out_date = (today + datetime.timedelta(days=8)).isoformat()

        # Step 1: Guest 1 books all available 2 rooms with discount code
        self.client.force_login(self.guest1)
        payload = {
            "room_type": self.room_type.id,
            "check_in": in_date,
            "check_out": out_date,
            "rooms_count": 2,
            "guests_count": 4,
            "discount_code": "DOD50",
        }
        res1 = self.client.post(reverse("bookings:booking-create"), payload, content_type="application/json")
        self.assertEqual(res1.status_code, 201)
        booking1_id = res1.json()["data"]["id"]

        # Discount counter must have incremented to 1
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.used_count, 1)

        # Step 2: Guest 2 attempts to book 1 room for same dates -> MUST return 409 Conflict
        self.client.force_login(self.guest2)
        payload2 = {
            "room_type": self.room_type.id,
            "check_in": in_date,
            "check_out": out_date,
            "rooms_count": 1,
            "guests_count": 2,
        }
        res2 = self.client.post(reverse("bookings:booking-create"), payload2, content_type="application/json")
        self.assertEqual(res2.status_code, 409)
        self.assertIn("not available", res2.json()["message"].lower())

        # Step 3: Guest 1 cancels the reservation
        self.client.force_login(self.guest1)
        cancel_url = reverse("bookings:booking-cancel", kwargs={"booking_id": booking1_id})
        res_cancel = self.client.post(cancel_url)
        self.assertEqual(res_cancel.status_code, 200)
        self.assertEqual(res_cancel.json()["data"]["status"], "cancelled")

        # Discount counter must have decremented back to 0
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.used_count, 0)

        # Step 4: Cancelling freed the rooms -> Guest 2 attempts to book again -> MUST SUCCEED (201)
        self.client.force_login(self.guest2)
        res3 = self.client.post(reverse("bookings:booking-create"), payload2, content_type="application/json")
        self.assertEqual(res3.status_code, 201)
        self.assertEqual(res3.json()["data"]["status"], "confirmed")



# ===========================================================================
# P3-02: BookingQuerySet and DiscountCodeManager Test Suites
# ===========================================================================


class BookingQuerySetAndDiscountManagerTests(TestCase):
    """Test suite for BookingQuerySet and DiscountCodeManager domain queries (P3-02)."""

    def setUp(self):
        self.manager = User.objects.create_user(
            username="p3_mgr",
            email="p3_mgr@test.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.other_manager = User.objects.create_user(
            username="p3_other_mgr",
            email="p3_other_mgr@test.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest = User.objects.create_user(
            username="p3_guest",
            email="p3_guest@test.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.other_guest = User.objects.create_user(
            username="p3_other_guest",
            email="p3_other_guest@test.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )

        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="P3 Grand Hotel",
            city="Isfahan",
            address="Chaharbagh Abbasi",
            is_active=True,
        )
        self.other_hotel = Hotel.objects.create(
            owner=self.other_manager,
            name="P3 Other Hotel",
            city="Shiraz",
            address="Zand St",
            is_active=True,
        )

        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            title="Executive Suite",
            capacity=2,
            price_per_night=3_000_000,
            quantity=5,
        )

    def test_booking_queryset_active(self):
        """active() returns only CONFIRMED bookings and excludes CANCELLED ones."""
        b_confirmed = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 9, 1),
            check_out=datetime.date(2026, 9, 5),
            rooms_count=1,
            guests_count=1,
            nights=4,
            price_per_night_snapshot=3_000_000,
            subtotal=12_000_000,
            total_price=12_000_000,
            status=Booking.Status.CONFIRMED,
        )
        b_cancelled = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 9, 10),
            check_out=datetime.date(2026, 9, 15),
            rooms_count=1,
            guests_count=1,
            nights=5,
            price_per_night_snapshot=3_000_000,
            subtotal=15_000_000,
            total_price=15_000_000,
            status=Booking.Status.CANCELLED,
        )

        active_qs = Booking.objects.active()
        self.assertIn(b_confirmed, active_qs)
        self.assertNotIn(b_cancelled, active_qs)

    def test_booking_queryset_same_day_turnover_dod(self):
        """
        DoD: Same-day turnover (out on 5th, in on 5th) does NOT trigger an overlap.
        """
        # Existing booking 1st to 5th
        b1 = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 9, 1),
            check_out=datetime.date(2026, 9, 5),
            rooms_count=2,
            guests_count=2,
            nights=4,
            price_per_night_snapshot=3_000_000,
            subtotal=24_000_000,
            total_price=24_000_000,
            status=Booking.Status.CONFIRMED,
        )

        # Query range starting on the 5th (same day guest 1 departs)
        turnover_in = Booking.objects.overlapping(
            check_in=datetime.date(2026, 9, 5),
            check_out=datetime.date(2026, 9, 10),
        )
        self.assertNotIn(b1, turnover_in, "Same-day arrival should not overlap with departing booking.")

        # Query range ending on the 1st (same day guest 1 arrives)
        turnover_out = Booking.objects.overlapping(
            check_in=datetime.date(2026, 8, 25),
            check_out=datetime.date(2026, 9, 1),
        )
        self.assertNotIn(b1, turnover_out, "Same-day departure should not overlap with arriving booking.")

    def test_booking_queryset_overlapping_scenarios(self):
        """Verify full, partial start, and partial end overlap scenarios."""
        # Booking: Sep 10 to Sep 20
        b = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 9, 10),
            check_out=datetime.date(2026, 9, 20),
            rooms_count=1,
            guests_count=1,
            nights=10,
            price_per_night_snapshot=3_000_000,
            subtotal=30_000_000,
            total_price=30_000_000,
            status=Booking.Status.CONFIRMED,
        )

        # 1. Enclosed inside: Sep 12 to Sep 18
        self.assertTrue(
            Booking.objects.overlapping(datetime.date(2026, 9, 12), datetime.date(2026, 9, 18)).filter(id=b.id).exists()
        )
        # 2. Straddling start: Sep 5 to Sep 15
        self.assertTrue(
            Booking.objects.overlapping(datetime.date(2026, 9, 5), datetime.date(2026, 9, 15)).filter(id=b.id).exists()
        )
        # 3. Straddling end: Sep 15 to Sep 25
        self.assertTrue(
            Booking.objects.overlapping(datetime.date(2026, 9, 15), datetime.date(2026, 9, 25)).filter(id=b.id).exists()
        )
        # 4. Strictly before: Sep 1 to Sep 10
        self.assertFalse(
            Booking.objects.overlapping(datetime.date(2026, 9, 1), datetime.date(2026, 9, 10)).filter(id=b.id).exists()
        )
        # 5. Strictly after: Sep 20 to Sep 25
        self.assertFalse(
            Booking.objects.overlapping(datetime.date(2026, 9, 20), datetime.date(2026, 9, 25)).filter(id=b.id).exists()
        )

    def test_booking_queryset_for_hotel_and_guest(self):
        """for_hotel() and for_guest() filter isolation."""
        b1 = Booking.objects.create(
            guest=self.guest,
            room_type=self.room_type,
            check_in=datetime.date(2026, 10, 1),
            check_out=datetime.date(2026, 10, 3),
            rooms_count=1,
            guests_count=1,
            nights=2,
            price_per_night_snapshot=3_000_000,
            subtotal=6_000_000,
            total_price=6_000_000,
            status=Booking.Status.CONFIRMED,
        )

        other_rt = RoomType.objects.create(
            hotel=self.other_hotel,
            title="Single Room",
            price_per_night=1_000_000,
            quantity=2,
        )
        b2 = Booking.objects.create(
            guest=self.other_guest,
            room_type=other_rt,
            check_in=datetime.date(2026, 10, 1),
            check_out=datetime.date(2026, 10, 3),
            rooms_count=1,
            guests_count=1,
            nights=2,
            price_per_night_snapshot=1_000_000,
            subtotal=2_000_000,
            total_price=2_000_000,
            status=Booking.Status.CONFIRMED,
        )

        # for_hotel with model instance and id
        hotel_qs = Booking.objects.for_hotel(self.hotel)
        self.assertIn(b1, hotel_qs)
        self.assertNotIn(b2, hotel_qs)
        self.assertEqual(list(hotel_qs), list(Booking.objects.for_hotel(self.hotel.id)))

        # for_guest with model instance and id
        guest_qs = Booking.objects.for_guest(self.guest)
        self.assertIn(b1, guest_qs)
        self.assertNotIn(b2, guest_qs)
        self.assertEqual(list(guest_qs), list(Booking.objects.for_guest(self.guest.id)))

        # Chaining
        chained_qs = Booking.objects.for_hotel(self.hotel).for_guest(self.guest).active()
        self.assertIn(b1, chained_qs)

    def test_discount_code_manager_valid_now(self):
        """valid_now() filters by active status, date range and max uses."""
        today = datetime.date(2026, 6, 15)

        # 1. Active and valid
        d_valid = DiscountCode.objects.create(
            hotel=self.hotel,
            code="VALID20",
            percent=20,
            valid_from=datetime.date(2026, 6, 1),
            valid_to=datetime.date(2026, 6, 30),
            max_uses=10,
            used_count=2,
            is_active=True,
        )
        # 2. Inactive
        d_inactive = DiscountCode.objects.create(
            hotel=self.hotel,
            code="INACTIVE10",
            percent=10,
            valid_from=datetime.date(2026, 6, 1),
            valid_to=datetime.date(2026, 6, 30),
            is_active=False,
        )
        # 3. Expired
        d_expired = DiscountCode.objects.create(
            hotel=self.hotel,
            code="EXPIRED15",
            percent=15,
            valid_from=datetime.date(2026, 5, 1),
            valid_to=datetime.date(2026, 5, 31),
            is_active=True,
        )
        # 4. Future
        d_future = DiscountCode.objects.create(
            hotel=self.hotel,
            code="FUTURE25",
            percent=25,
            valid_from=datetime.date(2026, 7, 1),
            valid_to=datetime.date(2026, 7, 31),
            is_active=True,
        )
        # 5. Depleted max_uses
        d_depleted = DiscountCode.objects.create(
            hotel=self.hotel,
            code="DEPLETED30",
            percent=30,
            valid_from=datetime.date(2026, 6, 1),
            valid_to=datetime.date(2026, 6, 30),
            max_uses=5,
            used_count=5,
            is_active=True,
        )
        # 6. Unlimited uses (max_uses=None)
        d_unlimited = DiscountCode.objects.create(
            hotel=self.hotel,
            code="UNLIMITED5",
            percent=5,
            valid_from=datetime.date(2026, 6, 1),
            valid_to=datetime.date(2026, 6, 30),
            max_uses=None,
            used_count=100,
            is_active=True,
        )

        valid_qs = DiscountCode.objects.valid_now(self.hotel, today=today)
        self.assertIn(d_valid, valid_qs)
        self.assertIn(d_unlimited, valid_qs)
        self.assertNotIn(d_inactive, valid_qs)
        self.assertNotIn(d_expired, valid_qs)
        self.assertNotIn(d_future, valid_qs)
        self.assertNotIn(d_depleted, valid_qs)

    def test_discount_code_manager_get_valid(self):
        """get_valid() retrieves matching normalized code or returns None."""
        today = datetime.date(2026, 6, 15)
        d = DiscountCode.objects.create(
            hotel=self.hotel,
            code="SUMMER20",
            percent=20,
            valid_from=datetime.date(2026, 6, 1),
            valid_to=datetime.date(2026, 6, 30),
            is_active=True,
        )

        # Exact match
        self.assertEqual(DiscountCode.objects.get_valid(self.hotel, "SUMMER20", today=today), d)
        # Case insensitive and whitespace stripped
        self.assertEqual(DiscountCode.objects.get_valid(self.hotel, "  summer20  ", today=today), d)
        # Non-existent code
        self.assertIsNone(DiscountCode.objects.get_valid(self.hotel, "NONEXISTENT", today=today))
        # Empty string
        self.assertIsNone(DiscountCode.objects.get_valid(self.hotel, "", today=today))
        # Wrong hotel
        self.assertIsNone(DiscountCode.objects.get_valid(self.other_hotel, "SUMMER20", today=today))

    def test_discount_code_for_hotel_and_owned_by(self):
        """DiscountCodeQuerySet.for_hotel and .owned_by scope discount codes correctly (P3-03)."""
        dc1 = DiscountCode.objects.create(
            hotel=self.hotel,
            code="SUMMER20",
            percent=20,
            valid_from=datetime.date(2026, 6, 1),
            valid_to=datetime.date(2026, 8, 31),
        )
        dc2 = DiscountCode.objects.create(
            hotel=self.other_hotel,
            code="AUTUMN15",
            percent=15,
            valid_from=datetime.date(2026, 9, 1),
            valid_to=datetime.date(2026, 11, 30),
        )

        hotel_dcs = DiscountCode.objects.for_hotel(self.hotel)
        self.assertIn(dc1, hotel_dcs)
        self.assertNotIn(dc2, hotel_dcs)

        hotel_dcs_id = DiscountCode.objects.for_hotel(self.hotel.id)
        self.assertIn(dc1, hotel_dcs_id)
        self.assertNotIn(dc2, hotel_dcs_id)

        mgr_dcs = DiscountCode.objects.owned_by(self.manager)
        self.assertIn(dc1, mgr_dcs)
        self.assertNotIn(dc2, mgr_dcs)

        other_mgr_dcs = DiscountCode.objects.owned_by(self.other_manager)
        self.assertIn(dc2, other_mgr_dcs)
        self.assertNotIn(dc1, other_mgr_dcs)

