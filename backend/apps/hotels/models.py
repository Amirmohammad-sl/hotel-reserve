from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Amenity(models.Model):
    """Hotel or room feature/amenity (e.g. wifi, breakfast, parking, pool)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name of the amenity.",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Optional description of the amenity.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "amenity"
        verbose_name_plural = "amenities"

    def __str__(self):
        return self.name


class Hotel(models.Model):
    """Hotel establishment managed by a user with manager role."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hotels",
        help_text="Manager who owns and manages this hotel.",
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the hotel.",
    )
    city = models.CharField(
        max_length=100,
        db_index=True,
        help_text="City where the hotel is located (indexed for search).",
    )
    address = models.TextField(
        help_text="Full street address.",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed description of the hotel.",
    )
    star_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Hotel star rating between 1 and 5 (optional).",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Geographical latitude coordinate.",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Geographical longitude coordinate.",
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="URL of hotel primary display image.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this hotel is active and available for public listing.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "hotel"
        verbose_name_plural = "hotels"
        indexes = [
            models.Index(fields=["city"], name="hotel_city_idx"),
            models.Index(fields=["is_active"], name="hotel_is_active_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(star_rating__gte=1, star_rating__lte=5)
                | models.Q(star_rating__isnull=True),
                name="hotel_star_rating_1_to_5",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.city})"


class RoomType(models.Model):
    """Room category defined within a hotel."""

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="room_types",
        help_text="Hotel to which this room type belongs.",
    )
    title = models.CharField(
        max_length=150,
        help_text="Title or name of room type (e.g. Deluxe Double, Standard Single).",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Description of room features and layout.",
    )
    capacity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum guests count per room (minimum 1).",
    )
    price_per_night = models.PositiveBigIntegerField(
        help_text="Price per night in Toman.",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Total number of physical rooms available for this type (minimum 1).",
    )
    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name="room_types",
        help_text="Amenities available in this room type.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["hotel", "price_per_night"]
        verbose_name = "room type"
        verbose_name_plural = "room types"
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "title"],
                name="unique_hotel_roomtype_title",
            ),
            models.CheckConstraint(
                check=models.Q(capacity__gte=1),
                name="roomtype_capacity_gte_1",
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gte=1),
                name="roomtype_quantity_gte_1",
            ),
        ]

    def __str__(self):
        return f"{self.hotel.name} - {self.title}"
