from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Root endpoint
def root_view(request):
    return JsonResponse({"message": "Welcome to GentlemanWell API"})

# Health endpoint
def health(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_view),
    path('health/', health, name='health'),  # Healthcheck at root
    path('api/', include('products.urls')),
    path('api/', include('cart.urls')),
    path('api/', include('moments.urls')),
    path("api/auth/", include("accounts.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
