# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, VariantViewSet

router = DefaultRouter()
router.register(r"variants", VariantViewSet, basename="variant")

router.register(r'categories', CategoryViewSet, basename='categories')

# We’ll use a custom route for slug-based product detail
product_list = ProductViewSet.as_view({
    "get": "list"
})
product_detail = ProductViewSet.as_view({
    "get": "retrieve"
})

urlpatterns = [
    # Lightweight product list
    path("products/", product_list, name="product-list"),

    # Product detail by slug
    path("products/<slug:slug>/", product_detail, name="product-detail"),

    # Include variant routes if needed
    path("", include(router.urls)),
]
