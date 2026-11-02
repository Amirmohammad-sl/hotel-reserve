from django.contrib.admin.sites import site
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .admin import CustomUserAdmin
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
