# cart/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem

@receiver(user_logged_in)
def merge_guest_cart(sender, request, user, **kwargs):
    """
    When a guest logs in, merge their session cart into their user cart.
    """
    session_key = request.session.session_key
    if not session_key:
        return

    try:
        guest_cart = Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        return

    # Get or create user cart
    user_cart, _ = Cart.objects.get_or_create(user=user)

    # Merge items
    for item in guest_cart.items.all():
        # Check if same product+variant exists
        existing_item_qs = user_cart.items.filter(product=item.product)
        if item.variant:
            existing_item_qs = existing_item_qs.filter(variant=item.variant)

        if existing_item_qs.exists():
            existing_item = existing_item_qs.first()
            # Sum quantities but respect stock
            stock = item.variant.stock if item.variant else item.product.stock
            new_qty = min(existing_item.quantity + item.quantity, stock)
            existing_item.quantity = new_qty
            existing_item.save()
        else:
            # Transfer ownership to user cart
            item.cart = user_cart
            item.save()

    # Delete guest cart
    guest_cart.delete()
