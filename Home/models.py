from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from django.utils.text import slugify
from .managers import UserManager


PERMISSION_CHOICES = (
    ("dashboard_view", "Dashboard View", "Can view dashboard"),

    ("food_category_view", "Food Category View", "Can view food categories"),
    ("food_category_create", "Food Category Create", "Can create food categories"),
    ("food_category_update", "Food Category Update", "Can update food categories"),
    ("food_category_delete", "Food Category Delete", "Can delete food categories"),

    ("food_item_view", "Food Item View", "Can view food items"),
    ("food_item_create", "Food Item Create", "Can create food items"),
    ("food_item_update", "Food Item Update", "Can update food items"),
    ("food_item_delete", "Food Item Delete", "Can delete food items"),

    ("orders", "Orders", "Can view orders"),
    ("order_create", "Order Create", "Can create orders"),
    ("order_update", "Order Update", "Can update orders"),
    ("order_delete", "Order Delete", "Can delete orders"),

    ("feedbacks_view", "Feedbacks View", "Can view feedbacks"),
    ("feedbacks_create", "Feedbacks Create", "Can create feedbacks"),
    ("feedbacks_update", "Feedbacks Update", "Can update feedbacks"),
    ("feedbacks_delete", "Feedbacks Delete", "Can delete feedbacks"),

    ("discount_view", "Discount View", "Can view discounts"),
    ("discount_create", "Discount Create", "Can create discounts"),
    ("discount_update", "Discount Update", "Can update discounts"),
    ("discount_delete", "Discount Delete", "Can delete discounts"),

    ("booking_view", "Booking View", "Can view dine-in bookings"),
    ("booking_update", "Booking Update", "Can approve/reject dine-in bookings"),

    ("report_view", "Report View", "Can view reports"),

    ("notification_send", "Notification Send", "Can send notifications"),

    ("payment_gateway_view", "Payment Gateway View", "Can view payment gateway"),
    ("payment_gateway_update", "Payment Gateway Update", "Can update payment gateway"),
)


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    display_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    permissions = models.JSONField(default=list, blank=True)

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Role.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        if not self.display_name:
            self.display_name = self.name

        super().save(*args, **kwargs)

    def has_permission(self, permission_slug):
        if not permission_slug:
            return False

        return permission_slug in (self.permissions or [])

    def __str__(self):
        return self.display_name or self.name
     


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)

    role = models.ForeignKey(
        "Role",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users"
    )


    is_mobile_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    otp_code = models.CharField(max_length=10, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.PositiveIntegerField(default=0)

    login_type = models.CharField(
        max_length=30,
        choices=(
            ("mobile", "Mobile"),
            ("email", "Email"),
            ("google", "Google"),
            ("apple", "Apple"),
        ),
        default="mobile"
    )

    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_device = models.CharField(max_length=255, blank=True, null=True)

    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    blocked_at = models.DateTimeField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.mobile_number
    
    objects = UserManager()


    def save(self, *args, **kwargs):
        if self.mobile_number:
            self.username = self.mobile_number
        super().save(*args, **kwargs)


    def has_role_permission(self, permission_slug):
        if self.is_superuser:
            return True

        if not self.role:
            return False

        return self.role.has_permission(permission_slug)

    def block_user(self, reason=None):
        self.is_blocked = True
        self.blocked_reason = reason
        self.blocked_at = timezone.now()
        self.save(update_fields=["is_blocked", "blocked_reason", "blocked_at"])

    def unblock_user(self):
        self.is_blocked = False
        self.blocked_reason = None
        self.blocked_at = None
        self.save(update_fields=["is_blocked", "blocked_reason", "blocked_at"])


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    full_name = models.CharField(max_length=150, blank=True, null=True)
    profile_image = models.ImageField(upload_to="users/profile/", blank=True, null=True)

    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    anniversary_date = models.DateField(blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    landmark = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=10, blank=True, null=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="referred_users"
    )

    total_points = models.PositiveIntegerField(default=0)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    preferred_language = models.CharField(max_length=20, default="en")

    notification_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    whatsapp_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)

    device_token = models.TextField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    is_profile_completed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.full_name or self.user.mobile_number
    









    