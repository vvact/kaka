from django.conf import settings
from django.db import models
from orders.models import Order

class Payment(models.Model):
    PAYMENT_METHODS = [
        ("POD", "Pash on Delivery"),
        ("MPESA", "M-Pesa"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)  # for STK Push reference
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status} ({self.method})"

