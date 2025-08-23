from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def root_view(request):
    return JsonResponse({"message": "Welcome to GentlemanWell API"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_view),
    path('api/', include('products.urls')),  # or whatever your app is called
    path('api/', include('cart.urls')),  # Include cart URLs
    path('api/', include('moments.urls')),  # Include moments URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
