# cart/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart
from .utils import get_or_create_cart, add_item_to_cart, remove_item_from_cart
from .serializers import CartSerializer
from products.models import Product, Variant

class CartViewSet(viewsets.ViewSet):
    """Cart endpoints: list, add_item, remove_item, update_item."""

    def list(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        cart = get_or_create_cart(request)
        product_id = request.data.get("product_id")
        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))

        product = Product.objects.get(id=product_id)
        variant = Variant.objects.filter(id=variant_id).first() if variant_id else None
        item = add_item_to_cart(cart, product, quantity, variant)

        cart.refresh_totals()  # recalc totals
        return Response({"success": True, "item_id": item.id, "cart_total": str(cart.total_price())})

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        cart = get_or_create_cart(request)
        product_id = request.data.get("product_id")
        variant_id = request.data.get("variant_id")

        product = Product.objects.get(id=product_id)
        variant = Variant.objects.filter(id=variant_id).first() if variant_id else None
        remove_item_from_cart(cart, product, variant)

        cart.refresh_totals()  # recalc totals
        return Response({"success": True, "cart_total": str(cart.total_price())})

    @action(detail=False, methods=["post"])
    def update_item(self, request):
        """
        Update existing cart item:
        - Change quantity
        - Switch variant
        """
        cart = get_or_create_cart(request)
        product_id = request.data.get("product_id")
        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))

        if quantity < 1:
            return Response({"detail": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.get(id=product_id)
        variant = Variant.objects.filter(id=variant_id).first() if variant_id else None

        # Use existing helper to add or update
        item = add_item_to_cart(cart, product, quantity, variant, override_quantity=True)

        cart.refresh_totals()  # recalc totals
        return Response({
            "success": True,
            "item": {
                "id": item.id,
                "product_id": item.product.id,
                "variant_id": item.variant.id if item.variant else None,
                "quantity": item.quantity,
                "price": str(item.final_price())  # use final_price() from CartItem
            },
            "cart_total": str(cart.total_price())
        })
