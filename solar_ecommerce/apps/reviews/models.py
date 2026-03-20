from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.base import TimeStampedModel
from apps.products.models import Product


class Review(TimeStampedModel):
    """Product review – one per user per product."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True, default='')
    comment = models.TextField(blank=True, default='')

    class Meta(TimeStampedModel.Meta):
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.product.name} – {self.rating}★ by {self.user.email}'
