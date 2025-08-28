from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("final_price_display",)
    fields = ("product", "variant", "quantity", "final_price_display")
    
    def final_price_display(self, obj):
        return obj.final_price()
    final_price_display.short_description = "Final Price"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "total_price_display", "is_expired", "created_at", "updated_at")
    list_filter = ("user", "created_at", "updated_at")
    search_fields = ("user__email", "session_key")
    readonly_fields = ("created_at", "updated_at", "total_price_display", "is_expired")
    inlines = [CartItemInline]

    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = "Total Price"

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
