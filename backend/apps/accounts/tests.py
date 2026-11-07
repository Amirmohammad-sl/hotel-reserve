import json
from django.contrib.admin.sites import site
from django.db import IntegrityError
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from .admin import CustomUserAdmin
from .forms import LoginForm, RegisterForm, user_to_dict
from .models import User


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
        self.assertEqual(
            response.json(),
            {
                "data": {
                    "id": self.user.id,
                    "username": "existingguest",
                    "email": "existing@example.com",
                    "role": "guest",
                    "email_verified": False,
                }
            },
        )

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
