from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Guest review and rating for a hotel."""

    hotel = models.ForeignKey(
        "hotels.Hotel",
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="Hotel being reviewed.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="User who wrote this review.",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Review rating from 1 to 5 stars.",
    )
    comment = models.TextField(
        blank=True,
        default="",
        help_text="Optional review comment.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "review"
        verbose_name_plural = "reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "user"],
                name="unique_hotel_user_review",
            ),
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_1_to_5",
            ),
        ]

    def __str__(self):
        return f"Review by {self.user} on {self.hotel} ({self.rating}/5)"
