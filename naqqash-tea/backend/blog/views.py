from rest_framework import viewsets, generics
from .models import Post, PostCategory
from .serializers import PostSerializer, PostCategorySerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    lookup_field = "slug"
    queryset = Post.objects.filter(is_published=True).order_by("-published_at")
    filterset_fields = ["category__slug", "is_featured"]


class PostCategoryListView(generics.ListAPIView):
    queryset = PostCategory.objects.all()
    serializer_class = PostCategorySerializer
