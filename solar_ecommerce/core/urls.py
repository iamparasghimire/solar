from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import IsAdminUser, AllowAny

# In production, restrict API docs to admins only
_docs_permission = AllowAny if settings.DEBUG else IsAdminUser


def root_status(_request):
    return JsonResponse(
        {
            'status': 'ok',
            'service': 'solar-backend',
            'admin': '/admin/',
            'schema': '/api/schema/',
        }
    )

urlpatterns = [
    path('', root_status),
    path('admin/', admin.site.urls),

    # ── API v1 ────────────────────────────
    path('api/auth/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/wishlists/', include('apps.wishlists.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/coupons/', include('apps.coupons.urls')),
    path('api/contacts/', include('apps.contacts.urls')),

    # ── API Documentation (restricted in production) ──
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[_docs_permission]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[_docs_permission]), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema', permission_classes=[_docs_permission]), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
