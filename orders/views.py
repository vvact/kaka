from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cart.models import Cart
from cart.utils import clear_cart
from .models import Order, OrderItem
from .serializers import OrderSerializer
from payments.models import Payment


def get_cart(request):
    """Fetch the cart for the logged-in user."""
    return Cart.objects.filter(user=request.user).first()


class CheckoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        if not cart or not cart.items.exists():
            return Response(
                {"cart": "No active cart found or cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1️⃣ Get checkout info
        full_name = request.data.get("full_name")
        phone = request.data.get("phone")
        address = request.data.get("address")
        payment_method = request.data.get("payment_method", "COD").upper()

        if not all([full_name, phone, address]):
            return Response(
                {"error": "Full name, phone, and address are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if payment_method not in ["COD", "STK"]:
            return Response(
                {"error": "Invalid payment method. Choose 'COD' or 'STK'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2️⃣ Create the order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
        )

        # 3️⃣ Copy cart items to order items & calculate total
        order_items = []
        total_amount = 0

        for cart_item in cart.items.all():
            product = cart_item.product
            price = cart_item.variant.price if getattr(cart_item, "variant", None) else (product.discount_price or product.base_price)
            line_total = price * cart_item.quantity
            total_amount += line_total

            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=price
            ))

            # Reduce stock safely
            if getattr(cart_item, "variant", None):
                if cart_item.variant.stock >= cart_item.quantity:
                    cart_item.variant.stock -= cart_item.quantity
                    cart_item.variant.save(update_fields=["stock"])
            else:
                if product.stock >= cart_item.quantity:
                    product.stock -= cart_item.quantity
                    product.save(update_fields=["stock"])

        OrderItem.objects.bulk_create(order_items)

        # 4️⃣ Create Payment linked to this order
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            method=payment_method,
            amount=total_amount,  # ✅ amount must be set
            status="PENDING"
        )

        # 5️⃣ Clear user's cart
        clear_cart(user=request.user)

        # 6️⃣ Return order + payment info
        data = OrderSerializer(order).data
        data["payment"] = {
            "id": payment.id,
            "method": payment.method,
            "status": payment.status,
            "amount": float(payment.amount)
        }

        return Response(data, status=status.HTTP_201_CREATED)


# ----------------------------
# List & Detail Views
# ----------------------------

class OrderListView(generics.ListAPIView):
    """List all orders of the logged-in user."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class OrderDetailView(generics.RetrieveAPIView):
    """Fetch a single order detail for the logged-in user."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
