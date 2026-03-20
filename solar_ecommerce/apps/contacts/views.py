from rest_framework import status, viewsets, mixins
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.throttles import ContactRateThrottle
from .models import ContactMessage, NewsletterSubscriber
from .serializers import (
    ContactMessageAdminSerializer,
    ContactMessageSerializer,
    NewsletterSerializer,
)


class ContactCreateView(APIView):
    """POST /api/contacts/ – public contact form."""
    permission_classes = [AllowAny]
    throttle_classes = [ContactRateThrottle]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Your message has been sent. We will get back to you soon.'},
            status=status.HTTP_201_CREATED,
        )


class ContactAdminViewSet(viewsets.ModelViewSet):
    """Admin CRUD for contact messages."""
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageAdminSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['status']
    search_fields = ['name', 'email', 'subject']


class NewsletterSubscribeView(APIView):
    """POST /api/contacts/newsletter/ – public email subscription."""
    permission_classes = [AllowAny]
    throttle_classes = [ContactRateThrottle]

    def post(self, request):
        serializer = NewsletterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Thank you for subscribing!'},
            status=status.HTTP_201_CREATED,
        )


class NewsletterUnsubscribeView(APIView):
    """POST /api/contacts/newsletter/unsubscribe/"""
    permission_classes = [AllowAny]
    throttle_classes = [ContactRateThrottle]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        updated = NewsletterSubscriber.objects.filter(email__iexact=email, is_active=True).update(is_active=False)
        if updated:
            return Response({'detail': 'You have been unsubscribed.'})
        return Response({'detail': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)
