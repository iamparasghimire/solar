"""
Security-focused tests – verifies permissions, rate limiting,
IDOR protection, and other security controls.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.orders.models import Order
from tests.factories import (
    AddressFactory,
    AdminFactory,
    CartFactory,
    CartItemFactory,
    ProductFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


def auth_client(user=None):
    client = APIClient()
    if user is None:
        user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


# ── Upload Permission Tests ──────────────────

class TestUploadSecurity:
    def test_non_admin_cannot_upload_product_image(self):
        """Regular authenticated user should NOT be able to upload product images."""
        product = ProductFactory(slug='test-upload')
        client, _ = auth_client()
        resp = client.post(f'/api/products/{product.slug}/upload-image/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_upload_product_image(self):
        product = ProductFactory(slug='test-upload-anon')
        client = APIClient()
        resp = client.post(f'/api/products/{product.slug}/upload-image/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ── Order IDOR Tests ─────────────────────────

class TestOrderIDOR:
    def _place_order(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        cart = CartFactory(user=user)
        product = ProductFactory(stock=10, price=5000, discount_percent=0)
        CartItemFactory(cart=cart, product=product, quantity=1)
        address = AddressFactory(user=user)
        resp = client.post('/api/orders/checkout/', {
            'address_id': str(address.id),
            'payment_method': 'cod',
        })
        return resp.data

    def test_user_cannot_view_other_users_order(self):
        """User A should not be able to access User B's order detail."""
        user_a = UserFactory()
        user_b = UserFactory()
        order_data = self._place_order(user_a)

        client = APIClient()
        client.force_authenticate(user=user_b)
        resp = client.get(f'/api/orders/list/{order_data["id"]}/')
        assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_cancel_other_users_order(self):
        """User A should not be able to cancel User B's order."""
        user_a = UserFactory()
        user_b = UserFactory()
        order_data = self._place_order(user_a)

        client = APIClient()
        client.force_authenticate(user=user_b)
        resp = client.post(f'/api/orders/list/{order_data["id"]}/cancel/', format='json')
        assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)


# ── Address IDOR Tests ───────────────────────

class TestAddressIDOR:
    def test_cannot_checkout_with_other_users_address(self):
        """User should not be able to use another user's address for checkout."""
        user_a = UserFactory()
        user_b = UserFactory()
        address = AddressFactory(user=user_a)

        client = APIClient()
        client.force_authenticate(user=user_b)
        cart = CartFactory(user=user_b)
        CartItemFactory(cart=cart, product=ProductFactory(stock=10))

        resp = client.post('/api/orders/checkout/', {
            'address_id': str(address.id),
            'payment_method': 'cod',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_see_other_users_addresses(self):
        user_a = UserFactory()
        AddressFactory(user=user_a)
        client, _ = auth_client()
        resp = client.get('/api/auth/addresses/')
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 0


# ── Cart IDOR Tests ──────────────────────────

class TestCartIDOR:
    def test_cannot_update_other_users_cart_item(self):
        user_a = UserFactory()
        cart = CartFactory(user=user_a)
        item = CartItemFactory(cart=cart)

        client, _ = auth_client()  # different user
        resp = client.patch(f'/api/orders/cart/items/{item.id}/', {'quantity': 99})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_delete_other_users_cart_item(self):
        user_a = UserFactory()
        cart = CartFactory(user=user_a)
        item = CartItemFactory(cart=cart)

        client, _ = auth_client()  # different user
        resp = client.delete(f'/api/orders/cart/items/{item.id}/')
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ── Admin Endpoint Protection ────────────────

class TestAdminProtection:
    def test_non_admin_cannot_access_dashboard(self):
        client, _ = auth_client()
        resp = client.get('/api/auth/admin/dashboard/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_non_admin_cannot_access_contact_messages(self):
        client, _ = auth_client()
        resp = client.get('/api/contacts/admin/messages/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_non_admin_cannot_create_product(self):
        client, _ = auth_client()
        resp = client.post('/api/products/', {'name': 'Hack Product'})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_non_admin_cannot_create_category(self):
        client, _ = auth_client()
        resp = client.post('/api/products/categories/', {
            'name': 'Hack Category',
            'slug': 'hack-cat',
        })
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_non_admin_cannot_create_coupon(self):
        client, _ = auth_client()
        resp = client.post('/api/coupons/', {
            'code': 'HACK',
            'discount_type': 'percentage',
            'discount_value': '100',
        }, format='json')
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# ── Authentication Required Tests ────────────

class TestAuthRequired:
    """Verify that protected endpoints require authentication."""

    PROTECTED_ENDPOINTS = [
        ('GET', '/api/orders/cart/'),
        ('POST', '/api/orders/cart/add/'),
        ('POST', '/api/orders/checkout/'),
        ('GET', '/api/orders/list/'),
        ('GET', '/api/wishlists/'),
        ('GET', '/api/auth/profile/'),
        ('POST', '/api/coupons/apply/'),
    ]

    @pytest.mark.parametrize('method,url', PROTECTED_ENDPOINTS)
    def test_unauthenticated_is_rejected(self, method, url):
        client = APIClient()
        resp = getattr(client, method.lower())(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
