# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_image = serializers.ReadOnlyField(source='product.thumbnail')  # adjust field

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'payment_method', 'total_amount', 'delivery_address', 'contact_phone', 'status', 'items', 'created_at']
        read_only_fields = ['user', 'status', 'total_amount', 'created_at']

class CreateOrderSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHODS)
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    contact_phone = serializers.CharField()
