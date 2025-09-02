# dashboard/urls.py
from django.urls import path
from .views import custom_dashboard

urlpatterns = [
    path('dashboard/', custom_dashboard, name='admin-dashboard'),
]
