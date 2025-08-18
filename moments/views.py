# moments/views.py
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import Moment
from .serializers import MomentSerializer

class MomentPagination(PageNumberPagination):
    page_size = 6  # Number of moments per page
    page_size_query_param = 'page_size'  # optional, allow frontend to change
    max_page_size = 20  # maximum allowed per page

class MomentListAPIView(generics.ListAPIView):
    serializer_class = MomentSerializer
    pagination_class = MomentPagination

    def get_queryset(self):
        """
        Return active moments, optionally filtering by featured.
        """
        queryset = Moment.objects.filter(is_active=True).order_by('-created_at')
        featured = self.request.query_params.get('featured')
        if featured is not None:
            if featured.lower() == 'true':
                queryset = queryset.filter(is_featured=True)
            elif featured.lower() == 'false':
                queryset = queryset.filter(is_featured=False)
        return queryset
