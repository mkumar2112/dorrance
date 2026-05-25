from django.db import models
from django.utils.text import slugify
import uuid
from django.utils import timezone
from Home.models import *
from django.core.exceptions import ValidationError



class Organization(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    logo = models.ImageField(upload_to="organization/logo/", blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=10, blank=True, null=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_organizations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class OrganizationGallery(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="gallery_images"
    )

    image = models.ImageField(upload_to="organization/gallery/")
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.organization.name} Gallery"
    

class OrgAdmin(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="org_admin_roles"
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="admins"
    )

    is_primary = models.BooleanField(default=False)

    can_manage_users = models.BooleanField(default=True)
    can_manage_menu = models.BooleanField(default=True)
    can_manage_orders = models.BooleanField(default=True)
    can_view_reports = models.BooleanField(default=True)
    can_manage_payments = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organization")
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user} - {self.organization}"
    


class FoodCategory(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="food_categories"
    )

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, blank=True)

    image = models.ImageField(upload_to="menu/category/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("organization", "slug")
        ordering = ["sort_order", "id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while FoodCategory.objects.filter(
                organization=self.organization,
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.organization})"
    

class FoodItem(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="food_items"
    )

    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="items"
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)

    image = models.ImageField(upload_to="menu/items/", blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    is_veg = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)

    preparation_time = models.PositiveIntegerField(
        blank=True, null=True, help_text="Time in minutes"
    )

    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    stock_quantity = models.PositiveIntegerField(default=0)
    is_unlimited_stock = models.BooleanField(default=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    sort_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_food_items"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("organization", "slug")
        ordering = ["sort_order", "id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while FoodItem.objects.filter(
                organization=self.organization,
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_final_price(self):
        return self.discounted_price or self.price

    def __str__(self):
        return f"{self.name} ({self.organization})"





class Order(models.Model):
    ORDER_TYPE_CHOICES = (
        ("dine_in", "Dine In"),
        ("takeaway", "Takeaway"),
        ("delivery", "Delivery"),
    )

    ORDER_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("partially_refunded", "Partially Refunded"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="orders"
    )

    order_number = models.CharField(max_length=50, unique=True, blank=True)

    order_type = models.CharField(
        max_length=20,
        choices=ORDER_TYPE_CHOICES,
        default="dine_in"
    )

    status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS_CHOICES,
        default="pending"
    )

    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    points_used = models.PositiveIntegerField(default=0)
    points_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    coupon_code = models.CharField(max_length=50, blank=True, null=True)

    customer_name = models.CharField(max_length=150, blank=True, null=True)
    customer_mobile = models.CharField(max_length=15, blank=True, null=True)

    table_number = models.CharField(max_length=20, blank=True, null=True)
    no_of_people = models.PositiveIntegerField(blank=True, null=True)

    delivery_address = models.TextField(blank=True, null=True)

    special_instruction = models.TextField(blank=True, null=True)
    cancel_reason = models.TextField(blank=True, null=True)

    confirmed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_orders"
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_id = Order.objects.count() + 1
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d')}{last_id:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

    def calculate_total(self):
        self.total_amount = (
            self.subtotal_amount
            + self.tax_amount
            + self.delivery_charge
            - self.discount_amount
            - self.points_discount_amount
        )

        self.payable_amount = max(self.total_amount, 0)
        return self.payable_amount


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="order_items"
    )

    item_name = models.CharField(max_length=200)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.PositiveIntegerField(default=1)

    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    special_instruction = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        self.total_amount = (self.item_price * self.quantity) - self.discount_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"



class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ("cash", "Cash"),
        ("card", "Card"),
        ("upi", "UPI"),
        ("wallet", "Wallet"),
        ("net_banking", "Net Banking"),
        ("razorpay", "Razorpay"),
        ("stripe", "Stripe"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
        ("partially_refunded", "Partially Refunded"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="payments"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="payments"
    )

    payment_number = models.CharField(max_length=50, unique=True, blank=True)

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default="cash"
    )

    gateway_name = models.CharField(max_length=50, blank=True, null=True)

    gateway_order_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_signature = models.TextField(blank=True, null=True)

    transaction_id = models.CharField(max_length=150, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")

    status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    payment_response = models.JSONField(default=dict, blank=True)

    paid_at = models.DateTimeField(blank=True, null=True)

    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)

    failure_reason = models.TextField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_payments"
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = f"PAY{timezone.now().strftime('%Y%m%d%H%M%S')}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.payment_number


