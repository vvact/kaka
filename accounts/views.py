from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from .serializers import (
    UserSerializer,
    ProfileSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()

# -------------------------
# Profile & Registration
# -------------------------
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Standardized response
        return Response(
            {
                "message": "User registered successfully",
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )

# -------------------------
# JWT Login (Option A)
# -------------------------
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Standardized response
        return Response(
            {
                "message": "Login successful",
                "user": getattr(serializer, "user_data", None),
                "refresh": serializer.validated_data["refresh"],
                "access": serializer.validated_data["access"],
            },
            status=status.HTTP_200_OK,
        )

class MyTokenRefreshView(TokenRefreshView):
    """Standard SimpleJWT refresh → returns new access token"""
    pass

# -------------------------
# Logout (Blacklist refresh)
# -------------------------
class LogoutAndBlacklistRefreshView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "No refresh token provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"detail": "Logged out successfully"}, status=status.HTTP_200_OK)

# -------------------------
# Google OAuth2 Login
# -------------------------
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://localhost:5173"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = getattr(self, "user", None)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name or "",
                        "last_name": user.last_name or "",
                        "date_joined": user.date_joined,
                        "last_login": user.last_login,
                    },
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Google authentication failed"},
            status=status.HTTP_400_BAD_REQUEST
        )
