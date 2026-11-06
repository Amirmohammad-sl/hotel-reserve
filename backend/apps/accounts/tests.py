from django.contrib.admin.sites import site
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
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
