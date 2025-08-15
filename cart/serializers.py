# cart/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    variant_id = serializers.IntegerField(source="variant.id", read_only=True)
    variant_attributes = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id", "product_name", "product_slug", "variant_id",
            "variant_attributes", "quantity", "final_price"
        ]

    def get_variant_attributes(self, obj):
        if obj.variant:
            return {attr.attribute.name: attr.value for attr in obj.variant.attributes.all()}
        return None

    def get_final_price(self, obj):
        return obj.final_price()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]

    def get_total_price(self, obj):
        return obj.total_price()
