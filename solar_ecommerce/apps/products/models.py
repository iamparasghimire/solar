from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.base import TimeStampedModel


class Category(TimeStampedModel):
    """Product category (e.g. Solar Panels, Inverters, Batteries)."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='children',
    )
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    """Solar product with key specs."""

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, default='')
    technical_description = models.TextField(blank=True, default='')

    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    # Key specs
    capacity = models.CharField(max_length=50, blank=True, default='', help_text='e.g. 540W, 5kWh')
    warranty_years = models.PositiveSmallIntegerField(default=0)
    lifespan_years = models.PositiveSmallIntegerField(default=0)

    # Inventory
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    # Delivery
    delivery_days = models.PositiveSmallIntegerField(default=7)
    installation_available = models.BooleanField(default=True)
    installation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Marketing
    is_featured = models.BooleanField(default=False, db_index=True)
    brand = models.CharField(max_length=100, blank=True, default='')
    tags = models.CharField(max_length=500, blank=True, default='', help_text='Comma-separated tags')

    class Meta(TimeStampedModel.Meta):
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        from decimal import Decimal
        return round(self.price * (1 - self.discount_percent / Decimal('100')), 2)

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def review_count(self):
        return self.reviews.count()


class ProductImage(TimeStampedModel):
    """Gallery images for a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True, default='')
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f'{self.product.name} – image {self.sort_order}'

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
