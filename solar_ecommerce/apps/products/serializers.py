from django.conf import settings
from rest_framework import serializers

from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 'parent', 'children', 'is_active')
        read_only_fields = ('id',)

    def get_children(self, obj):
        qs = obj.children.filter(is_active=True)
        return CategorySerializer(qs, many=True).data if qs.exists() else []


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'sort_order')
        read_only_fields = ('id',)

    def validate_image(self, value):
        """Validate image file type and size."""
        max_size = getattr(settings, 'MAX_IMAGE_UPLOAD_SIZE', 5 * 1024 * 1024)
        allowed_types = getattr(settings, 'ALLOWED_IMAGE_TYPES', ['image/jpeg', 'image/png', 'image/webp'])

        if value.size > max_size:
            raise serializers.ValidationError(f'Image size cannot exceed {max_size // (1024 * 1024)} MB.')
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f'Unsupported image type "{value.content_type}". Allowed: {", ".join(allowed_types)}'
            )
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list / search pages."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    discounted_price = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'category', 'category_name',
            'price', 'discount_percent', 'discounted_price',
            'capacity', 'warranty_years', 'brand', 'is_featured',
            'primary_image', 'average_rating', 'review_count',
            'in_stock', 'is_active',
        )

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for the product detail page."""

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True,
    )
    images = ProductImageSerializer(many=True, read_only=True)
    discounted_price = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'category', 'category_id',
            'description', 'technical_description',
            'price', 'discount_percent', 'discounted_price',
            'capacity', 'warranty_years', 'lifespan_years',
            'stock', 'in_stock', 'is_active',
            'delivery_days', 'installation_available', 'installation_fee',
            'brand', 'tags', 'is_featured',
            'images', 'average_rating', 'review_count',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
