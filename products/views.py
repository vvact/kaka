from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Min, Max, Case, When, DecimalField, Count, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from .models import Product, ProductImage, Variant, Category
from .serializers import (
    ProductSerializer,
    ProductListSerializer,
    VariantSerializer,
    CategorySerializer,
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Product endpoints:
      - list: lightweight ProductListSerializer
      - retrieve: full ProductSerializer
      - slug is used for lookup
    """
    lookup_field = "slug"
    variant_qs = Variant.objects.prefetch_related("attributes__attribute", "image")
    queryset = Product.objects.select_related("category").prefetch_related(
        "images",
        Prefetch("variants", queryset=variant_qs, to_attr="_prefetched_variants"),
    )

    def get_serializer_class(self):
        return ProductListSerializer if self.action == "list" else ProductSerializer

    def get_queryset(self):
        qs = self.queryset

        # --- SEARCH ---
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(slug__icontains=search))

        # --- PRICE RANGE ANNOTATIONS ---
        qs = qs.annotate(
            min_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Min("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            max_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Max("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        return qs

    @action(detail=True, methods=["post"])
    def variant_lookup(self, request, slug=None):
        """
        Given a list of attribute value IDs, return the matching variant.
        """
        product = self.get_object()
        value_ids = request.data.get("value_ids") or []
        if not isinstance(value_ids, list) or not value_ids:
            return Response({"detail": "value_ids list required"}, status=400)

        target = set(map(int, value_ids))
        variants = getattr(product, "_prefetched_variants", None) or product.variants.prefetch_related("attributes")
        match = next((v for v in variants if set(v.attributes.values_list("id", flat=True)) == target), None)

        if not match:
            return Response({"detail": "No matching variant"}, status=404)

        return Response({
            "variant_id": match.id,
            "sku": match.sku,
            "price": str(match.price),
            "stock": match.stock,
            "in_stock": bool(match.is_active and match.stock > 0),
            "attributes": [
                {"id": av.id, "name": av.name, "attribute": av.attribute.name}
                for av in match.attributes.all()
            ]
        })


class VariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only Variant endpoints.
    """
    serializer_class = VariantSerializer
    queryset = Variant.objects.prefetch_related("attributes__attribute", "image").select_related("product")


class ProductListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Alternative product list view with filters (featured/new arrivals).
    """
    serializer_class = ProductListSerializer
    queryset = Product.objects.all().prefetch_related("images")

    def get_queryset(self):
        qs = self.queryset

        # --- SEARCH ---
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(slug__icontains=search))

        # --- FEATURED FILTER ---
        featured = self.request.query_params.get("featured")
        if featured is not None:
            qs = qs.filter(is_featured=(featured.lower() == "true"))

        # --- NEW ARRIVALS FILTER ---
        new_arrivals = self.request.query_params.get("new_arrivals")
        if new_arrivals is not None:
            last_30_days = timezone.now() - timedelta(days=30)
            if new_arrivals.lower() == "true":
                qs = qs.filter(created_at__gte=last_30_days)
            else:
                qs = qs.exclude(created_at__gte=last_30_days)

        # --- PRICE RANGE ---
        qs = qs.annotate(
            min_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Min("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            max_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Max("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        return qs


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category endpoints:
      - list: categories with product count (for sidebar/homepage)
      - retrieve: category with products & annotated prices
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = "slug"

    def list(self, request, *args, **kwargs):
        qs = self.queryset.annotate(product_count=Count("products")).filter(product_count__gt=0)
        data = [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "image": request.build_absolute_uri(category.image.url) if category.image else None,
                "product_count": category.product_count,
            }
            for category in qs
        ]
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        category = get_object_or_404(
            Category.objects.prefetch_related(
                Prefetch(
                    "products",
                    queryset=Product.objects.prefetch_related("images").annotate(
                        min_price=Case(
                            When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                            default=Min("variants__price"),
                            output_field=DecimalField(max_digits=12, decimal_places=2),
                        ),
                        max_price=Case(
                            When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                            default=Max("variants__price"),
                            output_field=DecimalField(max_digits=12, decimal_places=2),
                        ),
                    ),
                )
            ),
            slug=kwargs["slug"],
        )
        serializer = self.get_serializer(category)
        data = serializer.data
        data["products"] = ProductListSerializer(category.products.all(), many=True, context={"request": request}).data
        return Response(data)


class FeaturedProductsAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_featured=True).annotate(
            min_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Min("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            max_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Max("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        return qs.prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.filter(is_featured=True), to_attr="featured_images")
        ).order_by("-created_at")


class NewArrivalsAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        last_30_days = timezone.now() - timedelta(days=30)
        qs = Product.objects.filter(is_active=True, created_at__gte=last_30_days).annotate(
            min_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Min("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            max_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Max("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        return qs.prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.filter(is_featured=True), to_attr="featured_images")
        ).order_by("-created_at")
