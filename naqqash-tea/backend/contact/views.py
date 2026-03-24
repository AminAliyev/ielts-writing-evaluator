from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics
from rest_framework.response import Response
from .models import ContactSubmission, NewsletterSubscriber, WholesaleInquiry, AllocationInquiry, MeetingRequest
from .serializers import ContactSubmissionSerializer, NewsletterSubscriberSerializer, WholesaleInquirySerializer, AllocationInquirySerializer, MeetingRequestSerializer


def _notify(subject: str, body: str, customer_email: str):
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_NOTIFICATION_EMAIL], fail_silently=True)
    send_mail(f"We received your message: {subject}", "Thank you for reaching out to Naqqash Tea.", settings.DEFAULT_FROM_EMAIL, [customer_email], fail_silently=True)


class SuccessCreateView(generics.CreateAPIView):
    success_message = "Submitted successfully."

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"success": True, "message": self.success_message}, status=response.status_code)


class ContactSubmitView(SuccessCreateView):
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    success_message = "Thanks for contacting us."

    def perform_create(self, serializer):
        obj = serializer.save()
        _notify("New contact submission", obj.message, obj.email)


class SubscribeView(SuccessCreateView):
    queryset = NewsletterSubscriber.objects.all()
    serializer_class = NewsletterSubscriberSerializer
    success_message = "Subscription successful."

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        obj, _ = NewsletterSubscriber.objects.get_or_create(email=email, defaults={"is_active": True})
        if not obj.is_active:
            obj.is_active = True
            obj.save(update_fields=["is_active"])
        return Response({"success": True, "message": self.success_message})


class WholesaleView(SuccessCreateView):
    queryset = WholesaleInquiry.objects.all()
    serializer_class = WholesaleInquirySerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        _notify("New wholesale inquiry", obj.message or "Wholesale inquiry", obj.email)


class AllocateView(SuccessCreateView):
    queryset = AllocationInquiry.objects.all()
    serializer_class = AllocationInquirySerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        _notify("New allocation inquiry", obj.special_requests or "Allocation inquiry", obj.email)


class MeetingRequestView(SuccessCreateView):
    queryset = MeetingRequest.objects.all()
    serializer_class = MeetingRequestSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        _notify("New meeting request", obj.message or "Meeting request", obj.email)
