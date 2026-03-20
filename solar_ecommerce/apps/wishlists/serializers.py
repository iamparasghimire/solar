from rest_framework import serializers

from apps.products.serializers import ProductListSerializer
from .models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = WishlistItem
        fields = ('id', 'product', 'product_detail', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_product(self, value):
        user = self.context['request'].user
        if WishlistItem.objects.filter(user=user, product=value).exists():
            raise serializers.ValidationError('Product already in wishlist.')
        return value
