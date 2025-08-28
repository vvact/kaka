from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer,
    ProfileSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

from datetime import timedelta

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


# -------------------------
# JWT Authentication (Cookie-based Refresh Rotation)
# -------------------------
COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/api/auth/token/refresh/"


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access = serializer.validated_data.get("access")
        refresh = serializer.validated_data.get("refresh")

        response_data = {
            "access": access,
            "user": getattr(serializer, "user_data", None),
        }
        response = Response(response_data, status=status.HTTP_200_OK)

        response.set_cookie(
            key=COOKIE_NAME,
            value=refresh,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path=COOKIE_PATH,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )
        return response


class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        if "refresh" not in request.data and COOKIE_NAME in request.COOKIES:
            request_data = request.data.copy()
            request_data["refresh"] = request.COOKIES.get(COOKIE_NAME)
            request._full_data = request_data

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200 and "refresh" in response.data:
            new_refresh = response.data["refresh"]
            response.set_cookie(
                key=COOKIE_NAME,
                value=new_refresh,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path=COOKIE_PATH,
                max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            )
            del response.data["refresh"]

        return response


class LogoutAndBlacklistRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh") or request.COOKIES.get(COOKIE_NAME)
        if not refresh_token:
            return Response({"detail": "No refresh token provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({"detail": "Logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH)
        return response


# -------------------------
# Google Social Login
# -------------------------
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def get_response(self):
        """Return JWT tokens + set refresh cookie"""
        user = self.user

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response_data = {
            "access": str(access),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }

        response = Response(response_data, status=status.HTTP_200_OK)

        # Set HttpOnly cookie for refresh token
        response.set_cookie(
            key=COOKIE_NAME,
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path=COOKIE_PATH,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )

        return response
