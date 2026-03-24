from django.contrib import admin
from .models import TasterBoxOrder


@admin.register(TasterBoxOrder)
class TasterBoxOrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "name", "email", "status", "country", "created_at")
    list_filter = ("status", "country")
    search_fields = ("order_number", "name", "email")
