from rest_framework import viewsets, parsers, filters, status as http_status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.permissions import IsAdminOrReadOnly

from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductListSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    GET  /api/products/categories/          – list (public)
    POST /api/products/categories/          – create (admin)
    GET  /api/products/categories/<id>/     – detail (public)
    """
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    search_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    GET  /api/products/                     – list (public)
    POST /api/products/                     – create (admin)
    GET  /api/products/<slug>/              – detail (public)
    """
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'is_active', 'installation_available', 'is_featured', 'brand']
    search_fields = ['name', 'sku', 'description', 'capacity', 'brand', 'tags']
    ordering_fields = ['price', 'created_at', 'warranty_years', 'discount_percent']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Product.objects.select_related('category').prefetch_related('images')
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    # ── Upload images for a product ───────
    @action(
        detail=True, methods=['post'],
        permission_classes=[IsAdminUser],
        parser_classes=[parsers.MultiPartParser],
        url_path='upload-image',
    )
    def upload_image(self, request, slug=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=201)

    # ── Featured products ─────────────────
    @action(detail=False, methods=['get'], url_path='featured', permission_classes=[AllowAny])
    def featured(self, request):
        """GET /api/products/featured/ – curated featured products."""
        qs = Product.objects.filter(is_active=True, is_featured=True).select_related('category').prefetch_related('images')[:12]
        return Response(ProductListSerializer(qs, many=True, context={'request': request}).data)

    # ── Related products ──────────────────
    @action(detail=True, methods=['get'], url_path='related', permission_classes=[AllowAny])
    def related(self, request, slug=None):
        """GET /api/products/<slug>/related/ – same-category products."""
        product = self.get_object()
        qs = (
            Product.objects.filter(category=product.category, is_active=True)
            .exclude(pk=product.pk)
            .select_related('category')
            .prefetch_related('images')[:6]
        )
        return Response(ProductListSerializer(qs, many=True, context={'request': request}).data)
