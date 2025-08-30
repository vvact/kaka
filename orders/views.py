# orders/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from cart.models import Cart  # adjust if your Cart model is in another app

class OrderListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def post(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get user's cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.items.count() == 0:
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Create order
        order = Order.objects.create(
            user=request.user,
            payment_method=serializer.validated_data['payment_method'],
            delivery_address=serializer.validated_data.get('delivery_address', ''),
            contact_phone=serializer.validated_data['contact_phone'],
            total_amount=sum([item.price * item.quantity for item in cart.items.all()])
        )

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.price
            )

        # Clear cart
        cart.items.all().delete()
        cart.cart_total = 0
        cart.item_count = 0
        cart.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

