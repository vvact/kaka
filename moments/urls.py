# moments/urls.py
from django.urls import path
from .views import MomentListAPIView

urlpatterns = [
    path("moments/", MomentListAPIView.as_view(), name="moment-list"),
]
