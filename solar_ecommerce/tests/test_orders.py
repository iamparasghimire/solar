"""Tests for the orders app – cart, checkout, order history, warranties."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.orders.models import Cart, Order
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


# ── Cart ──────────────────────────────────────

class TestCart:
    def test_get_cart_creates_if_missing(self):
        client, user = auth_client()
        resp = client.get('/api/orders/cart/')
        assert resp.status_code == status.HTTP_200_OK
        assert Cart.objects.filter(user=user).exists()

    def test_add_to_cart(self):
        client, user = auth_client()
        product = ProductFactory(stock=10)
        resp = client.post('/api/orders/cart/add/', {
            'product': str(product.id),
            'quantity': 2,
            'include_installation': True,
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['total_items'] == 2

    def test_add_to_cart_exceeding_stock(self):
        client, _ = auth_client()
        product = ProductFactory(stock=3)
        resp = client.post('/api/orders/cart/add/', {
            'product': str(product.id),
            'quantity': 10,
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_same_product_increments_quantity(self):
        client, user = auth_client()
        product = ProductFactory(stock=20)
        client.post('/api/orders/cart/add/', {'product': str(product.id), 'quantity': 2})
        client.post('/api/orders/cart/add/', {'product': str(product.id), 'quantity': 3})
        resp = client.get('/api/orders/cart/')
        assert resp.data['total_items'] == 5

    def test_update_cart_item(self):
        client, user = auth_client()
        cart = CartFactory(user=user)
        item = CartItemFactory(cart=cart, quantity=1)
        resp = client.patch(f'/api/orders/cart/items/{item.id}/', {'quantity': 5})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['total_items'] == 5

    def test_delete_cart_item(self):
        client, user = auth_client()
        cart = CartFactory(user=user)
        item = CartItemFactory(cart=cart)
        resp = client.delete(f'/api/orders/cart/items/{item.id}/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['total_items'] == 0

    def test_cart_unauthenticated(self):
        client = APIClient()
        resp = client.get('/api/orders/cart/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestClearCart:
    def test_clear_cart(self):
        client, user = auth_client()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart)
        CartItemFactory(cart=cart)
        resp = client.delete('/api/orders/cart/clear/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['total_items'] == 0

    def test_clear_empty_cart(self):
        client, user = auth_client()
        CartFactory(user=user)
        resp = client.delete('/api/orders/cart/clear/')
        assert resp.status_code == status.HTTP_200_OK


# ── Checkout ──────────────────────────────────

class TestCheckout:
    URL = '/api/orders/checkout/'

    def _prepare_cart(self, user):
        """Add a product to the user's cart and return address."""
        cart = CartFactory(user=user)
        product = ProductFactory(stock=10, price=1000, discount_percent=10, installation_fee=500)
        CartItemFactory(cart=cart, product=product, quantity=2, include_installation=True)
        address = AddressFactory(user=user)
        return address, product

    def test_checkout_success(self):
        client, user = auth_client()
        address, product = self._prepare_cart(user)
        resp = client.post(self.URL, {
            'address_id': str(address.id),
            'payment_method': 'cod',
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['status'] == 'pending'
        assert resp.data['order_number'].startswith('SOL-')
        # Stock should decrease
        product.refresh_from_db()
        assert product.stock == 8

    def test_checkout_empty_cart(self):
        client, user = auth_client()
        CartFactory(user=user)
        address = AddressFactory(user=user)
        resp = client.post(self.URL, {
            'address_id': str(address.id),
            'payment_method': 'upi',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_checkout_insufficient_stock(self):
        client, user = auth_client()
        cart = CartFactory(user=user)
        product = ProductFactory(stock=1)
        CartItemFactory(cart=cart, product=product, quantity=5)
        address = AddressFactory(user=user)
        resp = client.post(self.URL, {
            'address_id': str(address.id),
            'payment_method': 'card',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_checkout_invalid_address(self):
        client, user = auth_client()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart)
        resp = client.post(self.URL, {
            'address_id': '00000000-0000-0000-0000-000000000000',
            'payment_method': 'cod',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Order History ─────────────────────────────

class TestOrderHistory:

    def test_list_own_orders(self):
        client, user = auth_client()
        # Create an order via checkout
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=ProductFactory(stock=10))
        address = AddressFactory(user=user)
        client.post('/api/orders/checkout/', {
            'address_id': str(address.id),
            'payment_method': 'cod',
        })
        resp = client.get('/api/orders/list/')
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 1

    def test_cannot_see_others_orders(self):
        # user1 places order
        user1 = UserFactory()
        cart = CartFactory(user=user1)
        CartItemFactory(cart=cart, product=ProductFactory(stock=10))
        address = AddressFactory(user=user1)
        c1 = APIClient()
        c1.force_authenticate(user=user1)
        c1.post('/api/orders/checkout/', {
            'address_id': str(address.id),
            'payment_method': 'cod',
        })

        # user2 tries to list
        client, _ = auth_client()
        resp = client.get('/api/orders/list/')
        assert len(resp.data['results']) == 0


# ── Cancel Order ──────────────────────────────

class TestCancelOrder:
    def _place_order(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        cart = CartFactory(user=user)
        product = ProductFactory(stock=10, price=5000, discount_percent=0)
        CartItemFactory(cart=cart, product=product, quantity=2)
        address = AddressFactory(user=user)
        resp = client.post('/api/orders/checkout/', {
            'address_id': str(address.id),
            'payment_method': 'cod',
        })
        return client, resp.data, product

    def test_cancel_pending_order(self):
        user = UserFactory()
        client, order_data, product = self._place_order(user)
        order_id = order_data['id']

        resp = client.post(f'/api/orders/list/{order_id}/cancel/', {
            'reason': 'Changed my mind',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['status'] == 'cancelled'
        assert resp.data['cancellation_reason'] == 'Changed my mind'

        # Stock restored
        product.refresh_from_db()
        assert product.stock == 10

    def test_cannot_cancel_non_pending(self):
        user = UserFactory()
        client, order_data, _ = self._place_order(user)
        order = Order.objects.get(pk=order_data['id'])
        order.status = 'shipped'
        order.save(update_fields=['status'])

        resp = client.post(f'/api/orders/list/{order.pk}/cancel/', format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Admin Order Management ────────────────────

class TestAdminOrderManagement:
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

    def test_admin_can_list_all_orders(self):
        """Admin should see orders from all users."""
        user1 = UserFactory()
        user2 = UserFactory()
        self._place_order(user1)
        self._place_order(user2)

        admin = AdminFactory()
        client = APIClient()
        client.force_authenticate(user=admin)
        resp = client.get('/api/orders/list/')
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 2

    def test_admin_can_update_order_status(self):
        user = UserFactory()
        order_data = self._place_order(user)

        admin = AdminFactory()
        client = APIClient()
        client.force_authenticate(user=admin)
        resp = client.post(
            f'/api/orders/list/{order_data["id"]}/update-status/',
            {'status': 'confirmed'},
            format='json',
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['status'] == 'confirmed'

    def test_non_admin_cannot_update_status(self):
        user = UserFactory()
        order_data = self._place_order(user)

        client = APIClient()
        client.force_authenticate(user=user)
        resp = client.post(
            f'/api/orders/list/{order_data["id"]}/update-status/',
            {'status': 'confirmed'},
            format='json',
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_status_transition_rejected(self):
        """Cannot skip statuses, e.g. pending → delivered."""
        user = UserFactory()
        order_data = self._place_order(user)

        admin = AdminFactory()
        client = APIClient()
        client.force_authenticate(user=admin)
        resp = client.post(
            f'/api/orders/list/{order_data["id"]}/update-status/',
            {'status': 'delivered'},
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancelled_order_cannot_be_updated(self):
        user = UserFactory()
        order_data = self._place_order(user)
        order = Order.objects.get(pk=order_data['id'])
        order.status = 'cancelled'
        order.save(update_fields=['status'])

        admin = AdminFactory()
        client = APIClient()
        client.force_authenticate(user=admin)
        resp = client.post(
            f'/api/orders/list/{order.pk}/update-status/',
            {'status': 'confirmed'},
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
