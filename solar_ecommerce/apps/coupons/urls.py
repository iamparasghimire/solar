from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.CouponViewSet, basename='coupon')

urlpatterns = [
    path('apply/', views.ApplyCouponView.as_view(), name='apply_coupon'),
    path('', include(router.urls)),
]
