from rest_framework import serializers
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.products.serializers import ProductListSerializer
from apps.products.models import Product
from apps.users.models import Address
from apps.coupons.models import Coupon, CouponUsage
from .models import Cart, CartItem, Order, OrderItem, WarrantyDocument


# ──────────────────────────────────────────────
# Cart
# ──────────────────────────────────────────────

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    unit_price = serializers.ReadOnlyField()
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_detail', 'quantity',
                  'include_installation', 'unit_price', 'line_total')
        read_only_fields = ('id',)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    installation_total = serializers.ReadOnlyField()
    grand_total = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'subtotal',
                  'installation_total', 'grand_total', 'updated_at')
        read_only_fields = ('id', 'updated_at')


class AddToCartSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    include_installation = serializers.BooleanField(default=False)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    include_installation = serializers.BooleanField(required=False)


# ──────────────────────────────────────────────
# Order
# ──────────────────────────────────────────────

class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'sku', 'unit_price',
                  'quantity', 'include_installation', 'installation_fee', 'line_total')
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'status', 'payment_method',
            'shipping_full_name', 'shipping_phone', 'shipping_address',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
            'subtotal', 'installation_total', 'discount_amount', 'coupon_code', 'grand_total',
            'payment_status', 'payment_id', 'paid_at',
            'cancelled_at', 'cancellation_reason',
            'note', 'items', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'order_number', 'status',
            'subtotal', 'installation_total', 'discount_amount', 'coupon_code', 'grand_total',
            'payment_status', 'payment_id', 'paid_at',
            'cancelled_at', 'cancellation_reason',
            'created_at', 'updated_at',
        )


class CheckoutSerializer(serializers.Serializer):
    """Validates checkout payload and creates the order atomically."""

    address_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    coupon_code = serializers.CharField(required=False, default='', allow_blank=True)
    note = serializers.CharField(required=False, default='', allow_blank=True)

    def validate_address_id(self, value):
        user = self.context['request'].user
        try:
            return Address.objects.get(pk=value, user=user)
        except Address.DoesNotExist:
            raise serializers.ValidationError('Address not found.')

    def _resolve_coupon(self, code, user):
        """Validate coupon if provided. Returns (Coupon, None) or (None, error_msg)."""
        if not code:
            return None, None
        try:
            coupon = Coupon.objects.get(code__iexact=code.strip())
        except Coupon.DoesNotExist:
            return None, 'Coupon not found.'
        if not coupon.is_valid:
            return None, 'This coupon is expired or inactive.'
        usage = CouponUsage.objects.filter(coupon=coupon, user=user).count()
        if usage >= coupon.per_user_limit:
            return None, 'You have already used this coupon.'
        return coupon, None

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        address = validated_data['address_id']  # resolved in validate
        cart = Cart.objects.prefetch_related('items__product').get(user=user)

        if not cart.items.exists():
            raise serializers.ValidationError({'cart': 'Cart is empty.'})

        # Check stock
        for ci in cart.items.all():
            if ci.quantity > ci.product.stock:
                raise serializers.ValidationError(
                    {'stock': f'"{ci.product.name}" only has {ci.product.stock} in stock.'}
                )

        # Resolve coupon
        coupon, coupon_err = self._resolve_coupon(
            validated_data.get('coupon_code', ''), user,
        )
        if coupon_err:
            raise serializers.ValidationError({'coupon_code': coupon_err})

        subtotal = cart.subtotal
        installation_total = cart.installation_total
        discount_amount = coupon.calculate_discount(subtotal) if coupon else 0
        grand_total = subtotal + installation_total - discount_amount

        order = Order.objects.create(
            user=user,
            payment_method=validated_data['payment_method'],
            note=validated_data.get('note', ''),
            coupon_code=coupon.code if coupon else '',
            shipping_full_name=address.full_name,
            shipping_phone=address.phone,
            shipping_address=f'{address.address_line1}\n{address.address_line2}'.strip(),
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_postal_code=address.postal_code,
            shipping_country=address.country,
            subtotal=subtotal,
            installation_total=installation_total,
            discount_amount=discount_amount,
            grand_total=grand_total,
        )

        order_items = []
        for ci in cart.items.select_related('product'):
            order_items.append(OrderItem(
                order=order,
                product=ci.product,
                product_name=ci.product.name,
                sku=ci.product.sku,
                unit_price=ci.product.discounted_price,
                quantity=ci.quantity,
                include_installation=ci.include_installation,
                installation_fee=ci.product.installation_fee if ci.include_installation else 0,
            ))
            # Atomic stock decrement – prevents race conditions
            Product.objects.filter(pk=ci.product.pk).update(
                stock=F('stock') - ci.quantity,
            )

        OrderItem.objects.bulk_create(order_items)

        # Record coupon usage atomically
        if coupon:
            CouponUsage.objects.create(coupon=coupon, user=user, order=order)
            Coupon.objects.filter(pk=coupon.pk).update(
                used_count=F('used_count') + 1,
            )

        cart.items.all().delete()
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, default='', allow_blank=True)


class WarrantyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyDocument
        fields = ('id', 'order_item', 'title', 'file', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_file(self, value):
        """Validate warranty document file type and size."""
        max_size = getattr(settings, 'MAX_DOCUMENT_UPLOAD_SIZE', 10 * 1024 * 1024)
        allowed_types = getattr(settings, 'ALLOWED_DOCUMENT_TYPES', ['application/pdf'])

        if value.size > max_size:
            raise serializers.ValidationError(f'File size cannot exceed {max_size // (1024 * 1024)} MB.')
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f'Unsupported file type "{value.content_type}". Only PDF is allowed.'
            )
        return value
