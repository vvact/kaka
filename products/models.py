# models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Attribute(models.Model):
    """E.g., Color, Size, Material."""
    name = models.CharField(max_length=100, db_index=True)
    position = models.PositiveIntegerField(default=0, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)

    class Meta:
        ordering = ["position", "name"]

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """E.g., Red, Blue, Large, Cotton."""
    attribute = models.ForeignKey(Attribute, related_name="values", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    hex_code = models.CharField(max_length=7, blank=True, null=True)  # Optional for colors
    image = models.ImageField(upload_to="attribute_images/", blank=True, null=True)
    slug = models.SlugField(unique=True, db_index=True)

    class Meta:
        ordering = ["attribute__position", "attribute__name", "name"]
        unique_together = ('attribute', 'name')

    def __str__(self):
        return f"{self.attribute.name}: {self.name}"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)

    # SEO fields
    meta_title = models.CharField(max_length=255, blank=True, help_text="Optional SEO title")
    meta_description = models.TextField(blank=True, help_text="Optional SEO description")

    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    has_variants = models.BooleanField(default=False, db_index=True)
    stock = models.PositiveIntegerField(default=0)  # used if no variants
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_final_price(self):
        return self.discount_price if self.discount_price else self.base_price

    def is_new_arrival(self):
        return self.created_at >= timezone.now() - timedelta(days=30)

    class Meta:
        verbose_name_plural = "Products"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Variant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE, db_index=True)
    sku = models.CharField(max_length=100, unique=True, blank=True, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    attributes = models.ManyToManyField(AttributeValue, related_name="variants", blank=True)

    class Meta:
        verbose_name_plural = "Variants"
        ordering = ["product", "id"]

    def __str__(self):
        return f"{self.product.name} ({self.sku})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", db_index=True)
    image = models.ImageField(upload_to="product_images/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name_plural = "Product Images"
        ordering = ["-is_featured", "id"]

    def save(self, *args, **kwargs):
        if self.is_featured:
            ProductImage.objects.filter(product=self.product, is_featured=True).exclude(pk=self.pk).update(is_featured=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"


class VariantImage(models.Model):
    variant = models.OneToOneField(Variant, on_delete=models.CASCADE, related_name="image", db_index=True)
    image = models.ImageField(upload_to="variant_images/")
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "Variant Images"

    def __str__(self):
        return f"Image for {self.variant.product.name} ({self.variant.sku})"
