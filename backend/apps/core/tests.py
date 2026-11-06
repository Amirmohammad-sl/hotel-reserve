import json
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.middleware.csrf import _unmask_cipher_token
from django.test import Client, RequestFactory, TestCase, override_settings
from .decorators import login_required_json, role_required
from .forms import form_errors
from .http import json_error, json_ok, parse_json
from .views import (
    bad_request_view,
    csrf_token_view,
    page_not_found_view,
    permission_denied_view,
    server_error_view,
)

User = get_user_model()


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_returns_ok(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": {"status": "ok"}})


class HttpHelpersTests(TestCase):
    def test_json_ok_default(self):
        res = json_ok()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode("utf-8")), {"data": {}})

    def test_json_ok_with_data_and_extra(self):
        res = json_ok({"status": "ok"}, extra_key="extra_val")
        self.assertEqual(res.status_code, 200)
        payload = json.loads(res.content.decode("utf-8"))
        self.assertEqual(payload["data"], {"status": "ok"})
        self.assertEqual(payload["extra_key"], "extra_val")

    def test_json_error(self):
        res = json_error("Validation error", errors={"field": ["Required"]}, status=422)
        self.assertEqual(res.status_code, 422)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Validation error")
        self.assertEqual(data["errors"], {"field": ["Required"]})

    def test_parse_json_valid(self):
        factory = RequestFactory()
        req = factory.post("/api/test/", data='{"key": "value"}', content_type="application/json")
        self.assertEqual(parse_json(req), {"key": "value"})

    def test_parse_json_empty(self):
        factory = RequestFactory()
        req = factory.post("/api/test/", data="", content_type="application/json")
        self.assertEqual(parse_json(req), {})

    def test_parse_json_invalid(self):
        factory = RequestFactory()
        req = factory.post("/api/test/", data="invalid-json", content_type="application/json")
        with self.assertRaises(ValueError):
            parse_json(req)


class SampleTestForm(forms.Form):
    title = forms.CharField(max_length=10)
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("title") == "invalid":
            raise forms.ValidationError("Overall form error message.")
        return cleaned_data


class FormsHelperTests(TestCase):
    def test_form_errors_with_field_errors(self):
        form = SampleTestForm(data={"title": "", "email": "not-an-email"})
        self.assertFalse(form.is_valid())
        errors = form_errors(form)
        self.assertIn("title", errors)
        self.assertIn("email", errors)
        self.assertTrue(len(errors["title"]) > 0)
        self.assertTrue(len(errors["email"]) > 0)

    def test_form_errors_with_non_field_errors(self):
        form = SampleTestForm(data={"title": "invalid", "email": "valid@example.com"})
        self.assertFalse(form.is_valid())
        errors = form_errors(form)
        self.assertIn("__all__", errors)
        self.assertEqual(errors["__all__"], ["Overall form error message."])

    def test_form_errors_empty_for_valid_form(self):
        form = SampleTestForm(data={"title": "valid", "email": "valid@example.com"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form_errors(form), {})


class DecoratorsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.guest_user = User.objects.create_user(
            username="guest1",
            email="guest1@example.com",
            password="password123",
            role=User.Role.GUEST,
        )
        self.manager_user = User.objects.create_user(
            username="manager1",
            email="manager1@example.com",
            password="password123",
            role=User.Role.MANAGER,
        )

    def test_login_required_json_unauthenticated(self):
        @login_required_json
        def dummy_view(request):
            return json_ok({"secret": "data"})

        req = self.factory.get("/api/dummy/")
        req.user = AnonymousUser()
        res = dummy_view(req)
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Authentication required.")

    def test_login_required_json_authenticated(self):
        @login_required_json
        def dummy_view(request):
            return json_ok({"secret": "data"})

        req = self.factory.get("/api/dummy/")
        req.user = self.guest_user
        res = dummy_view(req)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["data"], {"secret": "data"})

    def test_role_required_unauthenticated(self):
        @role_required(User.Role.MANAGER)
        def manager_view(request):
            return json_ok({"manager": "area"})

        req = self.factory.get("/api/manager/")
        req.user = AnonymousUser()
        res = manager_view(req)
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Authentication required.")

    def test_role_required_wrong_role(self):
        @role_required(User.Role.MANAGER)
        def manager_view(request):
            return json_ok({"manager": "area"})

        req = self.factory.get("/api/manager/")
        req.user = self.guest_user
        res = manager_view(req)
        self.assertEqual(res.status_code, 403)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Permission denied.")

    def test_role_required_correct_role(self):
        @role_required(User.Role.MANAGER)
        def manager_view(request):
            return json_ok({"manager": "area"})

        req = self.factory.get("/api/manager/")
        req.user = self.manager_user
        res = manager_view(req)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["data"], {"manager": "area"})

    def test_role_required_multiple_allowed_roles(self):
        @role_required(User.Role.GUEST, User.Role.MANAGER)
        def any_role_view(request):
            return json_ok({"allowed": True})

        req_guest = self.factory.get("/api/common/")
        req_guest.user = self.guest_user
        self.assertEqual(any_role_view(req_guest).status_code, 200)

        req_manager = self.factory.get("/api/common/")
        req_manager.user = self.manager_user
        self.assertEqual(any_role_view(req_manager).status_code, 200)


class CsrfEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_csrf_endpoint_sets_cookie_and_returns_token(self):
        res = self.client.get("/api/auth/csrf/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("data", data)
        self.assertIn("csrfToken", data["data"])
        self.assertTrue(len(data["data"]["csrfToken"]) >= 32)
        self.assertIn("csrftoken", res.cookies)
        cookie_token = res.cookies["csrftoken"].value
        masked_token = data["data"]["csrfToken"]
        self.assertEqual(_unmask_cipher_token(masked_token), cookie_token)


class ErrorHandlersTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_api_404_handler_direct(self):
        req = self.factory.get("/api/not-existing-endpoint/")
        res = page_not_found_view(req)
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Resource not found.")

    def test_api_500_handler_direct(self):
        req = self.factory.get("/api/error-endpoint/")
        res = server_error_view(req)
        self.assertEqual(res.status_code, 500)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Internal server error.")

    def test_api_400_handler_direct(self):
        req = self.factory.get("/api/bad-endpoint/")
        res = bad_request_view(req)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Bad request.")

    def test_api_403_handler_direct(self):
        req = self.factory.get("/api/forbidden-endpoint/")
        res = permission_denied_view(req)
        self.assertEqual(res.status_code, 403)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Permission denied.")

    @override_settings(DEBUG=False)
    def test_client_404_returns_json_under_api(self):
        res = self.client.get("/api/non-existent-route-xyz/")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json(), {"message": "Resource not found."})


from io import StringIO
from datetime import date
from django.core.management import call_command
from apps.bookings.models import Booking, DiscountCode
from apps.hotels.models import Amenity, Hotel, RoomType


class SeedDemoCommandTests(TestCase):
    """Test suite for seed_demo management command, idempotency, and --reset flag."""

    def test_seed_demo_creates_required_entities(self):
        out = StringIO()
        call_command("seed_demo", stdout=out)
        output = out.getvalue()
        self.assertIn("Successfully seeded demo data", output)

        # 2 managers and 5 guests
        managers = User.objects.filter(role=User.Role.MANAGER, username__startswith="manager")
        guests = User.objects.filter(role=User.Role.GUEST, username__startswith="guest")
        self.assertEqual(managers.count(), 2)
        self.assertEqual(guests.count(), 5)

        # Authenticate known passwords
        self.assertTrue(self.client.login(username="manager1", password="Manager123!"))
        self.client.logout()
        self.assertTrue(self.client.login(username="guest1", password="Guest123!"))
        self.client.logout()

        # >= 6 hotels in >= 3 cities
        hotels = Hotel.objects.all()
        self.assertGreaterEqual(hotels.count(), 6)
        distinct_cities = set(Hotel.objects.values_list("city", flat=True))
        self.assertGreaterEqual(len(distinct_cities), 3)

        # 2 to 4 room types each with amenities
        for hotel in hotels:
            rt_count = hotel.room_types.count()
            self.assertTrue(2 <= rt_count <= 4, f"Hotel {hotel.name} has {rt_count} room types, expected 2-4")
            for rt in hotel.room_types.all():
                self.assertTrue(rt.amenities.exists(), f"RoomType {rt.title} has no amenities")

        # Discounts exist
        discounts = DiscountCode.objects.all()
        self.assertGreaterEqual(discounts.count(), 6)

        # ~20 bookings with past, current, future, and cancelled states
        bookings = Booking.objects.all()
        self.assertGreaterEqual(bookings.count(), 20)

        today = date.today()
        past_bookings = bookings.filter(status=Booking.Status.CONFIRMED, check_out__lte=today)
        current_bookings = bookings.filter(status=Booking.Status.CONFIRMED, check_in__lte=today, check_out__gt=today)
        future_bookings = bookings.filter(status=Booking.Status.CONFIRMED, check_in__gt=today)
        cancelled_bookings = bookings.filter(status=Booking.Status.CANCELLED)

        self.assertTrue(past_bookings.exists(), "No past bookings found")
        self.assertTrue(current_bookings.exists(), "No current bookings found")
        self.assertTrue(future_bookings.exists(), "No future bookings found")
        self.assertTrue(cancelled_bookings.exists(), "No cancelled bookings found")

        # Ensure cancelled bookings have cancelled_at populated
        for b in cancelled_bookings:
            self.assertIsNotNone(b.cancelled_at)

    def test_seed_demo_idempotency_does_not_duplicate(self):
        # Run first time
        call_command("seed_demo", stdout=StringIO())
        counts_before = {
            "users": User.objects.count(),
            "hotels": Hotel.objects.count(),
            "room_types": RoomType.objects.count(),
            "amenities": Amenity.objects.count(),
            "discounts": DiscountCode.objects.count(),
            "bookings": Booking.objects.count(),
        }

        # Run second time without --reset
        call_command("seed_demo", stdout=StringIO())
        counts_after = {
            "users": User.objects.count(),
            "hotels": Hotel.objects.count(),
            "room_types": RoomType.objects.count(),
            "amenities": Amenity.objects.count(),
            "discounts": DiscountCode.objects.count(),
            "bookings": Booking.objects.count(),
        }

        self.assertEqual(counts_before, counts_after, "Re-running seed_demo duplicated records!")

    def test_seed_demo_reset_flag_rebuilds_cleanly(self):
        # Initial run
        call_command("seed_demo", stdout=StringIO())
        initial_bookings_count = Booking.objects.count()

        # Run with --reset
        out = StringIO()
        call_command("seed_demo", reset=True, stdout=out)
        self.assertIn("Reset requested", out.getvalue())
        self.assertIn("Successfully seeded demo data", out.getvalue())
        self.assertEqual(Booking.objects.count(), initial_bookings_count)
