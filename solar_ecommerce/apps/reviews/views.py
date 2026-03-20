from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.permissions import IsOwnerOrReadOnly

from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    GET    /api/reviews/?product=<uuid>   – list reviews
    POST   /api/reviews/                  – create
    PATCH  /api/reviews/<id>/             – update own
    DELETE /api/reviews/<id>/             – delete own
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ['product']

    def get_queryset(self):
        return Review.objects.select_related('user', 'product')
