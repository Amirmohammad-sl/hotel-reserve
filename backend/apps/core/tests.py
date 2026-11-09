import json
from datetime import date
from io import StringIO
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.middleware.csrf import _unmask_cipher_token
from django.test import Client, RequestFactory, TestCase, override_settings
from apps.bookings.models import Booking, DiscountCode
from apps.hotels.models import Amenity, Hotel, RoomType
from .decorators import login_required_json, role_required, verified_required
from .forms import form_errors
import logging
from django.conf import settings
from django.http import HttpResponse
from .http import json_error, json_ok, parse_json
from .middleware import RequestLogMiddleware
from .views import (
    bad_request_view,
    csrf_token_view,
    page_not_found_view,
    permission_denied_view,
    server_error_view,
    spa_host_view,
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

    def test_verified_required_unauthenticated(self):
        @verified_required
        def protected_view(request):
            return json_ok({"verified": True})

        req = self.factory.post("/api/verified-only/")
        req.user = AnonymousUser()
        res = protected_view(req)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(json.loads(res.content.decode("utf-8"))["message"], "Authentication required.")

    def test_verified_required_unverified_returns_403(self):
        @verified_required
        def protected_view(request):
            return json_ok({"verified": True})

        req = self.factory.post("/api/verified-only/")
        self.guest_user.email_verified = False
        self.guest_user.save()
        req.user = self.guest_user
        res = protected_view(req)
        self.assertEqual(res.status_code, 403)
        self.assertIn("Email verification required", json.loads(res.content.decode("utf-8"))["message"])

    def test_verified_required_verified_returns_200(self):
        @verified_required
        def protected_view(request):
            return json_ok({"verified": True})

        req = self.factory.post("/api/verified-only/")
        self.guest_user.email_verified = True
        self.guest_user.save()
        req.user = self.guest_user
        res = protected_view(req)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode("utf-8"))["data"], {"verified": True})

    def test_verified_required_method_filtering(self):
        @verified_required(methods=["POST"])
        def mixed_view(request):
            return json_ok({"action": request.method})

        self.guest_user.email_verified = False
        self.guest_user.save()

        # GET request passes even if email is unverified
        req_get = self.factory.get("/api/mixed/")
        req_get.user = self.guest_user
        res_get = mixed_view(req_get)
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(json.loads(res_get.content.decode("utf-8"))["data"], {"action": "GET"})

        # POST request is blocked when unverified
        req_post = self.factory.post("/api/mixed/")
        req_post.user = self.guest_user
        res_post = mixed_view(req_post)
        self.assertEqual(res_post.status_code, 403)

        # POST request succeeds once verified
        self.guest_user.email_verified = True
        self.guest_user.save()
        res_post_verified = mixed_view(req_post)
        self.assertEqual(res_post_verified.status_code, 200)

    def test_verified_required_cbv_method(self):
        class DummyCBV:
            @verified_required
            def handle(self, request):
                return json_ok({"cbv": True})

        cbv = DummyCBV()
        self.guest_user.email_verified = False
        self.guest_user.save()
        req = self.factory.post("/api/cbv/")
        req.user = self.guest_user

        # Unverified -> 403
        res = cbv.handle(req)
        self.assertEqual(res.status_code, 403)

        # Verified -> 200
        self.guest_user.email_verified = True
        self.guest_user.save()
        res_ok = cbv.handle(req)
        self.assertEqual(res_ok.status_code, 200)


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


