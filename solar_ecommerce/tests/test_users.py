"""Tests for the users app – registration, login, profile, addresses, logout."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import AddressFactory, UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


# ── helpers ───────────────────────────────────

def auth_client(user=None):
    """Return an APIClient with JWT auth for the given (or new) user."""
    client = APIClient()
    if user is None:
        user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


# ── Registration ──────────────────────────────

class TestRegister:
    URL = '/api/auth/register/'

    def test_register_success(self):
        client = APIClient()
        data = {
            'email': 'new@test.com',
            'username': 'newuser',
            'phone_number': '9999999999',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        resp = client.post(self.URL, data)
        assert resp.status_code == status.HTTP_201_CREATED
        assert 'tokens' in resp.data
        assert 'access' in resp.data['tokens']
        assert User.objects.filter(email='new@test.com').exists()

    def test_register_password_mismatch(self):
        client = APIClient()
        data = {
            'email': 'fail@test.com',
            'username': 'failuser',
            'password': 'StrongPass123!',
            'password2': 'WrongPass456!',
        }
        resp = client.post(self.URL, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self):
        UserFactory(email='dup@test.com')
        client = APIClient()
        data = {
            'email': 'dup@test.com',
            'username': 'dup2',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        resp = client.post(self.URL, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Login (JWT) ───────────────────────────────

class TestLogin:
    URL = '/api/auth/login/'

    def test_login_success(self):
        user = UserFactory()
        client = APIClient()
        resp = client.post(self.URL, {'email': user.email, 'password': 'testpass123'})
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data
        assert 'refresh' in resp.data

    def test_login_wrong_password(self):
        user = UserFactory()
        client = APIClient()
        resp = client.post(self.URL, {'email': user.email, 'password': 'wrongpass'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ── Logout ────────────────────────────────────

class TestLogout:
    URL = '/api/auth/logout/'

    def test_logout_success(self):
        user = UserFactory()
        client = APIClient()
        login_resp = client.post('/api/auth/login/', {'email': user.email, 'password': 'testpass123'})
        refresh = login_resp.data['refresh']
        client.force_authenticate(user=user)
        resp = client.post(self.URL, {'refresh': refresh})
        assert resp.status_code == status.HTTP_200_OK

    def test_logout_without_token(self):
        client, _ = auth_client()
        resp = client.post(self.URL, {})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Profile ───────────────────────────────────

class TestProfile:
    URL = '/api/auth/profile/'

    def test_get_profile(self):
        client, user = auth_client()
        resp = client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['email'] == user.email

    def test_update_profile(self):
        client, _ = auth_client()
        resp = client.patch(self.URL, {'first_name': 'Updated'})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['first_name'] == 'Updated'

    def test_unauthenticated(self):
        client = APIClient()
        resp = client.get(self.URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ── Change Password ──────────────────────────

class TestChangePassword:
    URL = '/api/auth/change-password/'

    def test_change_password_success(self):
        client, user = auth_client()
        resp = client.put(self.URL, {
            'old_password': 'testpass123',
            'new_password': 'NewStrongPass456!',
        })
        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('NewStrongPass456!')

    def test_wrong_old_password(self):
        client, _ = auth_client()
        resp = client.put(self.URL, {
            'old_password': 'wrongold',
            'new_password': 'NewStrongPass456!',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Addresses ─────────────────────────────────

class TestAddresses:
    URL = '/api/auth/addresses/'

    def test_create_address(self):
        client, _ = auth_client()
        data = {
            'label': 'Office',
            'full_name': 'Test User',
            'phone': '9876543210',
            'address_line1': '123 Solar St',
            'city': 'Delhi',
            'state': 'Delhi',
            'postal_code': '110001',
        }
        resp = client.post(self.URL, data)
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['city'] == 'Delhi'

    def test_list_own_addresses(self):
        client, user = auth_client()
        AddressFactory(user=user)
        AddressFactory(user=user, label='Office')
        resp = client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 2

    def test_cannot_see_other_users_addresses(self):
        other_user = UserFactory()
        AddressFactory(user=other_user)
        client, _ = auth_client()
        resp = client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 0
