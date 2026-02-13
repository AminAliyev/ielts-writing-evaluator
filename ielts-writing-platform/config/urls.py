"""URL configuration for IELTS Writing Platform."""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    """
    Return a simple health-check response indicating service status.
    
    Returns:
        JsonResponse: JSON object {"status": "ok"}.
    """
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', health_check, name='health_check'),
    path('', include('core.urls')),
]