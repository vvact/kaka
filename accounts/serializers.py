from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# -------------------------
# User Serializer (Standardized)
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "date_joined", "last_login"]
        read_only_fields = ["id", "email", "date_joined", "last_login"]

# -------------------------
# Custom JWT Serializer
# -------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # attach standardized user data
        self.user_data = UserSerializer(self.user).data
        return data

# -------------------------
# Registration Serializer
# -------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name")  # Removed avatar

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user

# -------------------------
# Profile Update Serializer
# -------------------------
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "date_joined", "last_login"]
        read_only_fields = ["id", "email", "date_joined", "last_login"]
