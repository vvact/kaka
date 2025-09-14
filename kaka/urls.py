from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# SimpleJWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Root endpoint
def root_view(request):
    return JsonResponse({"message": "Welcome to GentlemanWell API"})

# Health endpoint
def health(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    # --- Admin ---
    path("admin/", include("dashboard.urls")),
    path("admin/", admin.site.urls),

    # --- Root / Health ---
    path("", root_view),
    path("health/", health, name="health"),

    # --- JWT Auth (Option A) ---
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # --- App Routes ---
    path("api/", include("products.urls")),
    path("api/", include("cart.urls")),
    path("api/", include("moments.urls")),
    path("api/accounts/", include("accounts.urls")),  # registration & profile
    path("api/orders/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
