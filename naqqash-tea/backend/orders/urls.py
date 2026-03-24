from django.urls import path
from .views import TasterBoxOrderCreateView, StripeWebhookView, TasterBoxOrderStatusView

urlpatterns = [
    path("taster-box/", TasterBoxOrderCreateView.as_view()),
    path("webhook/stripe/", StripeWebhookView.as_view()),
    path("taster-box/<str:order_number>/", TasterBoxOrderStatusView.as_view()),
]