class SpaHostViewTests(TestCase):
    """Test suite for SPA host template rendering and client-side deep routing (P2-11)."""

    def setUp(self):
        self.client = Client()

    def test_root_path_serves_spa_template(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, '<div id="root"></div>')
        self.assertContains(response, 'src="/static/assets/app.js"')
        self.assertContains(response, 'href="/static/assets/app.css"')
        # Ensure CSRF cookie is seeded for SPA mutations
        self.assertIn("csrftoken", response.cookies)

    def test_deep_link_hotels_detail_serves_spa_template(self):
        response = self.client.get("/hotels/3")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, '<div id="root"></div>')

    def test_deep_link_my_bookings_serves_spa_template(self):
        response = self.client.get("/my-bookings")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_deep_link_manager_path_serves_spa_template(self):
        response = self.client.get("/manager/hotels/create")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_api_routes_not_intercepted_by_spa_catch_all(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": {"status": "ok"}})

    def test_unknown_api_route_returns_json_404_not_spa_html(self):
        response = self.client.get("/api/nonexistent-route-xyz/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        data = response.json()
        self.assertEqual(data.get("message"), "Resource not found.")


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



class RequestLogMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_anonymous_request_logging(self):
        def get_response(req):
            return HttpResponse("OK", status=200)

        middleware = RequestLogMiddleware(get_response)
        request = self.factory.get("/api/test/anonymous/")
        request.user = AnonymousUser()

        with self.assertLogs("apps.core.middleware", level="INFO") as cm:
            response = middleware(request)
            self.assertEqual(response.status_code, 200)

        self.assertTrue(
            any("GET /api/test/anonymous/ 200 user_id=anon duration_ms=" in msg for msg in cm.output),
            f"Expected request log line not found in: {cm.output}",
        )

    def test_authenticated_request_logging(self):
        user = User.objects.create_user(
            username="logger_guest",
            email="logger@hotel.local",
            password="StrongPassword123!",
            role="guest",
        )

        def get_response(req):
            return HttpResponse("OK", status=200)

        middleware = RequestLogMiddleware(get_response)
        request = self.factory.get("/api/test/authenticated/")
        request.user = user

        with self.assertLogs("apps.core.middleware", level="INFO") as cm:
            response = middleware(request)
            self.assertEqual(response.status_code, 200)

        self.assertTrue(
            any(f"GET /api/test/authenticated/ 200 user_id={user.id} duration_ms=" in msg for msg in cm.output),
            f"Expected request log line with user_id={user.id} not found in: {cm.output}",
        )

    def test_request_logging_on_exception(self):
        def get_response(req):
            raise ValueError("Unexpected error inside view")

        middleware = RequestLogMiddleware(get_response)
        request = self.factory.get("/api/test/crash/")
        request.user = AnonymousUser()

        with self.assertLogs("apps.core.middleware", level="INFO") as cm:
            with self.assertRaises(ValueError):
                middleware(request)

        self.assertTrue(
            any("GET /api/test/crash/ 500 user_id=anon duration_ms=" in msg for msg in cm.output),
            f"Expected status 500 on unhandled exception in: {cm.output}",
        )


class LoggingConfigurationTests(TestCase):
    def test_logging_dict_structure(self):
        self.assertTrue(hasattr(settings, "LOGGING"))
        logging_cfg = settings.LOGGING
        self.assertEqual(logging_cfg["version"], 1)

        # Formatters check
        formatters = logging_cfg.get("formatters", {})
        self.assertIn("standard", formatters)
        self.assertIn("verbose", formatters)
        self.assertIn("{asctime}", formatters["standard"]["format"])
        self.assertIn("{levelname}", formatters["standard"]["format"])
        self.assertIn("{name}", formatters["standard"]["format"])

        # Handlers check
        handlers = logging_cfg.get("handlers", {})
        self.assertIn("console", handlers)
        self.assertIn("app_file", handlers)
        self.assertIn("error_file", handlers)
        self.assertIn("security_file", handlers)

        # Rotating file handlers verification
        for handler_name in ["app_file", "error_file", "security_file"]:
            self.assertEqual(
                handlers[handler_name]["class"],
                "logging.handlers.RotatingFileHandler",
            )
            self.assertIn("maxBytes", handlers[handler_name])
            self.assertIn("backupCount", handlers[handler_name])

        # Loggers check
        loggers = logging_cfg.get("loggers", {})
        self.assertIn("", loggers)
        self.assertIn("apps", loggers)
        self.assertIn("security", loggers)
        self.assertIn("django.security", loggers)

    def test_logs_directory_exists(self):
        logs_dir = getattr(settings, "LOGS_DIR", None)
        self.assertIsNotNone(logs_dir)
        self.assertTrue(logs_dir.exists())

    def test_writing_to_rotating_log_files(self):
        logs_dir = settings.LOGS_DIR

        # 1. App logger info
        app_logger = logging.getLogger("apps.core")
        test_info_token = "unique_app_info_token_test_123"
        app_logger.info("Test message %s", test_info_token)

        app_log_file = logs_dir / "app.log"
        self.assertTrue(app_log_file.exists())
        with open(app_log_file, "r", encoding="utf-8") as f:
            app_content = f.read()
        self.assertIn(test_info_token, app_content)

        # 2. Error logger
        test_error_token = "unique_error_token_test_456"
        app_logger.error("Test error %s", test_error_token)

        error_log_file = logs_dir / "error.log"
        self.assertTrue(error_log_file.exists())
        with open(error_log_file, "r", encoding="utf-8") as f:
            err_content = f.read()
        self.assertIn(test_error_token, err_content)

        # 3. Security logger
        sec_logger = logging.getLogger("security")
        test_sec_token = "unique_security_token_test_789"
        sec_logger.info("Security audit %s", test_sec_token)

        sec_log_file = logs_dir / "security.log"
        self.assertTrue(sec_log_file.exists())
        with open(sec_log_file, "r", encoding="utf-8") as f:
            sec_content = f.read()
        self.assertIn(test_sec_token, sec_content)

    def test_e2e_request_logging_via_client(self):
        client = Client()
        response = client.get("/api/health/")
        self.assertEqual(response.status_code, 200)

        app_log_file = settings.LOGS_DIR / "app.log"
        self.assertTrue(app_log_file.exists())
        with open(app_log_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("GET /api/health/ 200 user_id=anon", content)



class CoreLoggingCoverageTests(TestCase):
    """Tests verifying logging coverage in core decorators and views (P3-09)."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_log_user",
            email="test_log@example.com",
            password="password123",
            role=User.Role.GUEST,
        )

    def test_login_required_unauthenticated_logs_security_warning(self):
        @login_required_json
        def dummy_view(request):
            return json_ok({})

        req = self.factory.get("/api/dummy-secure/")
        req.user = AnonymousUser()

        with self.assertLogs("apps.security", level="WARNING") as cm:
            res = dummy_view(req)
            self.assertEqual(res.status_code, 401)
            self.assertTrue(any("Unauthenticated access attempt to /api/dummy-secure/" in m for m in cm.output))

    def test_role_required_forbidden_role_logs_security_warning(self):
        @role_required("manager")
        def manager_view(request):
            return json_ok({})

        req = self.factory.get("/api/manager-only/")
        req.user = self.user

        with self.assertLogs("apps.security", level="WARNING") as cm:
            res = manager_view(req)
            self.assertEqual(res.status_code, 403)
            self.assertTrue(any("Forbidden role access: user_id=" in m for m in cm.output))

    def test_custom_error_views_logging(self):
        from apps.core.views import bad_request_view, permission_denied_view, page_not_found_view, server_error_view

        req = self.factory.get("/api/test-400/")
        with self.assertLogs("apps.core.views", level="WARNING") as cm:
            res = bad_request_view(req, exception=Exception("Bad input"))
            self.assertEqual(res.status_code, 400)
            self.assertTrue(any("Bad request on /api/test-400/" in m for m in cm.output))

        req = self.factory.get("/api/test-403/")
        with self.assertLogs("apps.security", level="WARNING") as cm:
            res = permission_denied_view(req, exception=Exception("Denied"))
            self.assertEqual(res.status_code, 403)
            self.assertTrue(any("Permission denied on /api/test-403/" in m for m in cm.output))

        req = self.factory.get("/api/test-404/")
        with self.assertLogs("apps.core.views", level="INFO") as cm:
            res = page_not_found_view(req, exception=Exception("Not found"))
            self.assertEqual(res.status_code, 404)
            self.assertTrue(any("Resource not found on /api/test-404/" in m for m in cm.output))

        req = self.factory.get("/api/test-500/")
        with self.assertLogs("apps.core.views", level="ERROR") as cm:
            res = server_error_view(req)
            self.assertEqual(res.status_code, 500)
            self.assertTrue(any("Internal server error on /api/test-500/" in m for m in cm.output))
