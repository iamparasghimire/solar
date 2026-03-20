from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('admin/messages', views.ContactAdminViewSet, basename='contact-admin')

urlpatterns = [
    path('', views.ContactCreateView.as_view(), name='contact'),
    path('newsletter/', views.NewsletterSubscribeView.as_view(), name='newsletter'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),
    path('', include(router.urls)),
]
