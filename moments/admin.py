# moments/admin.py
from django.contrib import admin
from .models import Moment

@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ("id", "caption", "is_featured", "is_active", "created_at")
    list_filter = ("is_featured", "is_active", "created_at")
    search_fields = ("caption",)
    readonly_fields = ("created_at",)
