# cart/management/commands/cleanup_expired_carts.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from cart.models import Cart

class Command(BaseCommand):
    help = 'Delete expired guest carts'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_carts = Cart.objects.filter(user__isnull=True, expires_at__lte=now)
        count = expired_carts.count()
        expired_carts.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} expired guest carts.'))
