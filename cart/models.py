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
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def is_expired(self):
        return self.expires_at and self.expires_at < timezone.now()

    def set_expiration(self, days=7):
        self.expires_at = timezone.now() + timezone.timedelta(days=days)
        self.save(update_fields=["expires_at"])

    def total_price(self, recalc=False):
        if recalc or self.total is None:
            return sum([item.final_price() for item in self.items.all()]) or Decimal("0.00")
        return self.total

    def refresh_totals(self):
        self.total = sum([item.final_price() for item in self.items.all()]) or Decimal("0.00")
        self.updated_at = timezone.now()
        self.save(update_fields=["total", "updated_at"])

    def merge_with(self, other_cart):
        for item in other_cart.items.all():
            obj, created = CartItem.objects.get_or_create(
                cart=self,
                product=item.product,
                variant=item.variant,
                defaults={"quantity": item.quantity}
            )
            if not created:
                obj.quantity += item.quantity
                obj.save()
        other_cart.delete()
        self.refresh_totals()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    variant = models.ForeignKey("products.Variant", null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product", "variant")

    def clean(self):
        if self.variant:
            if self.quantity > self.variant.stock:
                raise ValueError(f"Only {self.variant.stock} left in stock")
        elif self.quantity > self.product.stock:
            raise ValueError(f"Only {self.product.stock} left in stock")

    def final_price(self):
        price = self.variant.price if self.variant else (self.product.discount_price or self.product.base_price)
        return price * self.quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cart.refresh_totals()

    def delete(self, *args, **kwargs):
        cart = self.cart
        super().delete(*args, **kwargs)
        cart.refresh_totals()
