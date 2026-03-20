from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.permissions import IsOwner
from apps.products.models import Product

from .models import Cart, CartItem, Order, WarrantyDocument
from .serializers import (
    AddToCartSerializer,
    CancelOrderSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    UpdateCartItemSerializer,
    WarrantyDocumentSerializer,
)


# ──────────────────────────────────────────────
# Cart
# ──────────────────────────────────────────────

class CartView(APIView):
    """GET /api/orders/cart/ – retrieve current user's cart."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.prefetch_related('items__product__images').get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


class AddToCartView(APIView):
    """POST /api/orders/cart/add/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product = Product.objects.filter(pk=data['product'], is_active=True).first()
        if not product:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        if data['quantity'] > product.stock:
            return Response({'detail': 'Not enough stock.'}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={
                'quantity': data['quantity'],
                'include_installation': data['include_installation'],
            },
        )
        if not created:
            item.quantity += data['quantity']
            item.include_installation = data['include_installation']
            item.save(update_fields=['quantity', 'include_installation'])

        cart.refresh_from_db()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    """PATCH/DELETE /api/orders/cart/items/<item_id>/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        item = CartItem.objects.filter(pk=item_id, cart__user=request.user).first()
        if not item:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        item.quantity = data['quantity']
        if 'include_installation' in data:
            item.include_installation = data['include_installation']
        item.save()

        cart = item.cart
        cart.refresh_from_db()
        return Response(CartSerializer(cart).data)

    def delete(self, request, item_id):
        deleted, _ = CartItem.objects.filter(pk=item_id, cart__user=request.user).delete()
        if not deleted:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart.objects.get(user=request.user)
        return Response(CartSerializer(cart).data)


class ClearCartView(APIView):
    """DELETE /api/orders/cart/clear/ – remove all items from cart."""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            return Response(CartSerializer(cart).data)
        return Response({'detail': 'Cart is empty.'})


# ──────────────────────────────────────────────
# Checkout
# ──────────────────────────────────────────────

class CheckoutView(APIView):
    """POST /api/orders/checkout/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────
# Orders
# ──────────────────────────────────────────────

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/orders/             – list own orders (or all for admin)
    GET /api/orders/<id>/        – order detail
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.prefetch_related('items')
        if self.request.user.is_staff:
            return qs  # Admin sees all orders
        return qs.filter(user=self.request.user)

    def get_permissions(self):
        if self.action == 'update_status':
            return [IsAdminUser()]
        return super().get_permissions()

    def check_object_permissions(self, request, obj):
        """Non-admin users can only access their own orders."""
        super().check_object_permissions(request, obj)
        if not request.user.is_staff and obj.user != request.user:
            self.permission_denied(request, message='You do not have permission to access this order.')

    @action(detail=True, methods=['post'], url_path='update-status',
            permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """POST /api/orders/<id>/update-status/ (admin only)"""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']

        # Validate status transitions
        valid_transitions = {
            Order.Status.PENDING: [Order.Status.CONFIRMED, Order.Status.CANCELLED],
            Order.Status.CONFIRMED: [Order.Status.PROCESSING, Order.Status.CANCELLED],
            Order.Status.PROCESSING: [Order.Status.SHIPPED, Order.Status.CANCELLED],
            Order.Status.SHIPPED: [Order.Status.DELIVERED],
            Order.Status.DELIVERED: [],
            Order.Status.CANCELLED: [],
        }
        allowed = valid_transitions.get(order.status, [])
        if new_status not in allowed:
            return Response(
                {'detail': f'Cannot transition from "{order.status}" to "{new_status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        if new_status == Order.Status.CANCELLED:
            order.cancelled_at = timezone.now()
        order.save(update_fields=['status', 'cancelled_at'] if new_status == Order.Status.CANCELLED else ['status'])
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """POST /api/orders/<id>/cancel/ – user cancels pending order."""
        order = self.get_object()

        # Non-admin can only cancel their own orders
        if not request.user.is_staff and order.user != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)

        if order.status != Order.Status.PENDING:
            return Response(
                {'detail': 'Only pending orders can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Restore stock atomically
            for item in order.items.select_related('product'):
                Product.objects.filter(pk=item.product_id).update(
                    stock=F('stock') + item.quantity,
                )

            order.status = Order.Status.CANCELLED
            order.cancelled_at = timezone.now()
            order.cancellation_reason = serializer.validated_data.get('reason', '')
            order.save(update_fields=['status', 'cancelled_at', 'cancellation_reason'])

        return Response(OrderSerializer(order).data)


# ──────────────────────────────────────────────
# Warranty Documents
# ──────────────────────────────────────────────

class WarrantyDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/orders/warranties/ – user's warranty docs."""
    serializer_class = WarrantyDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WarrantyDocument.objects.filter(
            order_item__order__user=self.request.user,
        ).select_related('order_item')
