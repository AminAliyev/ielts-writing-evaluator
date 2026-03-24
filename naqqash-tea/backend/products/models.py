from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tea(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="teas")
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    story = models.TextField(blank=True)
    origin = models.CharField(max_length=200)
    altitude = models.CharField(max_length=100, blank=True)
    harvest_season = models.CharField(max_length=100, blank=True)
    tasting_notes = models.JSONField(default=list)
    brewing_temp = models.CharField(max_length=50, blank=True)
    brewing_time = models.CharField(max_length=50, blank=True)
    weight_options = models.JSONField(default=list)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_available_for_allocation = models.BooleanField(default=True)
    available_harvest_seasons = models.JSONField(default=list)
    image = models.ImageField(upload_to="teas/", blank=True)
    image_alt = models.CharField(max_length=300, blank=True)
    gallery = models.JSONField(default=list)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        return self.reviews.filter(is_approved=True).aggregate(v=Avg("rating"))["v"] or Decimal("0.00")

    @property
    def reviews_count(self):
        return self.reviews.filter(is_approved=True).count()

    def __str__(self):
        return self.name


class TeaReview(models.Model):
    tea = models.ForeignKey(Tea, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class TasterBoxConfig(models.Model):
    name = models.CharField(max_length=200, default="Naqqash Tea Taster Box")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    weight_per_tea_grams = models.IntegerField(default=50)
    teas = models.ManyToManyField(Tea, related_name="taster_boxes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            TasterBoxConfig.objects.exclude(id=self.id).update(is_active=False)
