from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class DiscountCodeQuerySet(models.QuerySet):
    """Custom QuerySet for DiscountCode providing domain-specific filtering."""

    def valid_now(self, hotel, today=None):
        """Filter discount coupons for a hotel that are active, unexpired, and have remaining redemptions.

        WHY: Encapsulates all temporal and usage constraints (D-004) into a single reusable
        ORM query so views, serializers, and booking services do not duplicate filter criteria.
        """
        if today is None:
            today = timezone.localdate()
        hotel_id = getattr(hotel, "id", hotel)
        return self.filter(
            hotel_id=hotel_id,
            is_active=True,
            valid_from__lte=today,
            valid_to__gte=today,
        ).filter(
            models.Q(max_uses__isnull=True) | models.Q(used_count__lt=models.F("max_uses"))
        )

    def get_valid(self, hotel, code: str, today=None):
        """Retrieve a valid discount code instance matching code for a hotel, or None if invalid/expired.

        WHY: Provides safe, normalized coupon redemption lookup, moving case-insensitive
        and active-validity verification out of views and forms into the model manager layer.
        """
        if not code:
            return None
        normalized_code = str(code).strip().upper()
        return self.valid_now(hotel, today=today).filter(code=normalized_code).first()

    def for_hotel(self, hotel):
        """Filter discount codes belonging to a specific hotel instance or hotel ID.

        WHY: Encapsulates hotel scoping for discount codes across manager and booking views.
        """
        hotel_id = getattr(hotel, "id", hotel)
        return self.filter(hotel_id=hotel_id)

    def owned_by(self, user):
        """Filter discount codes belonging to hotels owned by the specified manager user.

        WHY: Enforces manager-level multi-tenancy and data isolation for coupon management,
        preventing foreign managers from inspecting, altering, or deleting promo codes.
        """
        return self.filter(hotel__owner=user)


class DiscountCodeManager(models.Manager.from_queryset(DiscountCodeQuerySet)):
    """Manager for DiscountCode model exposing DiscountCodeQuerySet methods."""

    pass


class DiscountCode(models.Model):
    """Discount coupon code defined by a hotel manager for a specific hotel."""

    objects = DiscountCodeManager()

    hotel = models.ForeignKey(
        "hotels.Hotel",
        on_delete=models.CASCADE,
        related_name="discount_codes",
        help_text="Hotel offering this discount coupon.",
    )
    code = models.CharField(
        max_length=50,
        help_text="Coupon code (uppercase, unique per hotel).",
    )
    percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Discount percentage between 1 and 100.",
    )
    valid_from = models.DateField(
        help_text="First date the discount code can be used (inclusive).",
    )
    valid_to = models.DateField(
        help_text="Last date the discount code can be used (inclusive).",
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum total allowed redemptions (null for unlimited).",
    )
    used_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this discount code has been redeemed.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this discount code is active.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "discount code"
        verbose_name_plural = "discount codes"
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "code"],
                name="unique_hotel_discount_code",
            ),
            models.CheckConstraint(
                check=models.Q(percent__gte=1, percent__lte=100),
                name="discount_percent_1_to_100",
            ),
            models.CheckConstraint(
                check=models.Q(valid_to__gte=models.F("valid_from")),
                name="discount_valid_to_gte_valid_from",
            ),
            models.CheckConstraint(
                check=models.Q(used_count__gte=0),
                name="discount_used_count_gte_0",
            ),
        ]

    def clean(self):
        super().clean()
        if self.code:
            self.code = self.code.strip().upper()
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValidationError(
                {"valid_to": "valid_to must be greater than or equal to valid_from."}
            )

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} ({self.percent}% - {self.hotel.name})"


