"""Tests for the coupons app – CRUD, apply, checkout integration."""

import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.coupons.models import Coupon, CouponUsage
from apps.orders.models import Cart, Order
from tests.factories import (
    AddressFactory,
    AdminFactory,
    CartFactory,
    CartItemFactory,
    CouponFactory,
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


def admin_client():
    client = APIClient()
    admin = AdminFactory()
    client.force_authenticate(user=admin)
    return client, admin


# ── Coupon CRUD (admin) ──────────────────────

class TestCouponCRUD:
    def test_admin_can_create_coupon(self):
        client, _ = admin_client()
        data = {
            'code': 'SUMMER20',
            'discount_type': 'percentage',
            'discount_value': '20.00',
            'valid_from': timezone.now().isoformat(),
            'valid_until': (timezone.now() + timedelta(days=30)).isoformat(),
        }
        resp = client.post('/api/coupons/', data, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['code'] == 'SUMMER20'

    def test_non_admin_cannot_create_coupon(self):
        client, _ = auth_client()
        data = {
            'code': 'FAIL',
            'discount_type': 'percentage',
            'discount_value': '10.00',
            'valid_from': timezone.now().isoformat(),
            'valid_until': (timezone.now() + timedelta(days=30)).isoformat(),
        }
        resp = client.post('/api/coupons/', data, format='json')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_list_coupons_public(self):
        CouponFactory(is_active=True)
        CouponFactory(is_active=False)
        client, _ = auth_client()
        resp = client.get('/api/coupons/')
        # Normal users only see active
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 1

    def test_admin_sees_all_coupons(self):
        CouponFactory(is_active=True)
        CouponFactory(is_active=False)
        client, _ = admin_client()
        resp = client.get('/api/coupons/')
        assert len(resp.data['results']) == 2


# ── Apply Coupon (preview) ───────────────────

class TestApplyCoupon:
    def test_apply_valid_coupon(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        product = ProductFactory(price=Decimal('10000'), discount_percent=0)
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=2)
        coupon = CouponFactory(discount_value=10)  # 10%

        resp = client.post('/api/coupons/apply/', {'code': coupon.code}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert 'discount_amount' in resp.data

    def test_apply_expired_coupon(self):
        client, _ = auth_client()
        coupon = CouponFactory(valid_until=timezone.now() - timedelta(days=1))
        resp = client.post('/api/coupons/apply/', {'code': coupon.code}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_apply_nonexistent_coupon(self):
        client, _ = auth_client()
        resp = client.post('/api/coupons/apply/', {'code': 'DOESNOTEXIST'}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_apply_coupon_empty_cart(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        CartFactory(user=user)
        coupon = CouponFactory()
        resp = client.post('/api/coupons/apply/', {'code': coupon.code}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Coupon model logic ────────────────────────

class TestCouponModel:
    def test_percentage_discount(self):
        coupon = CouponFactory(discount_type='percentage', discount_value=15)
        assert coupon.calculate_discount(Decimal('10000')) == Decimal('1500')

    def test_fixed_discount(self):
        coupon = CouponFactory(discount_type='fixed', discount_value=500)
        assert coupon.calculate_discount(Decimal('10000')) == Decimal('500')

    def test_max_discount_cap(self):
        coupon = CouponFactory(
            discount_type='percentage', discount_value=50,
            max_discount_amount=Decimal('2000'),
        )
        assert coupon.calculate_discount(Decimal('10000')) == Decimal('2000')

    def test_min_order_amount(self):
        coupon = CouponFactory(discount_value=10, min_order_amount=Decimal('5000'))
        assert coupon.calculate_discount(Decimal('3000')) == Decimal('0')

    def test_is_valid_active(self):
        coupon = CouponFactory()
        assert coupon.is_valid is True

    def test_is_valid_expired(self):
        coupon = CouponFactory(valid_until=timezone.now() - timedelta(hours=1))
        assert coupon.is_valid is False

    def test_is_valid_usage_exhausted(self):
        coupon = CouponFactory(usage_limit=1, used_count=1)
        assert coupon.is_valid is False


# ── Checkout with coupon ──────────────────────

class TestCheckoutWithCoupon:
    def test_checkout_applies_coupon(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        address = AddressFactory(user=user)
        product = ProductFactory(price=Decimal('10000'), discount_percent=0, stock=10)
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=1)
        coupon = CouponFactory(discount_type='percentage', discount_value=10)

        resp = client.post('/api/orders/checkout/', {
            'address_id': str(address.pk),
            'payment_method': 'cod',
            'coupon_code': coupon.code,
        }, format='json')

        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['coupon_code'] == coupon.code
        assert Decimal(resp.data['discount_amount']) == Decimal('1000.00')
        assert Decimal(resp.data['grand_total']) == Decimal('9000.00')

        # Usage recorded
        assert CouponUsage.objects.filter(coupon=coupon, user=user).exists()
        coupon.refresh_from_db()
        assert coupon.used_count == 1

    def test_checkout_without_coupon_still_works(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        address = AddressFactory(user=user)
        product = ProductFactory(price=Decimal('5000'), discount_percent=0, stock=10)
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=1)

        resp = client.post('/api/orders/checkout/', {
            'address_id': str(address.pk),
            'payment_method': 'cod',
        }, format='json')

        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['coupon_code'] == ''
        assert Decimal(resp.data['discount_amount']) == Decimal('0')
