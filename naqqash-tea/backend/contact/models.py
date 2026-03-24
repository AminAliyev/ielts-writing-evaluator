from django.db import models


class ContactSubmission(models.Model):
    SUBJECT_CHOICES = [
        ("general", "General Question"), ("order", "Order Inquiry"), ("wholesale", "Wholesale"), ("press", "Press"), ("other", "Other")
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)


class WholesaleInquiry(models.Model):
    STATUS_CHOICES = [("new", "New"), ("contacted", "Contacted"), ("sample_sent", "Sample Sent"), ("negotiating", "Negotiating"), ("active", "Active Account"), ("declined", "Declined"), ("churned", "Churned")]
    BUSINESS_TYPES = [("cafe", "Cafe / Restaurant"), ("hotel", "Hotel"), ("retail", "Retail Store"), ("distributor", "Distributor"), ("corporate", "Corporate Gifting"), ("other", "Other")]
    company_name = models.CharField(max_length=300)
    contact_person = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
    country = models.CharField(max_length=100)
    monthly_volume = models.CharField(max_length=50)
    message = models.TextField(blank=True)
    wants_taster = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AllocationInquiry(models.Model):
    STATUS_CHOICES = [("new", "New"), ("contacted", "Contacted"), ("proposal_sent", "Proposal Sent"), ("confirmed", "Confirmed"), ("declined", "Declined")]
    DELIVERY_CHOICES = [("ship", "Ship to Me"), ("pickup", "Pick Up in Baku")]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    teas_requested = models.JSONField()
    harvest_season = models.CharField(max_length=50)
    delivery_preference = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default="ship")
    special_requests = models.TextField(blank=True)
    wants_meeting = models.BooleanField(default=False)
    meeting_format = models.CharField(max_length=30, blank=True)
    wants_taster = models.BooleanField(default=False)
    shipping_address = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MeetingRequest(models.Model):
    STATUS_CHOICES = [("new", "New"), ("scheduled", "Scheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    meeting_type = models.CharField(max_length=30)
    preferred_datetime = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    calendar_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
