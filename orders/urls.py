# orders/urls.py
from django.urls import path
from .views import CheckoutView, OrderListView, OrderDetailView

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list"),             # GET -> list orders
    path("checkout/", CheckoutView.as_view(), name="checkout"),       # POST -> create order (checkout)
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),# GET -> order details
]
