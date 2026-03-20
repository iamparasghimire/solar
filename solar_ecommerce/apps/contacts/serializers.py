from rest_framework import serializers

from .models import ContactMessage, NewsletterSubscriber


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('id', 'name', 'email', 'phone', 'subject', 'message', 'status', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')


class ContactMessageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('id', 'name', 'email', 'phone', 'subject', 'message',
                  'status', 'admin_notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class NewsletterSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        """Reactivate if previously unsubscribed, else create."""
        sub, created = NewsletterSubscriber.objects.get_or_create(
            email=validated_data['email'],
            defaults={'is_active': True},
        )
        if not created and not sub.is_active:
            sub.is_active = True
            sub.save(update_fields=['is_active'])
        return sub
