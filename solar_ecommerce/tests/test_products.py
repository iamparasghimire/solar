"""Tests for the products app – categories, product list/detail, search, filtering."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import CategoryFactory, ProductFactory, UserFactory

pytestmark = pytest.mark.django_db


def admin_client():
    user = UserFactory(is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def anon_client():
    return APIClient()


# ── Categories ────────────────────────────────

class TestCategories:
    URL = '/api/products/categories/'

    def test_list_categories_public(self):
        CategoryFactory.create_batch(3)
        resp = anon_client().get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 3

    def test_create_category_admin_only(self):
        resp = anon_client().post(self.URL, {'name': 'Panels', 'slug': 'panels'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_as_admin(self):
        resp = admin_client().post(self.URL, {'name': 'Inverters', 'slug': 'inverters'})
        assert resp.status_code == status.HTTP_201_CREATED


# ── Product List ──────────────────────────────

class TestProductList:
    URL = '/api/products/'

    def test_list_products_public(self):
        ProductFactory.create_batch(5)
        resp = anon_client().get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 5

    def test_inactive_products_hidden_from_public(self):
        ProductFactory(is_active=True)
        ProductFactory(is_active=False)
        resp = anon_client().get(self.URL)
        assert len(resp.data['results']) == 1

    def test_admin_sees_inactive_products(self):
        ProductFactory(is_active=True)
        ProductFactory(is_active=False)
        resp = admin_client().get(self.URL)
        assert len(resp.data['results']) == 2

    def test_search_by_name(self):
        ProductFactory(name='UltraVolt 540W Panel')
        ProductFactory(name='PowerMax Inverter')
        resp = anon_client().get(self.URL, {'search': 'UltraVolt'})
        assert len(resp.data['results']) == 1

    def test_filter_by_category(self):
        cat = CategoryFactory(slug='panels')
        ProductFactory(category=cat)
        ProductFactory()  # different category
        resp = anon_client().get(self.URL, {'category__slug': 'panels'})
        assert len(resp.data['results']) == 1

    def test_ordering_by_price(self):
        ProductFactory(price=500)
        ProductFactory(price=100)
        ProductFactory(price=300)
        resp = anon_client().get(self.URL, {'ordering': 'price'})
        prices = [r['price'] for r in resp.data['results']]
        assert prices == sorted(prices)


# ── Product Detail ────────────────────────────

class TestProductDetail:

    def test_detail_by_slug(self):
        p = ProductFactory(slug='test-panel')
        resp = anon_client().get(f'/api/products/{p.slug}/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['slug'] == 'test-panel'
        assert 'discounted_price' in resp.data
        assert 'average_rating' in resp.data
        assert 'images' in resp.data

    def test_detail_404(self):
        resp = anon_client().get('/api/products/nonexistent/')
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ── Product Create (Admin) ────────────────────

class TestProductCreate:
    URL = '/api/products/'

    def test_create_product_as_admin(self):
        cat = CategoryFactory()
        client = admin_client()
        data = {
            'name': 'New Panel',
            'slug': 'new-panel',
            'sku': 'NP-001',
            'category_id': str(cat.id),
            'price': '15000.00',
            'stock': 100,
        }
        resp = client.post(self.URL, data)
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_product_anon_forbidden(self):
        resp = anon_client().post(self.URL, {'name': 'Hack'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ── Featured Products ─────────────────────────

class TestFeaturedProducts:
    URL = '/api/products/featured/'

    def test_featured_returns_only_featured(self):
        ProductFactory(is_featured=True)
        ProductFactory(is_featured=True)
        ProductFactory(is_featured=False)
        resp = anon_client().get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2

    def test_featured_empty(self):
        ProductFactory(is_featured=False)
        resp = anon_client().get(self.URL)
        assert len(resp.data) == 0


# ── Related Products ─────────────────────────

class TestRelatedProducts:
    def test_related_same_category(self):
        cat = CategoryFactory()
        p1 = ProductFactory(category=cat, slug='main-product')
        ProductFactory(category=cat)
        ProductFactory(category=cat)
        ProductFactory()  # different category

        resp = anon_client().get(f'/api/products/{p1.slug}/related/')
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2  # excludes itself, excludes other category

    def test_related_excludes_self(self):
        cat = CategoryFactory()
        p = ProductFactory(category=cat, slug='only-product')
        resp = anon_client().get(f'/api/products/{p.slug}/related/')
        assert len(resp.data) == 0


# ── Filter by featured/brand ─────────────────

class TestProductFiltering:
    URL = '/api/products/'

    def test_filter_by_featured(self):
        ProductFactory(is_featured=True)
        ProductFactory(is_featured=False)
        resp = anon_client().get(self.URL, {'is_featured': True})
        assert len(resp.data['results']) == 1

    def test_filter_by_brand(self):
        ProductFactory(brand='Luminous')
        ProductFactory(brand='Tata Power')
        resp = anon_client().get(self.URL, {'brand': 'Luminous'})
        assert len(resp.data['results']) == 1
