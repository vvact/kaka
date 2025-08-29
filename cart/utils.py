# cart/utils.py
from django.utils import timezone
from django.db import transaction
from .models import Cart, CartItem
from products.models import Product, Variant
import uuid

GUEST_CART_EXPIRATION_DAYS = 7


def get_or_create_cart(request):
    """Return cart for logged-in user or guest, creating if needed."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.get("cart_key")
        if not session_key:
            session_key = str(uuid.uuid4())
            request.session["cart_key"] = session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        cart.expires_at = timezone.now() + timezone.timedelta(days=GUEST_CART_EXPIRATION_DAYS)
        cart.save(update_fields=["expires_at"])
    return cart


def merge_guest_cart_to_user(user, session_key):
    """Merge guest cart into user's cart upon login."""
    try:
        guest_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    with transaction.atomic():
        for item in guest_cart.items.all():
            cart_item, created = CartItem.objects.select_for_update().get_or_create(
                cart=user_cart,
                product=item.product,
                variant=item.variant,
                defaults={"quantity": item.quantity}
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save(update_fields=["quantity"])
        guest_cart.delete()
    user_cart.refresh_totals()


def validate_stock(product, variant=None, quantity=1):
    """Raise error if quantity exceeds stock."""
    stock = variant.stock if variant else product.stock
    if quantity > stock:
        raise ValueError(f"Only {stock} units available for {variant.sku if variant else product.name}")


def add_item_to_cart(cart, product, quantity=1, variant=None, override_quantity=False):
    """Add or update a cart item, handling both base and variant products."""
    validate_stock(product, variant, quantity)

    with transaction.atomic():
        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={"quantity": quantity}
        )
        if not created:
            if override_quantity:
                validate_stock(product, variant, quantity)
                item.quantity = quantity
            else:
                validate_stock(product, variant, item.quantity + quantity)
                item.quantity += quantity
            item.save(update_fields=["quantity"])
        cart.refresh_totals()
    return item


def remove_item_from_cart(cart, product, variant=None):
    """Remove a product/variant from cart and refresh totals."""
    CartItem.objects.filter(cart=cart, product=product, variant=variant).delete()
    cart.refresh_totals()


def cleanup_expired_carts():
    """Delete expired guest carts."""
    Cart.objects.filter(user__isnull=True, expires_at__lt=timezone.now()).delete()
