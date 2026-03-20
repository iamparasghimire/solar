from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from apps.throttles import AuthRateThrottle
from .models import Address
from .serializers import (
    AddressSerializer,
    ChangePasswordSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


# ── Authentication ────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """POST /api/auth/logout/  – blacklist the refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)


# ── Profile ───────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/profile/"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """PUT /api/auth/change-password/"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password updated.'}, status=status.HTTP_200_OK)


# ── Addresses ─────────────────────────────────

class AddressViewSet(ModelViewSet):
    """CRUD /api/auth/addresses/"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


# ── Admin Dashboard ──────────────────────────

class AdminDashboardView(APIView):
    """GET /api/auth/admin/dashboard/ – admin-only stats."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.orders.models import Order
        from apps.products.models import Product, Category
        from apps.contacts.models import ContactMessage, NewsletterSubscriber

        now = timezone.now()
        thirty_days_ago = now - timezone.timedelta(days=30)

        # Order stats
        orders_qs = Order.objects.all()
        order_stats = orders_qs.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('grand_total'),
            pending_orders=Count('id', filter=Q(status='pending')),
            delivered_orders=Count('id', filter=Q(status='delivered')),
            cancelled_orders=Count('id', filter=Q(status='cancelled')),
        )
        recent_orders = orders_qs.filter(created_at__gte=thirty_days_ago).aggregate(
            count=Count('id'),
            revenue=Sum('grand_total'),
        )

        # Product & category stats
        product_stats = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'out_of_stock': Product.objects.filter(stock=0, is_active=True).count(),
            'featured_products': Product.objects.filter(is_featured=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
        }

        # Customer stats
        customer_stats = {
            'total_customers': User.objects.filter(is_staff=False).count(),
            'new_customers_30d': User.objects.filter(
                is_staff=False, date_joined__gte=thirty_days_ago,
            ).count(),
        }

        # Support & newsletter
        support_stats = {
            'new_messages': ContactMessage.objects.filter(status='new').count(),
            'newsletter_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
        }

        return Response({
            'orders': {**order_stats, 'total_revenue': str(order_stats['total_revenue'] or 0)},
            'recent_30d': {
                'orders': recent_orders['count'] or 0,
                'revenue': str(recent_orders['revenue'] or 0),
            },
            'products': product_stats,
            'customers': customer_stats,
            'support': support_stats,
        })
