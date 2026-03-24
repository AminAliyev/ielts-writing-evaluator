from django.contrib import admin
from .models import ContactSubmission, NewsletterSubscriber, WholesaleInquiry, AllocationInquiry, MeetingRequest


@admin.action(description="Mark selected as read")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "is_read", "created_at")
    list_filter = ("subject", "is_read")
    actions = [mark_as_read]


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")


@admin.register(WholesaleInquiry)
class WholesaleInquiryAdmin(admin.ModelAdmin):
    list_display = ("company_name", "business_type", "status", "country", "created_at")
    list_filter = ("status", "business_type", "country")


@admin.register(AllocationInquiry)
class AllocationInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "harvest_season", "country", "created_at")
    list_filter = ("status", "harvest_season", "country")


@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "meeting_type", "status", "created_at")
    list_filter = ("status", "meeting_type")
