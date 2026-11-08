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


class HotelQuerySet(models.QuerySet):
    """Custom QuerySet for Hotel queries with reusable business domain logic."""

    def active(self):
        """Filter hotels that are active (is_active=True).

        WHY: Soft-deactivated hotels must be excluded from public search, listings,
        and reservation workflows. Centralising `is_active=True` avoids scattered
        boolean flag checks and accidental leaks of inactive hotels to guests.
        """
        return self.filter(is_active=True)

    def in_city(self, city):
        """Filter hotels located in a specific city (case-insensitive and trimmed).

        WHY: Search queries for cities may contain extra whitespace or mixed casing
        (e.g. ' Tehran ' vs 'tehran'). Stripping whitespace and using `iexact`
        ensures robust matching without repeating string cleanup in view logic.
        """
        if not city:
            return self
        cleaned_city = str(city).strip()
        return self.filter(city__iexact=cleaned_city)

    def owned_by(self, user):
        """Filter hotels owned by a specific manager user.

        WHY: Crucial for multi-tenant manager security. Ensures manager-side views,
        hotel edits, room management, and statistics strictly operate within the
        logged-in manager's boundary, preventing horizontal privilege escalation.
        """
        return self.filter(owner=user)

    def with_min_price(self):
        """Annotate each hotel with `min_price`, the lowest price_per_night among its room types.

        WHY: Hotel search result cards display starting prices ('From X Toman').
        Calculating this using SQL `MIN(room_types.price_per_night)` in a single query
        avoids the classic N+1 query problem of fetching all room types in Python.
        """
        return self.annotate(min_price=models.Min("room_types__price_per_night"))

    def priced_between(self, min_price=None, max_price=None):
        """Filter hotels that have at least one room type within [min_price, max_price].

        WHY: Allows guests to filter hotels based on nightly room budget. Applying both
        minimum and maximum bounds in a single `.filter()` call ensures they match against
        the SAME room type row (avoiding the multi-valued relationship trap in Django ORM).
        """
        filters = {}
        if min_price is not None:
            filters["room_types__price_per_night__gte"] = min_price
        if max_price is not None:
            filters["room_types__price_per_night__lte"] = max_price
        if filters:
            return self.filter(**filters).distinct()
        return self


class Hotel(models.Model):
    """Hotel establishment managed by a user with manager role."""

    objects = HotelQuerySet.as_manager()

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


class RoomTypeQuerySet(models.QuerySet):
    """Custom QuerySet for RoomType providing availability calculations."""

    def with_availability(self, check_in=None, check_out=None):
        """Annotate each RoomType with 'reserved' and 'available_count' for [check_in, check_out).

        WHY: Eliminates N+1 in-memory availability loops in hotel search, detail, and
        booking flows by executing subquery aggregation at the database level.
        Guarantees that same-day turnover (out on 5th, in on 5th) does not reduce inventory (D-006).
        """
        if not check_in or not check_out:
            return self.annotate(
                reserved=models.Value(0, output_field=models.IntegerField()),
                available_count=models.F("quantity"),
            )

        from django.apps import apps

        Booking = apps.get_model("bookings", "Booking")

        overlapping_bookings = (
            Booking.objects.active()
            .overlapping(check_in, check_out)
            .filter(room_type=models.OuterRef("pk"))
            .values("room_type")
            .annotate(total_rooms=models.Sum("rooms_count"))
            .values("total_rooms")
        )

        return self.annotate(
            reserved=models.functions.Coalesce(
                models.Subquery(
                    overlapping_bookings[:1],
                    output_field=models.IntegerField(),
                ),
                models.Value(0, output_field=models.IntegerField()),
            )
        ).annotate(
            available_count=models.functions.Greatest(
                models.F("quantity") - models.F("reserved"),
                models.Value(0, output_field=models.IntegerField()),
                output_field=models.IntegerField(),
            )
        )

    def available_in_range(self, check_in, check_out, rooms_count=1):
        """Filter room types that have at least rooms_count available in the given date range.

        WHY: Convenient chained filter for search queries requiring immediate inventory checks.
        """
        return self.with_availability(check_in, check_out).filter(
            available_count__gte=rooms_count
        )


class RoomType(models.Model):
    """Room category defined within a hotel."""

    objects = RoomTypeQuerySet.as_manager()

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
