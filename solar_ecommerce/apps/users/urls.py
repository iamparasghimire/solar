from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.throttles import AuthRateThrottle
from . import views

router = DefaultRouter()
router.register('addresses', views.AddressViewSet, basename='address')


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """Login endpoint with strict rate limiting to prevent brute-force attacks."""
    throttle_classes = [AuthRateThrottle]


class ThrottledTokenRefreshView(TokenRefreshView):
    """Token refresh with rate limiting."""
    throttle_classes = [AuthRateThrottle]


urlpatterns = [
    # JWT tokens (rate-limited)
    path('login/', ThrottledTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', ThrottledTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Registration & profile
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # Admin dashboard
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),

    # Addresses
    path('', include(router.urls)),
]
