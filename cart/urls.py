from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, MergeCartView  # 👈 import MergeCartView

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/merge/', MergeCartView.as_view(), name='cart-merge'),  # 👈 merge guest cart
]
