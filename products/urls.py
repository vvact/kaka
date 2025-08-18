# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, VariantViewSet
from .views import FeaturedProductsAPIView, NewArrivalsAPIView  # import new views

router = DefaultRouter()
router.register(r"variants", VariantViewSet, basename="variant")
router.register(r'categories', CategoryViewSet, basename='categories')

# Product list and detail views (slug-based)
product_list = ProductViewSet.as_view({
    "get": "list"
})
product_detail = ProductViewSet.as_view({
    "get": "retrieve"
})

urlpatterns = [
    # Featured products
    path("products/featured/", FeaturedProductsAPIView.as_view(), name="featured-products"),

    # New arrivals
    path("products/new-arrivals/", NewArrivalsAPIView.as_view(), name="new-arrivals"),

    # Lightweight product list
    path("products/", product_list, name="product-list"),

    # Product detail by slug (catch-all)
    path("products/<slug:slug>/", product_detail, name="product-detail"),

    # Include variant routes and categories
    path("", include(router.urls)),
]

