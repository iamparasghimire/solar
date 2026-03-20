from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Cart
from apps.permissions import IsAdminOrReadOnly

from .models import Coupon
from .serializers import ApplyCouponSerializer, CouponPublicSerializer, CouponSerializer


class CouponViewSet(viewsets.ModelViewSet):
    """Admin CRUD for coupons. Public can only list active ones with limited info."""

    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'code'

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return CouponSerializer
        return CouponPublicSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Coupon.objects.all()
        return Coupon.objects.filter(is_active=True)


class ApplyCouponView(APIView):
    """POST /api/coupons/apply/ – preview discount for current cart."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        coupon = serializer.validated_data['code']
        cart = Cart.objects.prefetch_related('items__product').filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = cart.subtotal
        discount = coupon.calculate_discount(subtotal)

        if discount == 0:
            return Response(
                {'detail': f'Minimum order amount is ₹{coupon.min_order_amount}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'coupon': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'discount_amount': str(discount),
            'subtotal_before': str(subtotal),
            'subtotal_after': str(subtotal - discount),
        })
