# cart/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return self.expires_at and self.expires_at < timezone.now()

    def set_expiration(self, days=7):
        """Set cart expiration for guests"""
        self.expires_at = timezone.now() + timezone.timedelta(days=days)
        self.save(update_fields=["expires_at"])

    def total_price(self):
        """Calculate total price of cart"""
        return sum([item.final_price() for item in self.items.all()]) or Decimal("0.00")

    def refresh_totals(self):
        """Call after any item addition/removal to refresh totals"""
        # Optional: could cache total in DB field for performance
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    variant = models.ForeignKey("products.Variant", null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product", "variant")

    def final_price(self):
        """Price considering variant or product"""
        price = self.variant.price if self.variant else (self.product.discount_price or self.product.base_price)
        return price * self.quantity
