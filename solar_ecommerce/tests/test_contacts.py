"""Tests for contacts app – contact form, newsletter."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.contacts.models import ContactMessage, NewsletterSubscriber
from tests.factories import (
    AdminFactory,
    ContactMessageFactory,
    NewsletterSubscriberFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


def auth_client(user=None):
    client = APIClient()
    if user is None:
        user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


def admin_client():
    client = APIClient()
    admin = AdminFactory()
    client.force_authenticate(user=admin)
    return client, admin


# ── Contact Form ─────────────────────────────

class TestContactForm:
    def test_submit_contact_form(self):
        client = APIClient()
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '9876543210',
            'subject': 'Solar Panel Enquiry',
            'message': 'I want to install solar panels on my roof.',
        }
        resp = client.post('/api/contacts/', data, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert ContactMessage.objects.count() == 1

    def test_contact_form_missing_fields(self):
        client = APIClient()
        resp = client.post('/api/contacts/', {'name': 'John'}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_list_messages(self):
        ContactMessageFactory()
        ContactMessageFactory()
        client, _ = admin_client()
        resp = client.get('/api/contacts/admin/messages/')
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 2

    def test_admin_can_update_status(self):
        msg = ContactMessageFactory()
        client, _ = admin_client()
        resp = client.patch(f'/api/contacts/admin/messages/{msg.pk}/', {
            'status': 'resolved',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        msg.refresh_from_db()
        assert msg.status == 'resolved'

    def test_non_admin_cannot_list_messages(self):
        client, _ = auth_client()
        resp = client.get('/api/contacts/admin/messages/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# ── Newsletter ───────────────────────────────

class TestNewsletter:
    def test_subscribe(self):
        client = APIClient()
        resp = client.post('/api/contacts/newsletter/', {
            'email': 'sub@example.com',
        }, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert NewsletterSubscriber.objects.filter(email='sub@example.com').exists()

    def test_subscribe_duplicate_reactivates(self):
        sub = NewsletterSubscriberFactory(email='dup@test.com', is_active=False)
        client = APIClient()
        resp = client.post('/api/contacts/newsletter/', {
            'email': 'dup@test.com',
        }, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        sub.refresh_from_db()
        assert sub.is_active is True

    def test_unsubscribe(self):
        NewsletterSubscriberFactory(email='unsub@test.com')
        client = APIClient()
        resp = client.post('/api/contacts/newsletter/unsubscribe/', {
            'email': 'unsub@test.com',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        sub = NewsletterSubscriber.objects.get(email='unsub@test.com')
        assert sub.is_active is False

    def test_unsubscribe_nonexistent(self):
        client = APIClient()
        resp = client.post('/api/contacts/newsletter/unsubscribe/', {
            'email': 'ghost@test.com',
        }, format='json')
        assert resp.status_code == status.HTTP_404_NOT_FOUND
