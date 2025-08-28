from django.urls import path, include
from .views import (
    ProfileUpdateView,
    ProfileView,
    RegisterView,
    MyTokenObtainPairView,
    MyTokenRefreshView,
    LogoutAndBlacklistRefreshView,
    GoogleLogin
)

urlpatterns = [
    # Auth endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAndBlacklistRefreshView.as_view(), name="logout"),

    # Profile
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),

    # Google social login
    path("google/", GoogleLogin.as_view(), name="google_login"),

    # Optional: include default allauth URLs if needed for other social flows
    path("social/", include("allauth.socialaccount.urls")),
]
