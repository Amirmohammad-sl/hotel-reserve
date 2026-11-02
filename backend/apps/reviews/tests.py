import datetime
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.hotels.models import Hotel
from apps.reviews.models import Review

User = get_user_model()


class ReviewModelTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="hotel_manager",
            email="manager@example.com",
            password="passWORD123!",
            role=User.Role.MANAGER,
        )
        self.guest1 = User.objects.create_user(
            username="traveler_one",
            email="guest1@example.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.guest2 = User.objects.create_user(
            username="traveler_two",
            email="guest2@example.com",
            password="passWORD123!",
            role=User.Role.GUEST,
        )
        self.hotel1 = Hotel.objects.create(
            owner=self.manager,
            name="Espinas Palace",
            city="Tehran",
            address="Saadat Abad",
        )
        self.hotel2 = Hotel.objects.create(
            owner=self.manager,
            name="Parsian Azadi",
            city="Tehran",
            address="Chamran Expressway",
        )

    def test_review_creation_valid(self):
        review = Review.objects.create(
            hotel=self.hotel1,
            user=self.guest1,
            rating=5,
            comment="Exceptional service and view!",
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Exceptional service and view!")
        self.assertIn("traveler_one", str(review))
        self.assertIn("Espinas Palace", str(review))
        self.assertIn("5/5", str(review))
        self.assertIsNotNone(review.created_at)
        self.assertIsNotNone(review.updated_at)

        # Check reverse relationships
        self.assertEqual(self.hotel1.reviews.count(), 1)
        self.assertEqual(self.hotel1.reviews.first(), review)
        self.assertEqual(self.guest1.reviews.count(), 1)
        self.assertEqual(self.guest1.reviews.first(), review)

    def test_review_without_comment_is_allowed(self):
        review = Review.objects.create(
            hotel=self.hotel1,
            user=self.guest2,
            rating=4,
        )
        review.full_clean()
        self.assertEqual(review.comment, "")
        self.assertEqual(review.rating, 4)

    def test_unique_hotel_user_constraint(self):
        Review.objects.create(
            hotel=self.hotel1,
            user=self.guest1,
            rating=4,
            comment="First review",
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    hotel=self.hotel1,
                    user=self.guest1,
                    rating=2,
                    comment="Duplicate review on same hotel",
                )

    def test_same_user_can_review_different_hotels(self):
        r1 = Review.objects.create(
            hotel=self.hotel1,
            user=self.guest1,
            rating=5,
            comment="Loved Espinas",
        )
        r2 = Review.objects.create(
            hotel=self.hotel2,
            user=self.guest1,
            rating=4,
            comment="Loved Azadi too",
        )
        self.assertEqual(self.guest1.reviews.count(), 2)
        self.assertIn(r1, self.guest1.reviews.all())
        self.assertIn(r2, self.guest1.reviews.all())

    def test_multiple_users_can_review_same_hotel(self):
        r1 = Review.objects.create(
            hotel=self.hotel1,
            user=self.guest1,
            rating=5,
        )
        r2 = Review.objects.create(
            hotel=self.hotel1,
            user=self.guest2,
            rating=3,
        )
        self.assertEqual(self.hotel1.reviews.count(), 2)
        self.assertIn(r1, self.hotel1.reviews.all())
        self.assertIn(r2, self.hotel1.reviews.all())

    def test_rating_validators_full_clean(self):
        # Rating 0 should fail MinValueValidator(1)
        invalid_low = Review(
            hotel=self.hotel1,
            user=self.guest1,
            rating=0,
        )
        with self.assertRaises(ValidationError) as ctx:
            invalid_low.full_clean()
        self.assertIn("rating", ctx.exception.message_dict)

        # Rating 6 should fail MaxValueValidator(5)
        invalid_high = Review(
            hotel=self.hotel1,
            user=self.guest1,
            rating=6,
        )
        with self.assertRaises(ValidationError) as ctx:
            invalid_high.full_clean()
        self.assertIn("rating", ctx.exception.message_dict)

        # Rating 1 and 5 should pass
        valid_min = Review(hotel=self.hotel1, user=self.guest1, rating=1)
        valid_min.full_clean()

        valid_max = Review(hotel=self.hotel1, user=self.guest2, rating=5)
        valid_max.full_clean()

    def test_rating_check_constraint_db_level(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    hotel=self.hotel1,
                    user=self.guest1,
                    rating=0,
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    hotel=self.hotel1,
                    user=self.guest1,
                    rating=6,
                )

    def test_cascade_delete_hotel(self):
        Review.objects.create(
            hotel=self.hotel1,
            user=self.guest1,
            rating=5,
        )
        self.assertEqual(Review.objects.count(), 1)
        self.hotel1.delete()
        self.assertEqual(Review.objects.count(), 0)

    def test_cascade_delete_user(self):
        Review.objects.create(
            hotel=self.hotel1,
            user=self.guest1,
            rating=5,
        )
        self.assertEqual(Review.objects.count(), 1)
        self.guest1.delete()
        self.assertEqual(Review.objects.count(), 0)

    def test_reviews_default_ordering(self):
        r1 = Review.objects.create(hotel=self.hotel1, user=self.guest1, rating=4)
        Review.objects.filter(id=r1.id).update(
            created_at=timezone.now() - datetime.timedelta(days=1)
        )
        r2 = Review.objects.create(hotel=self.hotel2, user=self.guest2, rating=5)
        reviews = list(Review.objects.all())
        # Ordered by -created_at, -id, so r2 is first
        self.assertEqual(reviews[0], r2)
        self.assertEqual(reviews[1], r1)
