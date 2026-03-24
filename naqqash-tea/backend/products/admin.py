from django.contrib import admin
from .models import Category, Tea, TeaReview, TasterBoxConfig


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)


@admin.register(Tea)
class TeaAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_per_kg", "is_featured", "is_active")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("name", "origin")
    fieldsets = (
        ("Basic Info", {"fields": ("name", "slug", "category", "tagline", "origin", "altitude", "harvest_season")}),
        ("Content", {"fields": ("description", "story", "tasting_notes", "brewing_temp", "brewing_time")}),
        ("Pricing", {"fields": ("price_per_kg", "currency", "weight_options")}),
        ("Media", {"fields": ("image", "image_alt", "gallery")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
        ("Allocation", {"fields": ("is_featured", "is_active", "is_available_for_allocation", "available_harvest_seasons")}),
    )


@admin.action(description="Approve selected reviews")
def approve_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="Reject selected reviews")
def reject_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.register(TeaReview)
class TeaReviewAdmin(admin.ModelAdmin):
    list_display = ("tea", "name", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    actions = [approve_reviews, reject_reviews]


@admin.register(TasterBoxConfig)
class TasterBoxConfigAdmin(admin.ModelAdmin):
    filter_horizontal = ("teas",)
