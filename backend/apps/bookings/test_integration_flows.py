"""
End-to-end API integration test flows for Hotel Reserve.

P4-05: Tests: API integration + frontend smoke
Covers:
- GuestJourneyApiIntegrationTests: Full guest lifecycle from anonymous search,
  recently viewed tracking, registration, email verification, login, live quote,
  discount validation, booking creation, availability reduction, booking review,
  cancellation, inventory restoration, and logout.
- ManagerJourneyApiIntegrationTests: Full manager lifecycle from registration,
  email verification, login, hotel CRUD, room type CRUD, discount CRUD,
  monitoring incoming bookings, availability calendar matrix, and multi-tenant
  isolation / cross-role security boundaries.
- EdgeCasesApiIntegrationTests: Unverified booking prevention, date ordering,
  capacity conflict (409), and cross-guest cancellation security.
"""

import datetime
import json
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.bookings.models import Booking, DiscountCode
from apps.hotels.models import Amenity, Hotel, RoomType

User = get_user_model()


class GuestJourneyApiIntegrationTests(TestCase):
    """
    Comprehensive end-to-end integration test of the entire Guest persona story:
    1. Anonymous browsing & city discovery
    2. Hotel search with date/guest filters
    3. Hotel details inspection & recently viewed session tracking
    4. Room availability inspection
    5. Guest account registration
    6. Email verification link/token activation
    7. Authentication (login / session persistence / me)
    8. Coupon code validation
    9. Real-time booking price quote
    10. Booking submission & inventory reservation
    11. Guest booking history inspection
    12. Booking cancellation & inventory restoration
    13. Session teardown (logout)
    """

    def setUp(self):
        self.manager = User.objects.create_user(
            username="isfahan_host",
            email="host@abbasihotel.ir",
            password="ManagerP@ssw0rd123!",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.wifi = Amenity.objects.create(name="وای‌فای رایگان", description="اینترنت پرسرعت در سراسر هتل")
        self.pool = Amenity.objects.create(name="استخر سرپوشیده", description="استخر و سونا")

        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="هتل بین‌المللی عباسی",
            city="اصفهان",
            address="چهارباغ عباسی، خیابان آمادگاه",
            description="یکی از کهن‌ترین مهمان‌سراهای جهان در قلب نصف جهان",
            is_active=True,
        )

        self.room_deluxe = RoomType.objects.create(
            hotel=self.hotel,
            title="اتاق دبل سنتی قاجار",
            capacity=2,
            price_per_night=3_000_000,
            quantity=2,
        )
        self.room_deluxe.amenities.add(self.wifi, self.pool)

        today = timezone.localdate()
        self.valid_coupon = DiscountCode.objects.create(
            hotel=self.hotel,
            code="ESFAHAN25",
            percent=25,
            valid_from=today - datetime.timedelta(days=2),
            valid_to=today + datetime.timedelta(days=20),
            max_uses=5,
            used_count=0,
            is_active=True,
        )

        self.client = Client()

    def test_complete_guest_journey_e2e(self):
        # 1. Anonymous browsing: CSRF + Available cities
        csrf_res = self.client.get(reverse("accounts:csrf"))
        self.assertEqual(csrf_res.status_code, 200)
        self.assertIn("csrftoken", self.client.cookies)

        cities_res = self.client.get(reverse("hotels:cities_list"))
        self.assertEqual(cities_res.status_code, 200)
        cities_data = cities_res.json()["data"]
        self.assertIn("اصفهان", cities_data)

        # 2. Public hotel search with filters
        today = timezone.localdate()
        in_date = today + datetime.timedelta(days=5)
        out_date = today + datetime.timedelta(days=8)  # 3 nights

        search_url = (
            f"{reverse('hotels:hotels_list')}?city=اصفهان"
            f"&check_in={in_date.isoformat()}&check_out={out_date.isoformat()}&guests=2"
        )
        search_res = self.client.get(search_url)
        self.assertEqual(search_res.status_code, 200)
        search_data = search_res.json()["data"]
        self.assertTrue(len(search_data) >= 1)
        self.assertEqual(search_data[0]["id"], self.hotel.id)
        self.assertEqual(search_data[0]["min_price"], 3_000_000)
        self.assertTrue(search_data[0]["available"])
        self.assertIn("last_city", self.client.cookies)

        # 3. Hotel detail & recently viewed tracking
        detail_url = reverse("hotels:hotel_detail", kwargs={"hotel_id": self.hotel.id})
        detail_res = self.client.get(detail_url)
        self.assertEqual(detail_res.status_code, 200)
        detail_data = detail_res.json()["data"]
        self.assertEqual(detail_data["name"], "هتل بین‌المللی عباسی")
        self.assertEqual(len(detail_data["room_types"]), 1)

        recent_res = self.client.get(reverse("hotels:recent_hotels"))
        self.assertEqual(recent_res.status_code, 200)
        recent_data = recent_res.json()["data"]
        self.assertEqual(len(recent_data), 1)
        self.assertEqual(recent_data[0]["id"], self.hotel.id)

        # 4. Rooms list with live availability counts
        rooms_url = (
            f"{reverse('hotels:hotel_rooms', kwargs={'hotel_id': self.hotel.id})}"
            f"?check_in={in_date.isoformat()}&check_out={out_date.isoformat()}&guests=2"
        )
        rooms_res = self.client.get(rooms_url)
        self.assertEqual(rooms_res.status_code, 200)
        rooms_data = rooms_res.json()["data"]
        self.assertEqual(len(rooms_data), 1)
        self.assertEqual(rooms_data[0]["id"], self.room_deluxe.id)
        self.assertEqual(rooms_data[0]["available_count"], 2)

        # 5. Guest registration flow
        mail.outbox.clear()
        reg_payload = {
            "username": "sina_traveler",
            "email": "sina@example.com",
            "password": "SecureP@ssw0rd987!",
            "password2": "SecureP@ssw0rd987!",
            "role": "guest",
            "phone": "09129998877",
        }
        reg_res = self.client.post(
            reverse("accounts:register"),
            data=json.dumps(reg_payload),
            content_type="application/json",
        )
        self.assertEqual(reg_res.status_code, 201)
        user_data = reg_res.json()["data"]
        self.assertEqual(user_data["username"], "sina_traveler")
        self.assertFalse(user_data["email_verified"])

        # Verification email dispatched
        self.assertEqual(len(mail.outbox), 1)
        verify_email = mail.outbox[0]
        self.assertIn("token=", verify_email.body)
        token = verify_email.body.split("token=")[1].split()[0]

        # 6. Email verification activation
        verify_res = self.client.post(
            reverse("accounts:verify-email"),
            data=json.dumps({"token": token}),
            content_type="application/json",
        )
        self.assertEqual(verify_res.status_code, 200)
        self.assertTrue(verify_res.json()["data"]["email_verified"])

        # 7. Login and session verification
        login_res = self.client.post(
            reverse("accounts:login"),
            data=json.dumps({"username_or_email": "sina_traveler", "password": "SecureP@ssw0rd987!"}),
            content_type="application/json",
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.json()["data"]["role"], "guest")

        me_res = self.client.get(reverse("accounts:me"))
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["data"]["username"], "sina_traveler")
        self.assertTrue(me_res.json()["data"]["email_verified"])

        # 8. Coupon code validation
        val_res = self.client.post(
            reverse("bookings:discount-validate"),
            data=json.dumps({"hotel": self.hotel.id, "code": "ESFAHAN25"}),
            content_type="application/json",
        )
        self.assertEqual(val_res.status_code, 200)
        val_data = val_res.json()["data"]
        self.assertTrue(val_data["valid"])
        self.assertEqual(val_data["percent"], 25)

        # 9. Real-time booking price quote
        # 3 nights * 3,000,000 * 1 room = 9,000,000; 25% discount = 2,250,000; total = 6,750,000
        quote_payload = {
            "room_type": self.room_deluxe.id,
            "check_in": in_date.isoformat(),
            "check_out": out_date.isoformat(),
            "rooms_count": 1,
            "guests_count": 2,
            "discount_code": "ESFAHAN25",
        }
        quote_res = self.client.post(
            reverse("bookings:quote"),
            data=json.dumps(quote_payload),
            content_type="application/json",
        )
        self.assertEqual(quote_res.status_code, 200)
        quote_data = quote_res.json()["data"]
        self.assertEqual(quote_data["nights"], 3)
        self.assertEqual(quote_data["subtotal"], 9_000_000)
        self.assertEqual(quote_data["discount_amount"], 2_250_000)
        self.assertEqual(quote_data["total_price"], 6_750_000)
        self.assertTrue(quote_data["available"])

        # 10. Booking submission
        book_res = self.client.post(
            reverse("bookings:booking-create"),
            data=json.dumps(quote_payload),
            content_type="application/json",
        )
        self.assertEqual(book_res.status_code, 201)
        booking_data = book_res.json()["data"]
        booking_id = booking_data["id"]
        self.assertEqual(booking_data["status"], "confirmed")
        self.assertEqual(booking_data["total_price"], 6_750_000)

        # Check inventory is atomically decremented: 2 total - 1 booked = 1 left
        rooms_recheck = self.client.get(rooms_url)
        self.assertEqual(rooms_recheck.status_code, 200)
        self.assertEqual(rooms_recheck.json()["data"][0]["available_count"], 1)

        # Discount code redemptions incremented
        self.valid_coupon.refresh_from_db()
        self.assertEqual(self.valid_coupon.used_count, 1)

        # 11. My bookings list
        mine_res = self.client.get(reverse("bookings:bookings-mine"))
        self.assertEqual(mine_res.status_code, 200)
        mine_data = mine_res.json()["data"]
        self.assertEqual(len(mine_data), 1)
        self.assertEqual(mine_data[0]["id"], booking_id)
        self.assertEqual(mine_data[0]["room_type"]["hotel"]["name"], "هتل بین‌المللی عباسی")

        # 12. Booking cancellation and inventory/coupon restoration
        cancel_url = reverse("bookings:booking-cancel", kwargs={"booking_id": booking_id})
        cancel_res = self.client.post(cancel_url)
        self.assertEqual(cancel_res.status_code, 200)
        self.assertEqual(cancel_res.json()["data"]["status"], "cancelled")

        # Inventory restored back to 2
        rooms_after_cancel = self.client.get(rooms_url)
        self.assertEqual(rooms_after_cancel.json()["data"][0]["available_count"], 2)

        # Coupon used_count restored back to 0
        self.valid_coupon.refresh_from_db()
        self.assertEqual(self.valid_coupon.used_count, 0)

        # 13. Logout
        logout_res = self.client.post(reverse("accounts:logout"))
        self.assertEqual(logout_res.status_code, 200)
        me_after_logout = self.client.get(reverse("accounts:me"))
        self.assertIsNone(me_after_logout.json()["data"])


