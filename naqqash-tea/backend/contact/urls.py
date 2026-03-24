from django.urls import path
from .views import ContactSubmitView, SubscribeView, WholesaleView, AllocateView, MeetingRequestView

urlpatterns = [
    path("submit/", ContactSubmitView.as_view()),
    path("subscribe/", SubscribeView.as_view()),
    path("wholesale/", WholesaleView.as_view()),
    path("allocate/", AllocateView.as_view()),
    path("meeting-request/", MeetingRequestView.as_view()),
]
