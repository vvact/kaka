from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Product, Variant, ProductImage, VariantImage,
    Attribute, AttributeValue,Category
)



class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    show_change_link = True
    fields = ("sku", "price", "stock", "is_active", "attribute_preview")
    readonly_fields = ("attribute_preview",)
    autocomplete_fields = ("attributes",)

    def attribute_preview(self, obj):
        """Show color swatches or size chips in admin inline."""
        previews = []
        for attr in obj.attributes.all():
            if attr.attribute.name.lower() == "color":
                if getattr(attr, "hex_value", None):
                    previews.append(
                        format_html(
                            '<span style="display:inline-block; width:20px; height:20px; background:{}; border:1px solid #ccc;"></span> {}',
                            attr.hex_value,
                            attr.name
                        )
                    )
                elif getattr(attr, "image", None):
                    previews.append(
                        format_html(
                            '<img src="{}" style="width:20px; height:20px; border:1px solid #ccc;"> {}',
                            attr.image.url,
                            attr.name
                        )
                    )
            elif attr.attribute.name.lower() == "size":
                previews.append(
                    format_html(
                        '<span style="padding:2px 6px; border:1px solid #ccc; border-radius:4px;">{}</span>',
                        attr.name
                    )
                )
            else:
                previews.append(attr.name)

        return format_html(" ".join(str(p) for p in previews))
    attribute_preview.short_description = "Attributes"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "min_price", "max_price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, VariantInline]

    def min_price(self, obj):
        prices = obj.variants.values_list("price", flat=True)
        return min(prices) if prices else None

    def max_price(self, obj):
        prices = obj.variants.values_list("price", flat=True)
        return max(prices) if prices else None


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("product", "sku", "price", "stock", "is_active", "attribute_preview")
    list_filter = ("is_active",)
    search_fields = ("sku",)
    autocomplete_fields = ("product", "attributes")
    inlines = [VariantImageInline]

    def attribute_preview(self, obj):
        """Same swatch preview for the main Variant admin page."""
        previews = []
        for attr in obj.attributes.all():
            if attr.attribute.name.lower() == "color":
                if getattr(attr, "hex_value", None):
                    previews.append(
                        format_html(
                            '<span style="display:inline-block; width:20px; height:20px; background:{}; border:1px solid #ccc;"></span> {}',
                            attr.hex_value,
                            attr.name
                        )
                    )
                elif getattr(attr, "image", None):
                    previews.append(
                        format_html(
                            '<img src="{}" style="width:20px; height:20px; border:1px solid #ccc;"> {}',
                            attr.image.url,
                            attr.name
                        )
                    )
            elif attr.attribute.name.lower() == "size":
                previews.append(
                    format_html(
                        '<span style="padding:2px 6px; border:1px solid #ccc; border-radius:4px;">{}</span>',
                        attr.name
                    )
                )
            else:
                previews.append(attr.name)

        return format_html(" ".join(str(p) for p in previews))
    attribute_preview.short_description = "Attributes"



@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("name", "attribute", "hex_code", "image_preview")
    list_filter = ("attribute",)
    search_fields = ("name", "attribute__name")
    autocomplete_fields = ("attribute",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:20px; height:20px; border:1px solid #ccc;">',
                obj.image.url
            )
        if obj.hex_code:
            return format_html(
                '<span style="display:inline-block; width:20px; height:20px; background:{}; border:1px solid #ccc;"></span>',
                obj.hex_code
            )
        return "-"
    image_preview.short_description = "Swatch"