class ManagerJourneyApiIntegrationTests(TestCase):
    """
    Comprehensive end-to-end integration test of the entire Hotel Manager story:
    1. Manager registration, email verification, login
    2. Hotel creation
    3. Hotel retrieval, inspection, and update
    4. Room type creation with amenities and updates
    5. Discount code creation and updates
    6. Receiving guest bookings and inspecting booking list with status filters
    7. Querying availability matrix across date ranges
    8. Multi-tenant isolation: Manager B cannot inspect or mutate Manager A's entities
    9. Cross-role boundary enforcement: Guests cannot access manager endpoints,
       and managers cannot submit room reservations.
    """

    def setUp(self):
        self.client_mgr = Client()
        self.client_other_mgr = Client()
        self.client_guest = Client()

        self.wifi = Amenity.objects.create(name="وای‌فای پرسرعت", description="وای‌فای رایگان")
        self.gym = Amenity.objects.create(name="باشگاه بدنسازی", description="تجهیزات ورزشی مدرن")
        self.breakfast = Amenity.objects.create(name="صبحانه بوفه", description="بوفه گرم و سرد")

    def test_complete_manager_journey_and_isolation_e2e(self):
        # 1. Manager registration, verification, login
        mail.outbox.clear()
        reg_payload = {
            "username": "shiraz_manager",
            "email": "manager@zandiyeh.ir",
            "password": "ManagerP@ssw0rd456!",
            "password2": "ManagerP@ssw0rd456!",
            "role": "manager",
            "phone": "09171112233",
        }
        reg_res = self.client_mgr.post(
            reverse("accounts:register"),
            data=json.dumps(reg_payload),
            content_type="application/json",
        )
        self.assertEqual(reg_res.status_code, 201)

        token = mail.outbox[0].body.split("token=")[1].split()[0]
        self.client_mgr.post(
            reverse("accounts:verify-email"),
            data=json.dumps({"token": token}),
            content_type="application/json",
        )

        login_res = self.client_mgr.post(
            reverse("accounts:login"),
            data=json.dumps({"username_or_email": "shiraz_manager", "password": "ManagerP@ssw0rd456!"}),
            content_type="application/json",
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.json()["data"]["role"], "manager")

        # 2. Amenities catalog query
        amenities_res = self.client_mgr.get(reverse("hotels:amenities_list"))
        self.assertEqual(amenities_res.status_code, 200)
        self.assertEqual(len(amenities_res.json()["data"]), 3)

        # 3. Hotel creation & listing
        hotel_payload = {
            "name": "هتل سنتی زندیه شیراز",
            "city": "شیراز",
            "address": "بلوار کریم‌خان زند، خیابان رودکی",
            "description": "هتلی اصیل با معماری سنتی زندیه",
            "is_active": True,
        }
        create_hotel_res = self.client_mgr.post(
            reverse("hotels:manager_hotels_list_create"),
            data=json.dumps(hotel_payload),
            content_type="application/json",
        )
        self.assertEqual(create_hotel_res.status_code, 201)
        hotel_data = create_hotel_res.json()["data"]
        hotel_id = hotel_data["id"]
        self.assertEqual(hotel_data["name"], "هتل سنتی زندیه شیراز")

        mgr_hotels_res = self.client_mgr.get(reverse("hotels:manager_hotels_list_create"))
        self.assertEqual(mgr_hotels_res.status_code, 200)
        self.assertEqual(len(mgr_hotels_res.json()["data"]), 1)

        # Update hotel
        update_hotel_res = self.client_mgr.put(
            reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": hotel_id}),
            data=json.dumps({
                "name": "هتل بزرگ سنتی زندیه شیراز",
                "city": "شیراز",
                "address": "بلوار کریم‌خان زند",
                "description": "توضیحات به‌روزشده",
                "is_active": True,
            }),
            content_type="application/json",
        )
        self.assertEqual(update_hotel_res.status_code, 200)
        self.assertEqual(update_hotel_res.json()["data"]["name"], "هتل بزرگ سنتی زندیه شیراز")

        # 4. Room type creation & update
        room_payload = {
            "title": "سوییت سلطنتی زند",
            "capacity": 3,
            "price_per_night": 4_500_000,
            "quantity": 3,
            "amenities": [self.wifi.id, self.gym.id],
        }
        create_room_res = self.client_mgr.post(
            reverse("hotels:manager_room_types_list_create", kwargs={"hotel_id": hotel_id}),
            data=json.dumps(room_payload),
            content_type="application/json",
        )
        self.assertEqual(create_room_res.status_code, 201)
        room_data = create_room_res.json()["data"]
        room_id = room_data["id"]
        self.assertEqual(room_data["quantity"], 3)
        self.assertEqual(len(room_data["amenities"]), 2)

        # Update room price, capacity, and amenities
        update_room_res = self.client_mgr.put(
            reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": room_id}),
            data=json.dumps({
                "title": "سوییت سلطنتی زند (ویژه)",
                "capacity": 4,
                "price_per_night": 5_000_000,
                "quantity": 3,
                "amenities": [self.wifi.id, self.breakfast.id],
            }),
            content_type="application/json",
        )
        self.assertEqual(update_room_res.status_code, 200)
        self.assertEqual(update_room_res.json()["data"]["price_per_night"], 5_000_000)

        # 5. Discount code creation & update
        today = timezone.localdate()
        discount_payload = {
            "code": "SHIRAZ20",
            "percent": 20,
            "valid_from": (today - datetime.timedelta(days=1)).isoformat(),
            "valid_to": (today + datetime.timedelta(days=30)).isoformat(),
            "max_uses": 10,
            "is_active": True,
        }
        create_disc_res = self.client_mgr.post(
            reverse("bookings:manager_hotel_discounts", kwargs={"hotel_id": hotel_id}),
            data=json.dumps(discount_payload),
            content_type="application/json",
        )
        self.assertEqual(create_disc_res.status_code, 201)
        disc_data = create_disc_res.json()["data"]
        discount_id = disc_data["id"]

        list_disc_res = self.client_mgr.get(
            reverse("bookings:manager_hotel_discounts", kwargs={"hotel_id": hotel_id})
        )
        self.assertEqual(list_disc_res.status_code, 200)
        self.assertEqual(len(list_disc_res.json()["data"]), 1)

        # 6. Guest makes a booking; manager reviews bookings & filters
        guest_user = User.objects.create_user(
            username="traveler_maryam",
            email="maryam@example.com",
            password="GuestP@ssw0rd123!",
            role=User.Role.GUEST,
            email_verified=True,
        )
        self.client_guest.force_login(guest_user)

        in_date = today + datetime.timedelta(days=10)
        out_date = today + datetime.timedelta(days=13)  # 3 nights

        booking_res = self.client_guest.post(
            reverse("bookings:booking-create"),
            data=json.dumps({
                "room_type": room_id,
                "check_in": in_date.isoformat(),
                "check_out": out_date.isoformat(),
                "rooms_count": 1,
                "guests_count": 2,
                "discount_code": "SHIRAZ20",
            }),
            content_type="application/json",
        )
        self.assertEqual(booking_res.status_code, 201)
        created_booking_id = booking_res.json()["data"]["id"]

        # Manager inspects hotel bookings
        mgr_bookings_res = self.client_mgr.get(
            reverse("bookings:manager_hotel_bookings", kwargs={"hotel_id": hotel_id})
        )
        self.assertEqual(mgr_bookings_res.status_code, 200)
        mgr_bookings = mgr_bookings_res.json()["data"]
        self.assertEqual(len(mgr_bookings), 1)
        self.assertEqual(mgr_bookings[0]["id"], created_booking_id)
        self.assertEqual(mgr_bookings[0]["guest"]["username"], "traveler_maryam")

        # Status filter check
        confirmed_filter_res = self.client_mgr.get(
            f"{reverse('bookings:manager_hotel_bookings', kwargs={'hotel_id': hotel_id})}?status=confirmed"
        )
        self.assertEqual(len(confirmed_filter_res.json()["data"]), 1)

        cancelled_filter_res = self.client_mgr.get(
            f"{reverse('bookings:manager_hotel_bookings', kwargs={'hotel_id': hotel_id})}?status=cancelled"
        )
        self.assertEqual(len(cancelled_filter_res.json()["data"]), 0)

        # 7. Manager availability calendar matrix
        avail_url = (
            f"{reverse('bookings:manager_hotel_availability', kwargs={'hotel_id': hotel_id})}"
            f"?date_from={in_date.isoformat()}&date_to={out_date.isoformat()}"
        )
        avail_res = self.client_mgr.get(avail_url)
        self.assertEqual(avail_res.status_code, 200)
        avail_data = avail_res.json()["data"]
        self.assertEqual(len(avail_data), 1)
        self.assertEqual(avail_data[0]["room_type_id"], room_id)

        days = avail_data[0]["daily_availability"]
        self.assertEqual(len(days), 3)  # in_date, in_date+1, in_date+2
        for day in days:
            self.assertEqual(day["total"], 3)
            self.assertEqual(day["reserved"], 1)
            self.assertEqual(day["free"], 2)

        # 8. Multi-tenant isolation: Manager 2 cannot touch Manager 1's resources
        other_mgr = User.objects.create_user(
            username="other_manager",
            email="other@hotel.ir",
            password="OtherManagerP@ss123!",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.client_other_mgr.force_login(other_mgr)

        self.assertEqual(
            self.client_other_mgr.get(reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": hotel_id})).status_code,
            404,
        )
        self.assertEqual(
            self.client_other_mgr.put(
                reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": hotel_id}),
                data=json.dumps({"name": "Hacked Hotel"}),
                content_type="application/json",
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client_other_mgr.delete(
                reverse("hotels:manager_hotel_detail", kwargs={"hotel_id": hotel_id})
            ).status_code,
            404,
        )

        self.assertEqual(
            self.client_other_mgr.put(
                reverse("hotels:manager_room_type_detail", kwargs={"room_type_id": room_id}),
                data=json.dumps({"title": "Hacked Room"}),
                content_type="application/json",
            ).status_code,
            404,
        )

        self.assertEqual(
            self.client_other_mgr.get(
                reverse("bookings:manager_hotel_bookings", kwargs={"hotel_id": hotel_id})
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client_other_mgr.get(avail_url).status_code,
            404,
        )

        self.assertEqual(
            self.client_other_mgr.put(
                reverse("bookings:manager_discount_detail", kwargs={"discount_id": discount_id}),
                data=json.dumps({"code": "HACKED"}),
                content_type="application/json",
            ).status_code,
            404,
        )

        # 9. Role boundary enforcement
        self.assertEqual(
            self.client_guest.get(reverse("hotels:manager_hotels_list_create")).status_code,
            403,
        )
        self.assertEqual(
            self.client_guest.post(
                reverse("hotels:manager_hotels_list_create"),
                data=json.dumps(hotel_payload),
                content_type="application/json",
            ).status_code,
            403,
        )

        mgr_booking_attempt = self.client_mgr.post(
            reverse("bookings:booking-create"),
            data=json.dumps({
                "room_type": room_id,
                "check_in": in_date.isoformat(),
                "check_out": out_date.isoformat(),
                "rooms_count": 1,
                "guests_count": 2,
            }),
            content_type="application/json",
        )
        self.assertEqual(mgr_booking_attempt.status_code, 403)


class EdgeCasesApiIntegrationTests(TestCase):
    """
    Validates boundary conditions and security invariants across the API surface:
    - Unverified guests blocked from booking (403)
    - Full capacity exhaustion produces 409 Conflict
    - Guests cannot cancel another guest's reservation (404 / IDOR isolation)
    - Chronological date validation (check_in >= check_out or past dates -> 400)
    """

    def setUp(self):
        self.manager = User.objects.create_user(
            username="boundary_mgr",
            email="mgr@boundary.ir",
            password="P@ssword123!",
            role=User.Role.MANAGER,
            email_verified=True,
        )
        self.hotel = Hotel.objects.create(
            owner=self.manager,
            name="هتل مرزی کیش",
            city="کیش",
            address="میدان پردیس",
            is_active=True,
        )
        self.room = RoomType.objects.create(
            hotel=self.hotel,
            title="اتاق تک‌نفره استاندارد",
            capacity=1,
            price_per_night=1_000_000,
            quantity=1,  # Only 1 room available
        )

        self.guest_a = User.objects.create_user(
            username="guest_alpha",
            email="alpha@example.com",
            password="P@ssword123!",
            role=User.Role.GUEST,
            email_verified=True,
        )
        self.guest_b = User.objects.create_user(
            username="guest_beta",
            email="beta@example.com",
            password="P@ssword123!",
            role=User.Role.GUEST,
            email_verified=True,
        )
        self.unverified_guest = User.objects.create_user(
            username="guest_unverified",
            email="unverified@example.com",
            password="P@ssword123!",
            role=User.Role.GUEST,
            email_verified=False,
        )

        self.client_a = Client()
        self.client_a.force_login(self.guest_a)

        self.client_b = Client()
        self.client_b.force_login(self.guest_b)

        self.client_unverified = Client()
        self.client_unverified.force_login(self.unverified_guest)

    def test_unverified_guest_cannot_book(self):
        today = timezone.localdate()
        res = self.client_unverified.post(
            reverse("bookings:booking-create"),
            data=json.dumps({
                "room_type": self.room.id,
                "check_in": (today + datetime.timedelta(days=2)).isoformat(),
                "check_out": (today + datetime.timedelta(days=4)).isoformat(),
                "rooms_count": 1,
                "guests_count": 1,
            }),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("verify your email", res.json()["message"].lower())

    def test_capacity_exhaustion_returns_409_conflict(self):
        today = timezone.localdate()
        in_date = today + datetime.timedelta(days=6)
        out_date = today + datetime.timedelta(days=8)

        # Guest A reserves the only room
        res_a = self.client_a.post(
            reverse("bookings:booking-create"),
            data=json.dumps({
                "room_type": self.room.id,
                "check_in": in_date.isoformat(),
                "check_out": out_date.isoformat(),
                "rooms_count": 1,
                "guests_count": 1,
            }),
            content_type="application/json",
        )
        self.assertEqual(res_a.status_code, 201)

        # Guest B attempts to book the same room and interval -> 409 Conflict
        res_b = self.client_b.post(
            reverse("bookings:booking-create"),
            data=json.dumps({
                "room_type": self.room.id,
                "check_in": in_date.isoformat(),
                "check_out": out_date.isoformat(),
                "rooms_count": 1,
                "guests_count": 1,
            }),
            content_type="application/json",
        )
        self.assertEqual(res_b.status_code, 409)
        self.assertIn("not available for the selected dates", res_b.json()["message"].lower())

    def test_cross_guest_cancellation_forbidden(self):
        today = timezone.localdate()
        in_date = today + datetime.timedelta(days=15)
        out_date = today + datetime.timedelta(days=17)

        res_a = self.client_a.post(
            reverse("bookings:booking-create"),
            data=json.dumps({
                "room_type": self.room.id,
                "check_in": in_date.isoformat(),
                "check_out": out_date.isoformat(),
                "rooms_count": 1,
                "guests_count": 1,
            }),
            content_type="application/json",
        )
        self.assertEqual(res_a.status_code, 201)
        booking_id = res_a.json()["data"]["id"]

        # Guest B attempts to cancel Guest A's booking -> 404 Not Found (IDOR defense)
        cancel_res = self.client_b.post(
            reverse("bookings:booking-cancel", kwargs={"booking_id": booking_id})
        )
        self.assertEqual(cancel_res.status_code, 404)
        self.assertEqual(
            Booking.objects.get(id=booking_id).status,
            Booking.Status.CONFIRMED,
        )

    def test_invalid_date_validation_rejected_with_400(self):
        today = timezone.localdate()
        # check_in in the past
        res_past = self.client_a.post(
            reverse("bookings:booking-create"),
            data=json.dumps({
                "room_type": self.room.id,
                "check_in": (today - datetime.timedelta(days=1)).isoformat(),
                "check_out": (today + datetime.timedelta(days=2)).isoformat(),
                "rooms_count": 1,
                "guests_count": 1,
            }),
            content_type="application/json",
        )
        self.assertEqual(res_past.status_code, 400)

        # check_out <= check_in
        res_order = self.client_a.post(
            reverse("bookings:booking-create"),
            data=json.dumps({
                "room_type": self.room.id,
                "check_in": (today + datetime.timedelta(days=5)).isoformat(),
                "check_out": (today + datetime.timedelta(days=3)).isoformat(),
                "rooms_count": 1,
                "guests_count": 1,
            }),
            content_type="application/json",
        )
        self.assertEqual(res_order.status_code, 400)
