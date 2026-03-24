import uuid
from django.db import models
from django.utils import timezone


class TasterBoxOrder(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    shipping_address = models.JSONField()
    country = models.CharField(max_length=100)
    is_gift = models.BooleanField(default=False)
    gift_recipient_name = models.CharField(max_length=200, blank=True)
    gift_message = models.TextField(blank=True, max_length=300)
    interested_teas = models.JSONField(default=list)
    is_business = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"NQT-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4().int)[-4:]}"
        super().save(*args, **kwargs)
