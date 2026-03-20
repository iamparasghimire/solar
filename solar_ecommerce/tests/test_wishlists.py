"""Tests for the wishlists app."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.wishlists.models import WishlistItem
from tests.factories import ProductFactory, UserFactory

pytestmark = pytest.mark.django_db

URL = '/api/wishlists/'


def auth_client(user=None):
    client = APIClient()
    if user is None:
        user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


class TestWishlist:

    def test_add_to_wishlist(self):
        client, _ = auth_client()
        product = ProductFactory()
        resp = client.post(URL, {'product': str(product.id)})
        assert resp.status_code == status.HTTP_201_CREATED

    def test_duplicate_wishlist_rejected(self):
        client, user = auth_client()
        product = ProductFactory()
        client.post(URL, {'product': str(product.id)})
        resp = client.post(URL, {'product': str(product.id)})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_wishlist(self):
        client, user = auth_client()
        p1, p2 = ProductFactory(), ProductFactory()
        WishlistItem.objects.create(user=user, product=p1)
        WishlistItem.objects.create(user=user, product=p2)
        resp = client.get(URL)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 2

    def test_remove_from_wishlist(self):
        client, user = auth_client()
        product = ProductFactory()
        item = WishlistItem.objects.create(user=user, product=product)
        resp = client.delete(f'{URL}{item.id}/')
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not WishlistItem.objects.filter(pk=item.id).exists()

    def test_cannot_see_others_wishlist(self):
        other = UserFactory()
        WishlistItem.objects.create(user=other, product=ProductFactory())
        client, _ = auth_client()
        resp = client.get(URL)
        assert len(resp.data['results']) == 0

    def test_unauthenticated(self):
        resp = APIClient().get(URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
