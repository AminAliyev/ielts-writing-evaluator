from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryListView, TeaViewSet, TeaReviewListByTeaView, TeaReviewCreateView, ActiveTasterBoxView

router = DefaultRouter()
router.register("teas", TeaViewSet, basename="tea")

urlpatterns = [
    path("categories/", CategoryListView.as_view()),
    path("", include(router.urls)),
    path("teas/<slug:slug>/reviews/", TeaReviewListByTeaView.as_view()),
    path("reviews/", TeaReviewCreateView.as_view()),
    path("taster-box/", ActiveTasterBoxView.as_view()),
]
