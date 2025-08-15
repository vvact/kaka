from rest_framework import serializers
from .models import (
    Category, Attribute, AttributeValue, Product,
    Variant, ProductImage, VariantImage
)


# --- CATEGORY ---
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image"]

        


# --- ATTRIBUTES ---
class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ["id", "name", "slug", "hex_code", "image"]


class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True)

    class Meta:
        model = Attribute
        fields = ["id", "name", "position", "values"]


# --- VARIANTS ---
class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = ["image", "alt_text"]


class VariantSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()
    image = VariantImageSerializer(read_only=True)

    class Meta:
        model = Variant
        fields = ["id", "sku", "price", "stock", "is_active", "attributes", "image"]

    def get_attributes(self, obj):
        """
        Return variant attributes as { AttributeName: ValueName, ... }
        Example: { "Color": "Red", "Size": "M" }
        """
        return {
            attr.attribute.name: attr.name
            for attr in obj.attributes.all()
        }


# --- PRODUCT IMAGES ---
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text", "is_featured"]


# --- PRODUCTS ---
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    options = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, source="get_final_price", read_only=True)
    is_new_arrival = serializers.SerializerMethodField()

    min_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    max_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description",
            "meta_title", "meta_description",
            "base_price", "discount_price",  "min_price", "max_price", "final_price",
            "stock", "has_variants", "is_featured", "is_active",
            "category", "images", "options", "variants",
            "is_new_arrival", "price",
        ]

    def get_price(self, obj):
        """Return single value if min_price == max_price, else range."""
        if obj.min_price is None:
            return None
        if obj.min_price == obj.max_price:
            return str(obj.min_price)  # single price
        return f"{obj.min_price} - {obj.max_price}"  # price range

    def get_is_new_arrival(self, obj):
        return obj.is_new_arrival()

    def get_options(self, obj):
        if not obj.has_variants:
            return []

        variants = getattr(obj, "_prefetched_variants", [])
        attr_map = {}

        for v in variants:
            for av in v.attributes.all():
                attr = av.attribute
                if attr.id not in attr_map:
                    attr_map[attr.id] = {
                        "id": attr.id,
                        "name": attr.name,
                        "position": attr.position,
                        "values": {}
                    }
                if av.id not in attr_map[attr.id]["values"]:
                    val_data = {
                        "id": av.id,
                        "name": av.name,
                        "slug": av.slug,
                        "hex_code": av.hex_code,
                        "image": self._get_absolute_image_url(av.image)
                    }
                    attr_map[attr.id]["values"][av.id] = val_data

        # Sort by attribute position
        return [
            {
                "id": a["id"],
                "name": a["name"],
                "position": a["position"],
                "values": list(a["values"].values())
            }
            for a in sorted(attr_map.values(), key=lambda x: x["position"])
        ]

    def get_variants(self, obj):
        if not obj.has_variants:
            return []
        variants = getattr(obj, "_prefetched_variants", [])
        return VariantSerializer(variants, many=True).data

    def _get_absolute_image_url(self, image_field):
        request = self.context.get("request")
        if image_field:
            try:
                url = image_field.url
                if request:
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return None
        return None


class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "thumbnail", "price" ,"original_price"]

    def get_thumbnail(self, obj):
        """Return the featured product image if available."""
        featured_image = obj.images.filter(is_featured=True).first()
        if not featured_image:
            featured_image = obj.images.first()
        if featured_image and featured_image.image:
            return self.context["request"].build_absolute_uri(featured_image.image.url)
        return None

    def get_price(self, obj):
        """Final price to show on card (discount or variant min price)."""
        return obj.min_price

    def get_original_price(self, obj):
        """Original price (crossed out) if different from final price."""
        if obj.max_price != obj.min_price:
            return obj.max_price
        if obj.discount_price and obj.discount_price != obj.base_price:
            return obj.base_price
        return None


# --- 2️⃣ Category detail serializer with products ---
class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "products"]