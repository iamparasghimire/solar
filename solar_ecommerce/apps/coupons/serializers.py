from rest_framework import serializers
from django.utils import timezone

from .models import Coupon, CouponUsage


class CouponSerializer(serializers.ModelSerializer):
    """Full coupon serializer for admin."""
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Coupon
        fields = (
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'max_discount_amount', 'min_order_amount', 'usage_limit', 'used_count',
            'per_user_limit', 'valid_from', 'valid_until', 'is_active', 'is_valid',
        )
        read_only_fields = ('id', 'used_count')


class CouponPublicSerializer(serializers.ModelSerializer):
    """Limited coupon info for public users – hides internal usage data."""

    class Meta:
        model = Coupon
        fields = (
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'min_order_amount', 'valid_until',
        )
        read_only_fields = fields


class ApplyCouponSerializer(serializers.Serializer):
    """Validate & preview a coupon against the current cart subtotal."""

    code = serializers.CharField(max_length=30)

    def validate_code(self, value):
        code_upper = value.strip().upper()
        try:
            coupon = Coupon.objects.get(code__iexact=code_upper)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError('Coupon not found.')

        if not coupon.is_valid:
            raise serializers.ValidationError('This coupon is expired or inactive.')

        user = self.context['request'].user
        user_usage = CouponUsage.objects.filter(coupon=coupon, user=user).count()
        if user_usage >= coupon.per_user_limit:
            raise serializers.ValidationError('You have already used this coupon.')

        return coupon
