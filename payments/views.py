from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order

class InitiatePaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        method = request.data.get("method", "COD")

        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create payment record
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "user": request.user,
                "method": method,
                "amount": order.order_total,
            }
        )

        # Here we can trigger STK push if method == MPESA
        response = PaymentSerializer(payment).data
        if method == "MPESA":
            response["message"] = "Trigger STK Push here."

        return Response(response, status=status.HTTP_201_CREATED)
