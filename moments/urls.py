# moments/urls.py
from django.urls import path
from .views import MomentListAPIView, health

urlpatterns = [
    path("moments/", MomentListAPIView.as_view(), name="moment-list"),
    path("health/", health, name="health"),
]