class DineInTable(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="dinein_tables"
    )

    table_code = models.CharField(max_length=50)
    table_name = models.CharField(max_length=100, blank=True, null=True)

    capacity = models.PositiveIntegerField(default=1)

    floor = models.CharField(max_length=50, blank=True, null=True)
    section = models.CharField(max_length=50, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        unique_together = ("organization", "table_code")

    def __str__(self):
        return f"{self.table_code} - {self.capacity} people"


class DineInBooking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("no_show", "No Show"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="dinein_bookings"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="dinein_bookings"
    )

    table = models.ForeignKey(
        DineInTable,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="bookings"
    )

    booking_number = models.CharField(max_length=50, unique=True, blank=True)

    booking_date = models.DateField()
    booking_time = models.TimeField()

    no_of_people = models.PositiveIntegerField()

    customer_name = models.CharField(max_length=150)
    customer_mobile = models.CharField(max_length=15)

    special_request = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    confirmed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    cancel_reason = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    is_walk_in = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_bookings"
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def clean(self):
        if self.table:
            if self.organization_id and self.table.organization_id != self.organization_id:
                raise ValidationError(
                    "Selected table does not belong to this organization."
                )

            if self.no_of_people and self.no_of_people > self.table.capacity:
                raise ValidationError(
                    f"This table capacity is only {self.table.capacity} people."
                )

            already_booked = DineInBooking.objects.filter(
                organization_id=self.organization_id,
                table=self.table,
                booking_date=self.booking_date,
                booking_time=self.booking_time,
                status__in=["pending", "confirmed"],
                is_deleted=False,
            )

            if self.pk:
                already_booked = already_booked.exclude(pk=self.pk)

            if already_booked.exists():
                raise ValidationError(
                    "This table is already booked for this date and time."
                )

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.booking_number:
            last_id = DineInBooking.objects.count() + 1
            self.booking_number = f"BOOK{timezone.now().strftime('%Y%m%d')}{last_id:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.booking_number

class RewardPointSetting(models.Model):
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name="reward_setting"
    )

    one_point_value = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    joining_points = models.PositiveIntegerField(default=0)
    referral_points = models.PositiveIntegerField(default=0)

    min_redeem_points = models.PositiveIntegerField(default=0)
    max_redeem_points_per_order = models.PositiveIntegerField(default=0)

    is_points_enabled = models.BooleanField(default=True)
    is_referral_enabled = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reward Setting - {self.organization}"


class PointTransaction(models.Model):
    EARN = "earn"
    REDEEM = "redeem"
    EXPIRE = "expire"
    ADJUST = "adjust"

    TRANSACTION_TYPE_CHOICES = (
        (EARN, "Earn"),
        (REDEEM, "Redeem"),
        (EXPIRE, "Expire"),
        (ADJUST, "Adjust"),
    )

    JOINING = "joining"
    REFERRAL = "referral"
    ORDER = "order"
    ADMIN = "admin"
    BOOKING = "booking"

    SOURCE_CHOICES = (
        (JOINING, "Joining Bonus"),
        (REFERRAL, "Referral"),
        (ORDER, "Order"),
        (ADMIN, "Admin Adjustment"),
        (BOOKING, "Dine In Booking"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="point_transactions"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="point_transactions"
    )

    points = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)

    description = models.TextField(blank=True, null=True)

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="point_transactions"
    )

    booking = models.ForeignKey(
        DineInBooking,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="point_transactions"
    )

    balance_after = models.IntegerField(default=0)

    expiry_date = models.DateField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_point_transactions"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user} - {self.points} - {self.transaction_type}"


class Referral(models.Model):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="referrals"
    )

    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="referrals_made"
    )

    referred_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="referrals_received"
    )

    referral_code = models.CharField(max_length=50)

    points_awarded = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    completed_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "referred_user")
        ordering = ["-id"]

    def __str__(self):
        return f"{self.referrer} referred {self.referred_user}"




class Feedback(models.Model):
    RATING_CHOICES = (
        (1, "1 - Very Poor"),
        (2, "2 - Poor"),
        (3, "3 - Average"),
        (4, "4 - Good"),
        (5, "5 - Excellent"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="feedbacks"
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="feedbacks"
    )

    booking = models.ForeignKey(
        DineInBooking,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="feedbacks"
    )

    customer_name = models.CharField(max_length=150, blank=True, null=True)
    customer_mobile = models.CharField(max_length=15, blank=True, null=True)

    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    food_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, blank=True, null=True)
    service_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, blank=True, null=True)
    ambience_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, blank=True, null=True)

    comment = models.TextField(blank=True, null=True)

    is_public = models.BooleanField(default=False)
    is_reviewed_by_admin = models.BooleanField(default=False)

    admin_reply = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.organization} - {self.rating} Star"
    



class Notification(models.Model):
    TARGET_TYPE_CHOICES = (
        ("all", "All Users"),
        ("single", "Single User"),
        ("organization", "Organization Users"),
    )

    CHANNEL_CHOICES = (
        ("push", "Push Notification"),
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("in_app", "In App"),
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    image = models.ImageField(upload_to="notifications/", blank=True, null=True)

    target_type = models.CharField(
        max_length=20,
        choices=TARGET_TYPE_CHOICES,
        default="all"
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="notifications"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="direct_notifications"
    )

    channels = models.JSONField(default=list, blank=True)

    scheduled_at = models.DateTimeField(blank=True, null=True)

    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_notifications"
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.title


class NotificationLog(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("read", "Read"),
    )

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_logs"
    )

    channel = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)

    sent_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user} - {self.notification.title}"

















