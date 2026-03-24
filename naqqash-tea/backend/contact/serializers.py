from rest_framework import serializers
from .models import ContactSubmission, NewsletterSubscriber, WholesaleInquiry, AllocationInquiry, MeetingRequest


class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = "__all__"


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]


class WholesaleInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = WholesaleInquiry
        fields = "__all__"


class AllocationInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = AllocationInquiry
        fields = "__all__"


class MeetingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRequest
        fields = "__all__"
