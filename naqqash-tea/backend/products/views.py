from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.response import Response
from .models import Category, Tea, TeaReview, TasterBoxConfig
from .serializers import CategorySerializer, TeaListSerializer, TeaDetailSerializer, TeaReviewSerializer, TasterBoxSerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TeaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tea.objects.select_related("category").filter(is_active=True)
    lookup_field = "slug"
    filterset_fields = ["category__slug", "is_featured", "is_active"]
    search_fields = ["name", "description", "origin"]
    ordering_fields = ["price_per_kg", "created_at", "name"]

    def get_serializer_class(self):
        return TeaDetailSerializer if self.action == "retrieve" else TeaListSerializer


class TeaReviewListByTeaView(generics.ListAPIView):
    serializer_class = TeaReviewSerializer

    def get_queryset(self):
        tea = get_object_or_404(Tea, slug=self.kwargs["slug"])
        return tea.reviews.filter(is_approved=True)


class TeaReviewCreateView(generics.CreateAPIView):
    serializer_class = TeaReviewSerializer

    def perform_create(self, serializer):
        serializer.save(is_approved=False)


class ActiveTasterBoxView(generics.GenericAPIView):
    serializer_class = TasterBoxSerializer

    def get(self, request):
        config = get_object_or_404(TasterBoxConfig, is_active=True)
        return Response(self.get_serializer(config).data)
