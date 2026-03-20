from django.conf import settings
from django.db import models

from apps.base import TimeStampedModel
from apps.products.models import Product


class WishlistItem(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='+')

    class Meta(TimeStampedModel.Meta):
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.email} ♥ {self.product.name}'
