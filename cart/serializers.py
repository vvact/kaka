# cart/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source="id", read_only=True)  # 👈 expose item_id
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.SlugField(source="product.slug", read_only=True)
    product_image = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()
    max_quantity = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "item_id",        # 👈 use item_id instead of raw id
            "product",
            "product_name",
            "product_slug",
            "product_image",
            "unit_price",
            "quantity",
            "line_total",
            "max_quantity",
        ]

    def get_max_quantity(self, obj):
        # if variant exists, use variant stock; else use product stock
        return obj.variant.stock if obj.variant else obj.product.stock

    def get_product_image(self, obj):
        request = self.context.get("request")

        # 1️⃣ Variant image first
        if obj.variant and hasattr(obj.variant, "image") and obj.variant.image and obj.variant.image.image:
            return request.build_absolute_uri(obj.variant.image.image.url) if request else obj.variant.image.image.url

        # 2️⃣ Product featured image
        featured = obj.product.images.filter(is_featured=True).first()
        if featured and featured.image:
            return request.build_absolute_uri(featured.image.url) if request else featured.image.url

        # 3️⃣ Any product image fallback
        first_image = obj.product.images.first()
        if first_image and first_image.image:
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url

        return None

    def get_unit_price(self, obj):
        return obj.variant.price if obj.variant else obj.product.discount_price or obj.product.base_price

    def get_line_total(self, obj):
        return self.get_unit_price(obj) * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "cart_total", "item_count"]

    def get_cart_total(self, obj):
        return sum([item.final_price() for item in obj.items.all()])

    def get_item_count(self, obj):
        return sum([item.quantity for item in obj.items.all()])