class BookingQuerySet(models.QuerySet):
    """Custom QuerySet for Booking providing domain filters for status, overlap, hotel and guest."""

    def active(self):
        """Filter bookings with CONFIRMED status.

        WHY: In our domain model, only confirmed reservations hold room inventory. Cancelled
        bookings free up room units, so active() provides the baseline set for occupancy and billing.
        """
        return self.filter(status=Booking.Status.CONFIRMED)

    def overlapping(self, check_in, check_out):
        """Filter bookings overlapping with the date range [check_in, check_out).

        WHY: Implements the exact interval overlap condition (check_in < req_out AND check_out > req_in)
        mandated by Decision D-006. Ensures that same-day turnover (e.g. guest departs morning of 5th
        and another arrives afternoon of 5th) does not trigger an overlap conflict.
        """
        return self.filter(check_in__lt=check_out, check_out__gt=check_in)

    def for_hotel(self, hotel):
        """Filter bookings belonging to a specific hotel instance or hotel ID.

        WHY: Provides hotel-level tenancy isolation for manager dashboards, availability matrices,
        and reservation listings without writing manual joins across room_type and hotel.
        """
        hotel_id = getattr(hotel, "id", hotel)
        return self.filter(room_type__hotel_id=hotel_id)

    def for_guest(self, user):
        """Filter bookings made by a specific guest user instance or user ID.

        WHY: Encapsulates ownership checks for guest booking management ('my bookings'), ensuring
        guests can never inspect or alter reservations belonging to other users.
        """
        user_id = getattr(user, "id", user)
        return self.filter(guest_id=user_id)


class Booking(models.Model):
    """Guest reservation for rooms of a specific RoomType in a date range."""

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    objects = BookingQuerySet.as_manager()

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bookings",
        help_text="Guest user who booked the room(s).",
    )
    room_type = models.ForeignKey(
        "hotels.RoomType",
        on_delete=models.PROTECT,
        related_name="bookings",
        help_text="Room type reserved in this booking.",
    )
    check_in = models.DateField(
        help_text="Check-in arrival date.",
    )
    check_out = models.DateField(
        help_text="Check-out departure date (exclusive).",
    )
    rooms_count = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of physical rooms reserved (minimum 1).",
    )
    guests_count = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Total number of staying guests (minimum 1).",
    )
    nights = models.PositiveSmallIntegerField(
        help_text="Calculated number of nights (check_out - check_in).",
    )
    price_per_night_snapshot = models.PositiveBigIntegerField(
        help_text="Snapshot of room price per night in Toman at reservation time.",
    )
    subtotal = models.PositiveBigIntegerField(
        help_text="Base total price before discount in Toman.",
    )
    discount_code = models.ForeignKey(
        DiscountCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
        help_text="Optional discount code applied to this booking.",
    )
    discount_amount = models.PositiveBigIntegerField(
        default=0,
        help_text="Total discount deducted in Toman.",
    )
    total_price = models.PositiveBigIntegerField(
        help_text="Final payable price in Toman (subtotal - discount_amount).",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
        help_text="Current booking status.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when booking was cancelled.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "booking"
        verbose_name_plural = "bookings"
        indexes = [
            models.Index(
                fields=["room_type", "check_in", "check_out"],
                name="booking_rt_dates_idx",
            ),
            models.Index(
                fields=["guest", "status"],
                name="booking_guest_status_idx",
            ),
            models.Index(
                fields=["status"],
                name="booking_status_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F("check_in")),
                name="booking_check_out_gt_check_in",
            ),
            models.CheckConstraint(
                check=models.Q(rooms_count__gte=1),
                name="booking_rooms_count_gte_1",
            ),
            models.CheckConstraint(
                check=models.Q(guests_count__gte=1),
                name="booking_guests_count_gte_1",
            ),
            models.CheckConstraint(
                check=models.Q(nights__gte=1),
                name="booking_nights_gte_1",
            ),
        ]

    def calculate_nights(self) -> int:
        """Pure helper returning the number of nights between check_in and check_out.

        Does not perform any database queries.
        """
        if self.check_in and self.check_out and self.check_out > self.check_in:
            return (self.check_out - self.check_in).days
        return 0

    def clean(self):
        super().clean()
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValidationError(
                {"check_out": "Check-out date must be strictly after check-in date."}
            )

    def save(self, *args, **kwargs):
        if not self.nights:
            self.nights = self.calculate_nights()
        super().save(*args, **kwargs)

    def __str__(self):
        guest_name = getattr(self.guest, "username", str(self.guest_id))
        room_title = getattr(self.room_type, "title", str(self.room_type_id))
        return f"Booking #{self.pk or 'new'} - {room_title} ({guest_name})"
