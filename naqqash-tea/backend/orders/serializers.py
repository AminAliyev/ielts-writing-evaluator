from rest_framework import serializers
from .models import TasterBoxOrder


class TasterBoxOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasterBoxOrder
        exclude = ["status", "stripe_payment_intent_id", "shipped_at", "tracking_number", "order_number", "created_at", "updated_at"]


class TasterBoxOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasterBoxOrder
        fields = ["order_number", "name", "email", "status", "country", "created_at"]
