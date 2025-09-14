# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "get_total")

    def get_total(self, obj):
        if obj.quantity is None or obj.price is None:
            return "-"
        return obj.quantity * obj.price
    get_total.short_description = "Total"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "status", "created_at", "order_total")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "phone", "address")
    readonly_fields = ("created_at", "order_total")
    inlines = [OrderItemInline]

    def order_total(self, obj):
        total = sum(
            (item.quantity or 0) * (item.price or 0)
            for item in obj.items.all()
        )
        return total
    order_total.short_description = "Order Total"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price", "get_total")
    search_fields = ("product__name", "order__full_name")
    list_filter = ("order__status",)

    def get_total(self, obj):
        if obj.quantity is None or obj.price is None:
            return "-"
        return obj.quantity * obj.price
    get_total.short_description = "Total"
