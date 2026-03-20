"""Tests for the reviews app."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.reviews.models import Review
from tests.factories import ProductFactory, UserFactory

pytestmark = pytest.mark.django_db

URL = '/api/reviews/'


def auth_client(user=None):
    client = APIClient()
    if user is None:
        user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


class TestReviews:

    def test_create_review(self):
        client, user = auth_client()
        product = ProductFactory()
        resp = client.post(URL, {
            'product': str(product.id),
            'rating': 5,
            'title': 'Excellent panel',
            'comment': 'Great quality, highly recommend.',
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['rating'] == 5

    def test_duplicate_review_rejected(self):
        client, user = auth_client()
        product = ProductFactory()
        client.post(URL, {'product': str(product.id), 'rating': 4})
        resp = client.post(URL, {'product': str(product.id), 'rating': 3})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_reviews_public(self):
        product = ProductFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        Review.objects.create(user=user1, product=product, rating=5)
        Review.objects.create(user=user2, product=product, rating=4)
        resp = APIClient().get(URL, {'product': str(product.id)})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 2

    def test_update_own_review(self):
        client, user = auth_client()
        product = ProductFactory()
        review = Review.objects.create(user=user, product=product, rating=3)
        resp = client.patch(f'{URL}{review.id}/', {'rating': 5})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['rating'] == 5

    def test_cannot_update_others_review(self):
        owner = UserFactory()
        product = ProductFactory()
        review = Review.objects.create(user=owner, product=product, rating=4)
        client, _ = auth_client()  # different user
        resp = client.patch(f'{URL}{review.id}/', {'rating': 1})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_rating_validation(self):
        client, _ = auth_client()
        product = ProductFactory()
        resp = client.post(URL, {'product': str(product.id), 'rating': 0})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        resp = client.post(URL, {'product': str(product.id), 'rating': 6})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
