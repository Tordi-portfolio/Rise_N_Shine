from django.contrib import admin

from .models import QuoteRequest


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "service", "frequency", "status", "created_at")
    list_filter = ("status", "service", "frequency")
    search_fields = ("name", "email", "phone", "zip_code")
    readonly_fields = ("created_at", "updated_at")
