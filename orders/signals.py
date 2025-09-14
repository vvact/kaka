from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order
from cart.utils import clear_cart


@receiver(post_save, sender=Order)
def clear_cart_after_order(sender, instance, created, **kwargs):
    """
    Automatically clear cart once an order is created.
    Works for both logged-in and guest users.
    """
    if not created:
        return  # only act on new orders

    if instance.user:
        clear_cart(user=instance.user)
    elif instance.session_key:
        clear_cart(session_key=instance.session_key)
