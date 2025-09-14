# orders/views.py
from decimal import Decimal
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from cart.models import Cart
from cart.utils import clear_cart
from .models import Order, OrderItem
from .serializers import OrderSerializer


def get_cart(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return None
        return Cart.objects.filter(session_key=session_key, user=None).first()


class CheckoutView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        if not cart or not cart.items.exists():
            return Response({"cart": "No active cart found or cart is empty."}, status=400)

        full_name = request.data.get("full_name")
        phone = request.data.get("phone")
        address = request.data.get("address")

        if not full_name or not phone or not address:
            return Response({"error": "Full name, phone, and address are required."}, status=400)

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=None if request.user.is_authenticated else request.session.session_key,
            full_name=full_name,
            phone=phone,
            address=address,
        )

        # Copy items from cart
        for item in cart.items.all():
            product = item.product
            price = product.discount_price if product.discount_price else product.base_price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=price,
            )

            # Decrease stock (basic inventory control)
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save(update_fields=["stock"])

        # ✅ Clear the cart safely
        if request.user.is_authenticated:
            clear_cart(user=request.user)
        else:
            clear_cart(session_key=request.session.session_key)

        return Response(OrderSerializer(order).data, status=201)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
