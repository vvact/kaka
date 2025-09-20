from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    product_image = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_slug",
            "product_image",
            "quantity",
            "price",
            "total_price",
        ]

    def get_product_image(self, obj):
        if hasattr(obj.product, "images") and obj.product.images.exists():
            return obj.product.images.first().image.url
        return None

    def get_total_price(self, obj):
        return obj.quantity * obj.price


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "full_name",
            "phone",
            "address",
            "status",
            "created_at",
            "items",
            "order_total",
        ]

    def get_order_total(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all())
