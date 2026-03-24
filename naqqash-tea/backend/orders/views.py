
try:
    import stripe
except Exception:
    stripe = None
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import TasterBoxConfig
from .models import TasterBoxOrder
from .serializers import TasterBoxOrderCreateSerializer, TasterBoxOrderStatusSerializer

if stripe:
    stripe.api_key = settings.STRIPE_SECRET_KEY


class TasterBoxOrderCreateView(APIView):
    def post(self, request):
        config = TasterBoxConfig.objects.filter(is_active=True).first()
        if not config:
            return Response({"detail": "No active taster box configuration."}, status=400)
        serializer = TasterBoxOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(price=config.price, currency=config.currency)
        if not stripe:
            return Response({"detail": "Stripe SDK unavailable in this environment."}, status=503)
        intent = stripe.PaymentIntent.create(
            amount=int(config.price * 100),
            currency=config.currency.lower(),
            metadata={"order_number": order.order_number},
            automatic_payment_methods={"enabled": True},
        )
        order.stripe_payment_intent_id = intent.id
        order.save(update_fields=["stripe_payment_intent_id"])
        return Response({"order_id": order.id, "order_number": order.order_number, "stripe_client_secret": intent.client_secret})


class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            if not stripe:
                return HttpResponse(status=503)
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except Exception:
            return HttpResponse(status=400)

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            order = TasterBoxOrder.objects.filter(stripe_payment_intent_id=intent["id"]).first()
            if order:
                order.status = "paid"
                order.save(update_fields=["status"])
                send_mail(
                    f"Naqqash Tea order confirmed: {order.order_number}",
                    "Thank you for ordering the taster box.",
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=True,
                )
        return HttpResponse(status=200)


class TasterBoxOrderStatusView(APIView):
    def get(self, request, order_number):
        email = request.query_params.get("email")
        order = get_object_or_404(TasterBoxOrder, order_number=order_number, email=email)
        return Response(TasterBoxOrderStatusSerializer(order).data)
