# payments/admin.py
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'method', 'status', 'amount', 'transaction_id', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('order__id', 'user__email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'transaction_id')
