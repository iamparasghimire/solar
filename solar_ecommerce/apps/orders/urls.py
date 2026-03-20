from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('list', views.OrderViewSet, basename='order')
router.register('warranties', views.WarrantyDocumentViewSet, basename='warranty')

urlpatterns = [
    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='cart_add'),
    path('cart/clear/', views.ClearCartView.as_view(), name='cart_clear'),
    path('cart/items/<uuid:item_id>/', views.UpdateCartItemView.as_view(), name='cart_item'),

    # Checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),

    # Orders & warranties via router
    path('', include(router.urls)),
]
