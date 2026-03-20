"""
Factory classes for generating test data across all apps.
"""

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta

from apps.products.models import Category, Product
from apps.orders.models import Cart, CartItem, Order, OrderItem
from apps.users.models import Address
from apps.coupons.models import Coupon
from apps.contacts.models import ContactMessage, NewsletterSubscriber

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@test.com')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Use create_user to properly hash the password."""
        manager = cls._get_manager(model_class)
        password = kwargs.pop('password', 'testpass123')
        user = manager.create_user(*args, password=password, **kwargs)
        return user


class AdminFactory(UserFactory):
    is_staff = True
    is_superuser = True


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    user = factory.SubFactory(UserFactory)
    label = 'Home'
    full_name = factory.Faker('name')
    phone = '9876543210'
    address_line1 = factory.Faker('street_address')
    city = 'Mumbai'
    state = 'Maharashtra'
    postal_code = '400001'
    country = 'India'
    is_default = True


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    is_active = True


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f'Solar Product {n}')
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    sku = factory.Sequence(lambda n: f'SKU-{n:04d}')
    price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True, min_value=100, max_value=99999)
    stock = 50
    warranty_years = 10
    lifespan_years = 25
    capacity = '5kW'
    is_active = True
    installation_fee = 2000


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    include_installation = False


class CouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Coupon

    code = factory.Sequence(lambda n: f'SAVE{n:03d}')
    discount_type = 'percentage'
    discount_value = 10
    valid_from = factory.LazyFunction(lambda: timezone.now() - timedelta(days=1))
    valid_until = factory.LazyFunction(lambda: timezone.now() + timedelta(days=30))
    is_active = True
    usage_limit = 0  # unlimited
    per_user_limit = 1


class ContactMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactMessage

    name = factory.Faker('name')
    email = factory.Faker('email')
    subject = factory.Faker('sentence')
    message = factory.Faker('paragraph')


class NewsletterSubscriberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsletterSubscriber

    email = factory.Sequence(lambda n: f'sub{n}@test.com')
    is_active = True
