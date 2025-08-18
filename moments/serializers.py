# moments/serializers.py
from rest_framework import serializers
from .models import Moment

class MomentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Moment
        fields = ["id", "caption", "image_url", "link", "is_featured", "created_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
