from django.urls import path
from .views import (
    RegisterView,
    ProfileView,
    ProfileUpdateView,
    MyTokenObtainPairView,
    LogoutAndBlacklistRefreshView,
    GoogleLogin,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Registration & Login
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", MyTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAndBlacklistRefreshView.as_view(), name="logout"),

    # Profile
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),

    # Google social login
    path("google/", GoogleLogin.as_view(), name="google_login"),
]
