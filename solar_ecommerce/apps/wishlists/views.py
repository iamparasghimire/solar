from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import WishlistItem
from .serializers import WishlistItemSerializer


class WishlistViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    GET    /api/wishlists/           – list
    POST   /api/wishlists/           – add
    DELETE /api/wishlists/<id>/      – remove
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related('product')
