from django.contrib import admin
from .models import Order, OrderItem
from payments.models import Payment

# ----------------------------
# Inline for Order Items
# ----------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "get_total")

    def get_total(self, obj):
        if obj.quantity is None or obj.price is None:
            return "-"
        return obj.quantity * obj.price
    get_total.short_description = "Total"

# ----------------------------
# Inline for Payment
# ----------------------------
class PaymentInline(admin.TabularInline):
    model = Payment
    readonly_fields = ("method", "status", "amount", "transaction_id", "created_at")
    can_delete = False
    extra = 0

# ----------------------------
# Order Admin
# ----------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone",
        "status",
        "created_at",
        "order_total",
        "get_payment_status",  # Shows payment method and status
    )
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "phone", "address")
    readonly_fields = ("created_at", "order_total")
    inlines = [OrderItemInline, PaymentInline]  # include payments inline

    # Total of order items
    def order_total(self, obj):
        total = sum(
            (item.quantity or 0) * (item.price or 0)
            for item in obj.items.all()
        )
        return total
    order_total.short_description = "Order Total"

    # Display payment status with readable labels
    def get_payment_status(self, obj):
        if hasattr(obj, "payment") and obj.payment:
            method = obj.payment.get_method_display()  # COD -> Cash on Delivery
            status = obj.payment.get_status_display()  # PENDING -> Pending
            return f"{method} ({status})"
        return "No payment yet"
    get_payment_status.short_description = "Payment"

# ----------------------------
# OrderItem Admin
# ----------------------------
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
