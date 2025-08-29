# cart/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import CartItem
from .serializers import CartSerializer
from .utils import get_or_create_cart, add_item_to_cart
from products.models import Product


class CartViewSet(viewsets.ViewSet):
    """
    Handles cart operations (authenticated + guest).
    """

    def list(self, request):
        """
        GET /cart/ → fetch current cart
        """
        cart = get_or_create_cart(request)
        return Response(CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """
        POST /cart/add_item/
        Add a product or variant to the cart.
        Body: { product_id, variant_id (optional), quantity }
        """
        cart = get_or_create_cart(request)

        product_id = request.data.get("product_id")
        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        try:
            add_item_to_cart(cart, product, quantity=quantity, variant_id=variant_id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CartSerializer(cart, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def update_item(self, request):
        """
        POST /cart/update_item/
        Updates quantity of an item in the cart.
        Body: { item_id, quantity }
        """
        cart = get_or_create_cart(request)
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity", 1))

        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        try:
            add_item_to_cart(
                cart,
                item.product,
                quantity=quantity,
                variant=item.variant,
                override_quantity=True,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CartSerializer(cart, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        """
        POST /cart/remove_item/
        Body: { item_id }
        """
        cart = get_or_create_cart(request)
        item_id = request.data.get("item_id")

        if not item_id:
            return Response({"error": "item_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()

        cart.refresh_totals()
        return Response(CartSerializer(cart, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def clear(self, request):
        """
        POST /cart/clear/
        Clear all items in the cart
        """
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        cart.refresh_totals()
        return Response({"success": True, "cart": CartSerializer(cart, context={"request": request}).data})
