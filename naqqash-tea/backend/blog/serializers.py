from rest_framework import serializers
from .models import Post, PostCategory, Tag


class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "slug"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class PostSerializer(serializers.ModelSerializer):
    category = PostCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    read_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"
