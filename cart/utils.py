from django.utils import timezone
from django.db import transaction
from .models import Cart, CartItem
from products.models import Product, Variant
import uuid

GUEST_CART_EXPIRATION_DAYS = 7


def get_or_create_cart(request):
    """
    Return cart for logged-in user or guest, creating if needed.
    Auto-merge guest cart if user logs in.
    """
    if request.user.is_authenticated:
        # 1️⃣ Get or create cart for logged-in user
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # 2️⃣ Merge guest cart if exists
        session_key = request.session.get("cart_key")
        if session_key:
            merge_guest_cart_to_user(request.user, session_key)
            request.session.pop("cart_key", None)  # remove session key after merge

        return cart

    # Guest cart
    session_key = request.session.get("cart_key")
    if not session_key:
        session_key = str(uuid.uuid4())
        request.session["cart_key"] = session_key

    cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
    cart.expires_at = timezone.now() + timezone.timedelta(days=GUEST_CART_EXPIRATION_DAYS)
    cart.save(update_fields=["expires_at"])
    return cart


def merge_guest_cart_to_user(user, session_key):
    """
    Merge guest cart (session) into logged-in user cart.
    """
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

        guest_cart.delete()  # remove guest cart after merge
    user_cart.refresh_totals()


def validate_stock(product, variant=None, quantity=1):
    stock = variant.stock if variant else product.stock
    if quantity > stock:
        raise ValueError(f"Only {stock} units available for {variant.sku if variant else product.name}")


def add_item_to_cart(cart, product, quantity=1, variant=None, variant_id=None, override_quantity=False):
    if variant_id and not variant:
        variant = Variant.objects.filter(id=variant_id, product=product).first()
        if not variant:
            raise ValueError("Invalid variant_id for this product")

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


def remove_item_from_cart(cart, product, variant=None, variant_id=None):
    if variant_id and not variant:
        variant = Variant.objects.filter(id=variant_id, product=product).first()
    CartItem.objects.filter(cart=cart, product=product, variant=variant).delete()
    cart.refresh_totals()


def cleanup_expired_carts():
    Cart.objects.filter(user__isnull=True, expires_at__lt=timezone.now()).delete()


def get_cart_items(user=None, session_key=None):
    if user:
        try:
            cart = Cart.objects.get(user=user)
            return cart.items.all()
        except Cart.DoesNotExist:
            return CartItem.objects.none()
    elif session_key:
        try:
            cart = Cart.objects.get(session_key=session_key, user__isnull=True)
            return cart.items.all()
        except Cart.DoesNotExist:
            return CartItem.objects.none()
    return CartItem.objects.none()


def clear_cart(user=None, session_key=None):
    if user:
        try:
            cart = Cart.objects.get(user=user)
            cart.items.all().delete()
            cart.refresh_totals()
        except Cart.DoesNotExist:
            pass
    elif session_key:
        try:
            cart = Cart.objects.get(session_key=session_key, user__isnull=True)
            cart.items.all().delete()
            cart.refresh_totals()
        except Cart.DoesNotExist:
            pass
