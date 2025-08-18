from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch, Min, Max, Q, Case, When, DecimalField, F, Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.db.models import Min, Max, Case, When, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import Prefetch
from rest_framework import generics
from .models import Product, ProductImage
from .serializers import ProductListSerializer
from django.db.models import Min, Max, Case, When, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import generics
from .models import Product
from .serializers import ProductListSerializer
from .models import Product, ProductImage, Variant, Category
from .serializers import ProductSerializer, ProductListSerializer, VariantSerializer, CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Full Product endpoints:
      - list: lightweight ProductListSerializer
      - retrieve: full ProductSerializer
      - slug used for retrieve
    """
    lookup_field = "slug"
    variant_qs = Variant.objects.prefetch_related("attributes__attribute", "image")
    queryset = Product.objects.select_related("category").prefetch_related(
        "images",
        Prefetch("variants", queryset=variant_qs, to_attr="_prefetched_variants")
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = self.queryset
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(slug__icontains=search))

        qs = qs.annotate(
            min_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Min("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            max_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Max("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
        return qs

    @action(detail=True, methods=["post"])
    def variant_lookup(self, request, slug=None):
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
            "in_stock": bool(match.is_active and match.stock > 0)
        })


class VariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only Variant endpoints.
    """
    serializer_class = VariantSerializer
    queryset = Variant.objects.prefetch_related("attributes__attribute", "image").select_related("product")



class ProductListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductListSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        qs = self.queryset
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(slug__icontains=search))

        # --- FEATURED FILTER ---
        featured = self.request.query_params.get("featured")
        if featured is not None:
            if featured.lower() == 'true':
                qs = qs.filter(is_featured=True)
            elif featured.lower() == 'false':
                qs = qs.filter(is_featured=False)

        # --- NEW ARRIVALS FILTER ---
        new_arrivals = self.request.query_params.get("new_arrivals")
        if new_arrivals is not None:
            last_30_days = timezone.now() - timedelta(days=30)
            if new_arrivals.lower() == 'true':
                qs = qs.filter(created_at__gte=last_30_days)
            elif new_arrivals.lower() == 'false':
                qs = qs.exclude(created_at__gte=last_30_days)

        # Annotate min/max price if needed
        qs = qs.annotate(
            min_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Min("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            max_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Max("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )

        return qs.prefetch_related("images")



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category endpoints:
      - list: categories with product count (for sidebar/homepage)
      - retrieve: category with all products and annotated prices
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'

    def list(self, request, *args, **kwargs):
        """
        Return all categories with product count for sidebar/homepage.
        """
        qs = self.queryset.annotate(product_count=Count('products')).filter(product_count__gt=0)
        data = [
            {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'image': request.build_absolute_uri(category.image.url) if category.image else None,
                'product_count': category.product_count
            }
            for category in qs
        ]
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """
        Return a single category with all products (including annotated min/max price and images)
        """
        category = get_object_or_404(
            Category.objects.prefetch_related(
                Prefetch(
                    "products",
                    queryset=Product.objects.prefetch_related('images').annotate(
                        min_price=Case(
                            When(has_variants=False, then=Coalesce('discount_price', 'base_price')),
                            default=Min('variants__price'),
                            output_field=DecimalField(max_digits=12, decimal_places=2)
                        ),
                        max_price=Case(
                            When(has_variants=False, then=Coalesce('discount_price', 'base_price')),
                            default=Max('variants__price'),
                            output_field=DecimalField(max_digits=12, decimal_places=2)
                        )
                    )
                )
            ),
            slug=kwargs['slug']
        )

        serializer = self.get_serializer(category)
        data = serializer.data
        data['products'] = ProductListSerializer(category.products.all(), many=True, context={'request': request}).data
        return Response(data)





class FeaturedProductsAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_featured=True)

        # Annotate min_price and max_price (required by serializer)
        qs = qs.annotate(
            min_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Min("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            max_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Max("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )

        # Prefetch featured images
        qs = qs.prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_featured=True),
                to_attr='featured_images'
            )
        ).order_by('-created_at')

        return qs

    

class NewArrivalsAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        last_30_days = timezone.now() - timedelta(days=30)
        return Product.objects.filter(created_at__gte=last_30_days, is_active=True).prefetch_related('images').order_by('-created_at')
    




class NewArrivalsAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        last_30_days = timezone.now() - timedelta(days=30)
        qs = Product.objects.filter(is_active=True, created_at__gte=last_30_days)

        # Annotate min_price and max_price (required by serializer)
        qs = qs.annotate(
            min_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Min("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            max_price=Case(
                When(has_variants=False, then=Coalesce("discount_price", "base_price")),
                default=Max("variants__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )

        # Prefetch featured images
        qs = qs.prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_featured=True),
                to_attr='featured_images'
            )
        ).order_by('-created_at')

        return qs
