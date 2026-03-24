from rest_framework import serializers
from .models import Category, Tea, TeaReview, TasterBoxConfig


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class TeaListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tea
        fields = [
            "id", "name", "slug", "category", "tagline", "origin", "price_per_kg", "weight_options",
            "currency", "image", "is_featured", "average_rating", "reviews_count"
        ]


class TeaDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Tea
        fields = "__all__"


class TeaReviewSerializer(serializers.ModelSerializer):
    tea_slug = serializers.SlugRelatedField(queryset=Tea.objects.all(), slug_field="slug", source="tea", write_only=True)

    class Meta:
        model = TeaReview
        fields = ["id", "name", "rating", "comment", "created_at", "tea_slug", "email"]
        read_only_fields = ["id", "created_at"]


class TasterBoxSerializer(serializers.ModelSerializer):
    teas = TeaListSerializer(many=True, read_only=True)

    class Meta:
        model = TasterBoxConfig
        fields = ["id", "name", "description", "price", "currency", "weight_per_tea_grams", "teas"]
