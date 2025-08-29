# cart/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart
from .utils import get_or_create_cart, add_item_to_cart, remove_item_from_cart
from .serializers import CartSerializer
from products.models import Product, Variant, AttributeValue


class CartViewSet(viewsets.ViewSet):
    """Cart endpoints with flexible attribute-driven variant selection."""

    def _cart_response(self, cart, success=True):
        serializer = CartSerializer(cart, context={'request': self.request})
        return Response({"success": success, "cart": serializer.data})

    def list(self, request):
        cart = get_or_create_cart(request)
        return self._cart_response(cart)

    def _get_variant_from_attributes(self, product, attributes: dict):
        variant_qs = Variant.objects.filter(product=product, is_active=True)
        for attr_name, value_name in attributes.items():
            variant_qs = variant_qs.filter(attributes__name=value_name)
        return variant_qs.first()

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        cart = get_or_create_cart(request)
        product_id = request.data.get("product_id")
        attributes = request.data.get("attributes", {})
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"success": False, "detail": "product_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        variant = None
        if product.has_variants:
            if not attributes:
                return Response({"success": False, "detail": "attributes are required for products with variants"},
                                status=status.HTTP_400_BAD_REQUEST)
            variant = self._get_variant_from_attributes(product, attributes)
            if not variant:
                return Response({"success": False, "detail": "No variant matches the selected options"},
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            add_item_to_cart(cart, product, quantity, variant)
            cart.refresh_totals()
            return self._cart_response(cart)
        except ValueError as e:
            return Response({"success": False, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        cart = get_or_create_cart(request)
        product_id = request.data.get("product_id")
        attributes = request.data.get("attributes", {})

        if not product_id:
            return Response({"success": False, "detail": "product_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        variant = None
        if product.has_variants:
            if not attributes:
                return Response({"success": False, "detail": "attributes are required for products with variants"},
                                status=status.HTTP_400_BAD_REQUEST)
            variant = self._get_variant_from_attributes(product, attributes)
            if not variant:
                return Response({"success": False, "detail": "No variant matches the selected options"},
                                status=status.HTTP_400_BAD_REQUEST)

        remove_item_from_cart(cart, product, variant)
        cart.refresh_totals()
        return self._cart_response(cart)

    @action(detail=False, methods=["post"])
    def update_item(self, request):
        cart = get_or_create_cart(request)
        product_id = request.data.get("product_id")
        attributes = request.data.get("attributes", {})
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"success": False, "detail": "product_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if quantity < 1:
            return Response({"success": False, "detail": "Quantity must be at least 1"},
                            status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        variant = None
        if product.has_variants:
            if not attributes:
                return Response({"success": False, "detail": "attributes are required for products with variants"},
                                status=status.HTTP_400_BAD_REQUEST)
            variant = self._get_variant_from_attributes(product, attributes)
            if not variant:
                return Response({"success": False, "detail": "No variant matches the selected options"},
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            add_item_to_cart(cart, product, quantity, variant, override_quantity=True)
            cart.refresh_totals()
            return self._cart_response(cart)
        except ValueError as e:
            return Response({"success": False, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @action(detail=False, methods=["post"])
    def clear_cart(self, request):
        """
        Remove all items from the cart.
        """
        cart = get_or_create_cart(request)
        cart.items.all().delete()  # assuming you have a related_name 'items' for cart items
        cart.refresh_totals()
        return Response({
            "success": True,
            "cart": CartSerializer(cart, context={'request': request}).data
        }, status=status.HTTP_200_OK)
