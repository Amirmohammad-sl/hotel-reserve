from django.conf import settings
from django.core import mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from unittest.mock import patch
from django.contrib.sessions.models import Session
import json
from django.contrib.admin.sites import site
from django.db import IntegrityError
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from .admin import CustomUserAdmin
from .forms import LoginForm, RegisterForm, user_to_dict
from .models import User
from .tokens import (
    VERIFICATION_TOKEN_MAX_AGE,
    build_verification_url,
    generate_verification_token,
    get_signer,
    send_verification_email,
    verify_token,
)


class UserModelTests(TestCase):
    def test_create_guest_user_defaults(self):
        user = User.objects.create_user(
            username="guest1",
            email="guest1@example.com",
            password="securepassword123",
        )
        self.assertEqual(user.role, User.Role.GUEST)
        self.assertTrue(user.is_guest)
        self.assertFalse(user.is_manager)
        self.assertFalse(user.email_verified)
        self.assertEqual(user.phone, "")
        self.assertEqual(str(user), "guest1 (Guest)")

    def test_create_manager_user(self):
        user = User.objects.create_user(
            username="manager1",
            email="manager1@example.com",
            password="securepassword123",
            role=User.Role.MANAGER,
            phone="09123456789",
            email_verified=True,
        )
        self.assertEqual(user.role, User.Role.MANAGER)
        self.assertTrue(user.is_manager)
        self.assertFalse(user.is_guest)
        self.assertTrue(user.email_verified)
        self.assertEqual(user.phone, "09123456789")
        self.assertEqual(str(user), "manager1 (Manager)")

    def test_email_uniqueness_enforced(self):
        User.objects.create_user(
            username="first_user",
            email="duplicate@example.com",
            password="password123",
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="second_user",
                email="duplicate@example.com",
                password="password123",
            )

    def test_create_superuser_defaults(self):
        admin_user = User.objects.create_superuser(
            username="superadmin",
            email="admin@example.com",
            password="adminpassword123",
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertEqual(admin_user.role, User.Role.MANAGER)
        self.assertTrue(admin_user.is_manager)

    def test_user_managers_and_guests_querysets(self):
        m1 = User.objects.create_user(username='m1', email='m1@ex.com', password='p', role=User.Role.MANAGER)
        m2 = User.objects.create_user(username='m2', email='m2@ex.com', password='p', role=User.Role.MANAGER)
        g1 = User.objects.create_user(username='g1', email='g1@ex.com', password='p')
        g2 = User.objects.create_user(username='g2', email='g2@ex.com', password='p')

        managers = list(User.objects.managers().values_list('id', flat=True))
        guests = list(User.objects.guests().values_list('id', flat=True))

        self.assertCountEqual(managers, [m1.id, m2.id])
        self.assertCountEqual(guests, [g1.id, g2.id])
        self.assertEqual(list(User.objects.filter(is_active=True).managers().values_list('id', flat=True)), managers)

    def test_create_user_role_validation(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username='no_email', email='', password='p')

        with self.assertRaises(ValueError):
            User.objects.create_user(username='bad_role', email='bad@ex.com', password='p', role='alien')

    def test_create_superuser_role_validation(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(username='bad_admin', email='badadmin@ex.com', password='p', role=User.Role.GUEST)


class UserAdminTests(TestCase):
    def test_custom_user_admin_registered(self):
        self.assertIn(User, site._registry)
        admin_instance = site._registry[User]
        self.assertIsInstance(admin_instance, CustomUserAdmin)
        self.assertIn("role", admin_instance.list_display)
        self.assertIn("email_verified", admin_instance.list_filter)

    def test_user_admin_changelist_view_renders_successfully(self):
        User.objects.create_superuser(
            username="admin_user_test",
            email="admin_user_test@example.com",
            password="adminpassword123",
        )
        self.client.login(username="admin_user_test", password="adminpassword123")
        url = reverse("admin:accounts_user_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class UserSerializerTests(TestCase):
    def test_user_to_dict_matches_contract(self):
        user = User.objects.create_user(
            username="ser_user",
            email="ser@example.com",
            password="pass12345User!",
            role=User.Role.MANAGER,
        )
        result = user_to_dict(user)
        self.assertEqual(
            result,
            {
                "id": user.id,
                "username": "ser_user",
                "email": "ser@example.com",
                "role": "manager",
                "email_verified": False,
            },
        )


class RegisterFormTests(TestCase):
    def test_register_form_valid_guest(self):
        form = RegisterForm(
            data={
                "username": "newguest",
                "email": "newguest@example.com",
                "password": "StrongPassword123!",
                "password2": "StrongPassword123!",
                "role": "guest",
                "phone": "09121111111",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, "newguest")
        self.assertEqual(user.email, "newguest@example.com")
        self.assertEqual(user.role, User.Role.GUEST)
        self.assertEqual(user.phone, "09121111111")
        self.assertTrue(user.check_password("StrongPassword123!"))

    def test_register_form_valid_manager_default_role(self):
        form = RegisterForm(
            data={
                "username": "newmgr",
                "email": "newmgr@example.com",
                "password": "StrongPassword123!",
                "password2": "StrongPassword123!",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, User.Role.GUEST)

    def test_register_form_password_mismatch(self):
        form = RegisterForm(
            data={
                "username": "mismatch",
                "email": "mismatch@example.com",
                "password": "StrongPassword123!",
                "password2": "DifferentPassword123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        self.assertEqual(form.errors["password2"], ["Passwords do not match."])

    def test_register_form_duplicate_username(self):
        User.objects.create_user(
            username="existing_user",
            email="unique1@example.com",
            password="StrongPassword123!",
        )
        form = RegisterForm(
            data={
                "username": "existing_user",
                "email": "unique2@example.com",
                "password": "StrongPassword123!",
                "password2": "StrongPassword123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("already exists", form.errors["username"][0])

    def test_register_form_duplicate_email(self):
        User.objects.create_user(
            username="unique_user",
            email="duplicate@example.com",
            password="StrongPassword123!",
        )
        form = RegisterForm(
            data={
                "username": "another_user",
                "email": "duplicate@example.com",
                "password": "StrongPassword123!",
                "password2": "StrongPassword123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("already exists", form.errors["email"][0])


class LoginFormTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="CorrectPassword123!",
            role=User.Role.GUEST,
        )

    def test_login_form_valid_with_username(self):
        request = self.factory.post("/api/auth/login/")
        form = LoginForm(
            data={
                "username_or_email": "loginuser",
                "password": "CorrectPassword123!",
            },
            request=request,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.get_user(), self.user)

    def test_login_form_valid_with_email(self):
        request = self.factory.post("/api/auth/login/")
        form = LoginForm(
            data={
                "username_or_email": "loginuser@example.com",
                "password": "CorrectPassword123!",
            },
            request=request,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.get_user(), self.user)

    def test_login_form_wrong_password_yields_field_error(self):
        request = self.factory.post("/api/auth/login/")
        form = LoginForm(
            data={
                "username_or_email": "loginuser",
                "password": "WrongPassword123!",
            },
            request=request,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"], ["Invalid password."])

    def test_login_form_unknown_identifier_yields_field_error(self):
        request = self.factory.post("/api/auth/login/")
        form = LoginForm(
            data={
                "username_or_email": "nonexistent@example.com",
                "password": "SomePassword123!",
            },
            request=request,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username_or_email", form.errors)
        self.assertEqual(form.errors["username_or_email"], ["Invalid username or email."])

    def test_login_form_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        request = self.factory.post("/api/auth/login/")
        form = LoginForm(
            data={
                "username_or_email": "loginuser",
                "password": "CorrectPassword123!",
            },
            request=request,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)


class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="existingguest",
            email="existing@example.com",
            password="StrongPassword123!",
            role=User.Role.GUEST,
        )

    def test_register_view_success(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "role": "manager",
            "phone": "09129999999",
        }
        response = self.client.post(
            reverse("accounts:register"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        res_data = response.json()
        self.assertIn("data", res_data)
        user_data = res_data["data"]
        self.assertEqual(user_data["username"], "newuser")
        self.assertEqual(user_data["email"], "newuser@example.com")
        self.assertEqual(user_data["role"], "manager")
        self.assertFalse(user_data["email_verified"])

        # Check DB
        db_user = User.objects.get(username="newuser")
        self.assertEqual(db_user.role, User.Role.MANAGER)
        self.assertEqual(db_user.phone, "09129999999")
        self.assertTrue(db_user.check_password("StrongPassword123!"))

    def test_register_view_validation_error(self):
        payload = {
            "username": "existingguest",
            "email": "invalid-email",
            "password": "pass",
            "password2": "different",
        }
        response = self.client.post(
            reverse("accounts:register"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.json()
        self.assertEqual(res_data["message"], "Validation failed.")
        self.assertIn("username", res_data["errors"])
        self.assertIn("email", res_data["errors"])
        self.assertIn("password2", res_data["errors"])

    def test_register_view_invalid_json(self):
        response = self.client.post(
            reverse("accounts:register"),
            data="{invalid_json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Invalid JSON body.")

    def test_register_view_method_not_allowed(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 405)

    def test_login_view_success_with_username(self):
        payload = {
            "username_or_email": "existingguest",
            "password": "StrongPassword123!",
        }
        response = self.client.post(
            reverse("accounts:login"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertEqual(res_data["data"]["username"], "existingguest")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.id)

    def test_login_view_success_with_email(self):
        payload = {
            "username_or_email": "existing@example.com",
            "password": "StrongPassword123!",
        }
        response = self.client.post(
            reverse("accounts:login"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["username"], "existingguest")

    def test_login_view_remember_me_options(self):
        # remember_me = True (1209600s / 2 weeks)
        response_remember = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "existingguest",
                "password": "StrongPassword123!",
                "remember_me": True,
            }),
            content_type="application/json",
        )
        self.assertEqual(response_remember.status_code, 200)
        self.assertFalse(self.client.session.get_expire_at_browser_close())

        # remember_me = False (expires at browser close)
        response_no_remember = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "existingguest",
                "password": "StrongPassword123!",
                "remember_me": False,
            }),
            content_type="application/json",
        )
        self.assertEqual(response_no_remember.status_code, 200)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_view_wrong_password_returns_400_with_field_errors(self):
        payload = {
            "username_or_email": "existingguest",
            "password": "WrongPassword!",
        }
        response = self.client.post(
            reverse("accounts:login"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.json()
        self.assertEqual(res_data["message"], "Invalid credentials.")
        self.assertIn("password", res_data["errors"])
        self.assertEqual(res_data["errors"]["password"], ["Invalid password."])

    def test_login_view_unknown_user_returns_400_with_field_errors(self):
        payload = {
            "username_or_email": "unknown_user",
            "password": "SomePassword123!",
        }
        response = self.client.post(
            reverse("accounts:login"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.json()
        self.assertEqual(res_data["message"], "Invalid credentials.")
        self.assertIn("username_or_email", res_data["errors"])

    def test_me_view_unauthenticated_returns_data_null(self):
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": None})

    def test_me_view_authenticated_returns_user_object(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, 200)
        res_data = response.json()["data"]
        self.assertEqual(res_data["id"], self.user.id)
        self.assertEqual(res_data["username"], "existingguest")
        self.assertEqual(res_data["email"], "existing@example.com")
        self.assertEqual(res_data["role"], "guest")
        self.assertEqual(res_data["email_verified"], False)
        self.assertIn("last_login", res_data)

    def test_logout_view_unauthenticated_returns_401(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["message"], "Authentication required.")

    def test_logout_view_authenticated_logs_out_session(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["message"], "Successfully logged out.")

        # Confirm session is cleared
        me_response = self.client.get(reverse("accounts:me"))
        self.assertEqual(me_response.json(), {"data": None})

    def test_auth_full_cycle_dod(self):
        # 1. Fetch CSRF token
        csrf_res = self.client.get(reverse("accounts:csrf"))
        self.assertEqual(csrf_res.status_code, 200)
        self.assertIn("csrftoken", self.client.cookies)

        # 2. Register
        reg_payload = {
            "username": "cycle_user",
            "email": "cycle@example.com",
            "password": "ComplexPassword123!",
            "password2": "ComplexPassword123!",
            "role": "guest",
        }
        reg_res = self.client.post(
            reverse("accounts:register"),
            data=json.dumps(reg_payload),
            content_type="application/json",
        )
        self.assertEqual(reg_res.status_code, 201)

        # 3. Wrong password -> 400 with field errors
        wrong_login_res = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "cycle_user",
                "password": "WrongPassword123!",
            }),
            content_type="application/json",
        )
        self.assertEqual(wrong_login_res.status_code, 400)
        self.assertIn("password", wrong_login_res.json()["errors"])

        # 4. Correct login
        login_res = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "cycle_user",
                "password": "ComplexPassword123!",
            }),
            content_type="application/json",
        )
        self.assertEqual(login_res.status_code, 200)

        # 5. /me/ returns user
        me_res = self.client.get(reverse("accounts:me"))
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["data"]["username"], "cycle_user")

        # 6. Logout
        logout_res = self.client.post(reverse("accounts:logout"))
        self.assertEqual(logout_res.status_code, 200)

        # 7. /me/ returns null
        after_logout_me = self.client.get(reverse("accounts:me"))
        self.assertEqual(after_logout_me.json(), {"data": None})



class SessionManagementTests(TestCase):
    """Tests for course-required session management, cookie flags, and lifecycle (P3-06)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="session_tester",
            email="session@example.com",
            password="SecurePassword123!",
        )

    def test_session_engine_is_database_backed(self):
        self.assertEqual(settings.SESSION_ENGINE, "django.contrib.sessions.backends.db")
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, "Lax")
        self.assertEqual(settings.SESSION_COOKIE_AGE, 1209600)

    def test_login_stores_last_login_in_session_and_me_returns_it(self):
        response = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "session_tester",
                "password": "SecurePassword123!",
                "remember_me": True,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        session_last_login = self.client.session.get("last_login")
        self.assertIsNotNone(session_last_login)
        self.assertEqual(response.json()["data"]["last_login"], session_last_login)

        # GET /api/auth/me/ returns session last_login
        me_res = self.client.get(reverse("accounts:me"))
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["data"]["last_login"], session_last_login)

    def test_logout_flushes_session_from_database(self):
        # 1. Login to create database session
        login_res = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "session_tester",
                "password": "SecurePassword123!",
            }),
            content_type="application/json",
        )
        self.assertEqual(login_res.status_code, 200)
        session_key = self.client.session.session_key
        self.assertIsNotNone(session_key)
        self.assertTrue(Session.objects.filter(session_key=session_key).exists())

        # 2. Logout flushes session
        logout_res = self.client.post(reverse("accounts:logout"))
        self.assertEqual(logout_res.status_code, 200)

        # 3. Session key no longer exists in DB
        self.assertFalse(Session.objects.filter(session_key=session_key).exists())

        # 4. /me/ returns null
        me_res = self.client.get(reverse("accounts:me"))
        self.assertEqual(me_res.json(), {"data": None})

    def test_cookie_flags_in_response(self):
        response = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "session_tester",
                "password": "SecurePassword123!",
                "remember_me": True,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        cookie = response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["max-age"], 1209600)

    def test_remember_me_false_session_cookie(self):
        response = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "session_tester",
                "password": "SecurePassword123!",
                "remember_me": False,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertTrue(self.client.session.get_expire_at_browser_close())



class AuthLoggingCoverageTests(TestCase):
    """Tests verifying logging coverage in accounts views (P3-09)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="logging_user",
            email="logging_user@example.com",
            password="StrongPassword123!",
            role=User.Role.GUEST,
        )

    def test_register_success_logging(self):
        payload = {
            "username": "new_audit_user",
            "email": "new_audit@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "role": "guest",
        }
        with self.assertLogs("apps.security", level="INFO") as cm:
            res = self.client.post(
                reverse("accounts:register"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 201)
            self.assertTrue(any("User registered successfully" in m and "new_audit_user" in m for m in cm.output))

    def test_register_validation_failure_logging(self):
        payload = {
            "username": "bad",
            "email": "not-an-email",
            "password": "123",
            "password2": "456",
        }
        with self.assertLogs("apps.accounts.views", level="WARNING") as cm:
            res = self.client.post(
                reverse("accounts:register"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 400)
            self.assertTrue(any("Registration validation failed" in m for m in cm.output))

    def test_login_success_and_logout_logging(self):
        login_payload = {
            "username_or_email": "logging_user",
            "password": "StrongPassword123!",
            "remember_me": True,
        }
        with self.assertLogs("apps.security", level="INFO") as cm:
            res = self.client.post(
                reverse("accounts:login"),
                data=json.dumps(login_payload),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 200)
            self.assertTrue(any("User logged in successfully" in m and "logging_user" in m for m in cm.output))

        with self.assertLogs("apps.security", level="INFO") as cm:
            res = self.client.post(reverse("accounts:logout"))
            self.assertEqual(res.status_code, 200)
            self.assertTrue(any("User logged out: user_id=" in m and "logging_user" in m for m in cm.output))

    def test_login_failure_logging(self):
        bad_payload = {
            "username_or_email": "logging_user",
            "password": "WrongPassword!",
        }
        with self.assertLogs("apps.security", level="WARNING") as cm:
            res = self.client.post(
                reverse("accounts:login"),
                data=json.dumps(bad_payload),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 400)
            self.assertTrue(any("Login failed for identifier=logging_user" in m for m in cm.output))


class EmailVerificationTests(TestCase):
    """Unit and integration test suite for email verification flow (P4-01)."""

    def setUp(self):
        self.guest = User.objects.create_user(
            username="unverified_guest",
            email="unverified@example.com",
            password="StrongPassword123!",
            role=User.Role.GUEST,
            email_verified=False,
        )
        self.manager = User.objects.create_user(
            username="unverified_manager",
            email="manager_unverified@example.com",
            password="StrongPassword123!",
            role=User.Role.MANAGER,
            email_verified=False,
        )

    def test_token_generation_and_verification(self):
        token = generate_verification_token(self.guest)
        self.assertIsInstance(token, str)
        self.assertIn(":", token)

        user = verify_token(token)
        self.assertEqual(user.id, self.guest.id)
        self.assertEqual(user.username, self.guest.username)

    def test_token_expired(self):
        token = generate_verification_token(self.guest)
        # Verify token unsign with max_age=-1 raises SignatureExpired
        signer = get_signer()
        with self.assertRaises(SignatureExpired):
            signer.unsign(token, max_age=-1)

        # Endpoint with expired token returns 400
        with patch("apps.accounts.views.verify_token", side_effect=SignatureExpired("Expired")):
            res = self.client.post(
                reverse("accounts:verify-email"),
                data=json.dumps({"token": token}),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 400)
            self.assertIn("expired", res.json()["message"].lower())

    def test_token_bad_signature(self):
        # Malformed or tampered token
        res = self.client.post(
            reverse("accounts:verify-email"),
            data=json.dumps({"token": "invalid:bad:token:xyz"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("invalid", res.json()["message"].lower())

        # Empty token
        res_empty = self.client.post(
            reverse("accounts:verify-email"),
            data=json.dumps({"token": ""}),
            content_type="application/json",
        )
        self.assertEqual(res_empty.status_code, 400)

    def test_verify_email_endpoint_success(self):
        self.assertFalse(self.guest.email_verified)
        token = generate_verification_token(self.guest)

        with self.assertLogs("apps.security", level="INFO") as sec_logs:
            res = self.client.post(
                reverse("accounts:verify-email"),
                data=json.dumps({"token": token}),
                content_type="application/json",
            )
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(data["id"], self.guest.id)
        self.assertTrue(data["email_verified"])

        self.guest.refresh_from_db()
        self.assertTrue(self.guest.email_verified)
        self.assertTrue(any("Email verified successfully" in msg for msg in sec_logs.output))

    def test_registration_triggers_verification_email(self):
        mail.outbox.clear()
        reg_payload = {
            "username": "verify_flow_user",
            "email": "verifyflow@example.com",
            "password": "Password123!",
            "password2": "Password123!",
            "role": "guest",
        }
        res = self.client.post(
            reverse("accounts:register"),
            data=json.dumps(reg_payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 201)
        user_id = res.json()["data"]["id"]
        new_user = User.objects.get(pk=user_id)
        self.assertFalse(new_user.email_verified)

        # Check console/outbox email
        self.assertEqual(len(mail.outbox), 1)
        email_msg = mail.outbox[0]
        self.assertIn("Verify your email address", email_msg.subject)
        self.assertIn("verifyflow@example.com", email_msg.to)
        self.assertIn("/verify-email?token=", email_msg.body)

        # Extract token from verification URL in email body
        token = email_msg.body.split("token=")[1].split()[0]
        verify_res = self.client.post(
            reverse("accounts:verify-email"),
            data=json.dumps({"token": token}),
            content_type="application/json",
        )
        self.assertEqual(verify_res.status_code, 200)
        self.assertTrue(verify_res.json()["data"]["email_verified"])
        new_user.refresh_from_db()
        self.assertTrue(new_user.email_verified)

    def test_resend_verification_endpoint(self):
        mail.outbox.clear()
        resend_url = reverse("accounts:resend-verification")

        # Anonymous request returns 401
        res_anon = self.client.post(resend_url)
        self.assertEqual(res_anon.status_code, 401)

        # Logged-in unverified user gets 200 and receives email
        self.client.force_login(self.guest)
        with self.assertLogs("apps.security", level="INFO") as sec_logs:
            res_auth = self.client.post(resend_url)
        self.assertEqual(res_auth.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.guest.email, mail.outbox[0].to)
        self.assertTrue(any("Verification email resent" in msg for msg in sec_logs.output))

        # Already verified user returns 400
        self.guest.email_verified = True
        self.guest.save()
        res_already = self.client.post(resend_url)
        self.assertEqual(res_already.status_code, 400)
        self.assertIn("already verified", res_already.json()["message"].lower())

    def test_unverified_guard_on_booking_create(self):
        # Unverified guest cannot create booking -> 403
        self.client.force_login(self.guest)
        res = self.client.post(
            reverse("bookings:booking-create"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("Email verification required", res.json()["message"])

    def test_unverified_guard_on_hotel_create(self):
        # Unverified manager cannot create hotel -> 403
        self.client.force_login(self.manager)
        url = reverse("hotels:manager_hotels_list_create")
        res = self.client.post(
            url,
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("Email verification required", res.json()["message"])

        # But unverified manager can view their hotels list -> 200
        res_get = self.client.get(url)
        self.assertEqual(res_get.status_code, 200)


    def test_send_verification_email_handles_smtp_exception(self):
        with patch("apps.accounts.tokens.send_mail", side_effect=RuntimeError("SMTP connection dropped")):
            with self.assertLogs("apps.accounts.tokens", level="ERROR") as log_cm:
                sent = send_verification_email(self.guest)
                self.assertFalse(sent)
                self.assertTrue(any("Failed to send verification email" in m for m in log_cm.output))

    def test_resend_verification_email_failure_returns_500(self):
        self.client.force_login(self.guest)
        with patch("apps.accounts.views.send_verification_email", return_value=False):
            res = self.client.post(reverse("accounts:resend-verification"))
            self.assertEqual(res.status_code, 500)
            self.assertIn("Failed to send verification email", res.json()["message"])

    def test_build_verification_url_format(self):
        token = generate_verification_token(self.guest)
        url = build_verification_url(token)
        self.assertTrue(url.startswith("http"))
        self.assertIn("/verify-email?token=", url)
        self.assertIn(token, url)

    def test_verify_token_invalid_types_and_payloads(self):
        # Empty or non-string
        with self.assertRaises(BadSignature):
            verify_token("")
        with self.assertRaises(BadSignature):
            verify_token(None)  # type: ignore

        # Malformed non-integer payload in signed token
        signer = get_signer()
        bad_payload_token = signer.sign("non_integer_id")
        with self.assertRaises(BadSignature):
            verify_token(bad_payload_token)

        # Non-existent user ID in signed token
        ghost_user_token = signer.sign("999999")
        with self.assertRaises(User.DoesNotExist):
            verify_token(ghost_user_token)

    def test_verify_email_endpoint_non_existent_user_returns_400(self):
        signer = get_signer()
        ghost_token = signer.sign("888888")
        res = self.client.post(
            reverse("accounts:verify-email"),
            data=json.dumps({"token": ghost_token}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("invalid", res.json()["message"].lower())


class AccountAuthLifecycleAndSessionContractTests(TestCase):
    """Deliverable DoD tests: register, login, logout, me, session contracts (P4-03)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="lifecycle_user",
            email="Lifecycle.User@example.com",
            password="StrongPassword123!",
            role=User.Role.GUEST,
        )

    def test_auth_me_contract_complete_keys(self):
        # Unauthenticated: returns {"data": None}
        res_anon = self.client.get(reverse("accounts:me"))
        self.assertEqual(res_anon.status_code, 200)
        self.assertEqual(res_anon.json(), {"data": None})

        # Authenticated: returns exact contract dictionary
        self.client.force_login(self.user)
        res_auth = self.client.get(reverse("accounts:me"))
        self.assertEqual(res_auth.status_code, 200)
        data = res_auth.json().get("data")
        expected_keys = {"id", "username", "email", "role", "email_verified", "last_login"}
        self.assertEqual(set(data.keys()), expected_keys)
        self.assertEqual(data["username"], "lifecycle_user")
        self.assertEqual(data["email"], "Lifecycle.User@example.com")
        self.assertEqual(data["role"], "guest")
        self.assertFalse(data["email_verified"])

    def test_login_with_case_insensitive_email(self):
        # Login with all-lowercase email when registered with mixed-case
        res = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "lifecycle.user@example.com",
                "password": "StrongPassword123!",
            }),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["username"], "lifecycle_user")

    def test_login_inactive_user_rejected(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        res = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "lifecycle_user",
                "password": "StrongPassword123!",
            }),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["message"], "Invalid credentials.")

    def test_logout_clears_session_and_subsequent_me_is_null(self):
        # 1. Login
        login_res = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({
                "username_or_email": "lifecycle_user",
                "password": "StrongPassword123!",
            }),
            content_type="application/json",
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("_auth_user_id", self.client.session)

        # 2. Logout
        logout_res = self.client.post(reverse("accounts:logout"))
        self.assertEqual(logout_res.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

        # 3. Subsequent /api/auth/me/ returns null
        me_res = self.client.get(reverse("accounts:me"))
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json(), {"data": None})
