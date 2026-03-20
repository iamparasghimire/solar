# Solar E-Commerce API – Daily Development Log

---

## 📅 February 23, 2026

### Tasks Completed – Security Audit & Hardening (15/15)

---

### 1. ✅ Settings Security Hardening
- `SECRET_KEY` now requires `DJANGO_SECRET_KEY` env var in production (raises `RuntimeError` if missing)
- `DEBUG` controlled via `DJANGO_DEBUG` env var
- `ALLOWED_HOSTS` configurable via `DJANGO_ALLOWED_HOSTS` env var
- Added production security block: HSTS (1 year), SSL redirect, secure cookies, `X-FRAME-OPTIONS: DENY`, strict referrer policy
- Disabled Browsable API in production (JSON-only renderer)
- Added file upload size limits (5MB images, 10MB documents)

### 2. ✅ Fixed Race Conditions (Stock & Coupon)
- Stock decrement during checkout now uses `F('stock') - quantity` (atomic DB operation)
- Coupon `used_count` incremented with `F('used_count') + 1`
- Stock restore on cancel uses `F('stock') + quantity`

### 3. ✅ Fixed Broken Admin Order Management
- `OrderViewSet.get_queryset()` now returns all orders for staff, filtered for regular users
- Added `check_object_permissions` for IDOR protection on non-admin users
- `update_status` action restricted to `IsAdminUser`

### 4. ✅ Added Order Status Transition Validation
- Status transitions enforced via `valid_transitions` dict (e.g., pending→confirmed/cancelled only)
- Cancelled orders cannot be updated further

### 5. ✅ Fixed Upload Permission Vulnerability
- Product image upload changed from `IsAuthenticated` → `IsAdminUser`

### 6. ✅ Added File Upload Validation
- `ProductImageSerializer.validate_image()` – 5MB max, JPEG/PNG/WebP only
- `WarrantyDocumentSerializer.validate_file()` – 10MB max, PDF only

### 7. ✅ Added Rate Limiting / Throttling
- Global: 60/min anon, 120/min authenticated
- Auth endpoints (login/register/refresh): 5/min
- Contact/newsletter: 3/min
- Created `apps/throttles.py` with `AuthRateThrottle` and `ContactRateThrottle`

### 8. ✅ Created Input Sanitization Middleware (`apps/middleware.py`)
- `InputSanitizationMiddleware` – blocks null bytes, limits query string to 2048 chars
- `SecurityHeadersMiddleware` – adds Permissions-Policy, X-Content-Type-Options, Cache-Control for API

### 9. ✅ Created Custom Exception Handler (`apps/exceptions.py`)
- Unhandled exceptions return generic error message (no traceback leak)
- Known DRF exceptions pass through unchanged
- Errors logged server-side for debugging

### 10. ✅ Fixed Coupon Information Leakage
- Added `CouponPublicSerializer` (hides `usage_limit`, `used_count`, `per_user_limit`)
- Role-based serializer selection in `CouponViewSet`

### 11. ✅ Protected API Documentation in Production
- Swagger/ReDoc endpoints restricted to `IsAdminUser` when `DEBUG=False`

### 12. ✅ Added IDOR Protection Tests
- Order IDOR (view/cancel other user's orders)
- Address IDOR (checkout with other user's address)
- Cart IDOR (update/delete other user's cart items)

### 13. ✅ Added Admin Endpoint Protection Tests
- Dashboard, contact messages, product/category/coupon creation – all require admin

### 14. ✅ Added Auth Required Parametrized Tests
- 7 protected endpoints verified (cart, checkout, orders, wishlists, profile, coupon apply)

### 15. ✅ Fixed Test Infrastructure
- Created `tests/conftest.py` with autouse fixture to disable throttling in tests
- Fixed `UserFactory` to use `_create` classmethod with `create_user` for proper password hashing
- Added `AdminFactory` for admin-specific test scenarios

### Test Results: 114 passed, 0 failed, 0 warnings ✅ (up from 89)

---

### New Files Created
| File | Purpose |
|------|---------|
| `apps/throttles.py` | Custom throttle classes (AuthRateThrottle, ContactRateThrottle) |
| `apps/middleware.py` | SecurityHeadersMiddleware + InputSanitizationMiddleware |
| `apps/exceptions.py` | Custom DRF exception handler (prevents traceback leaks) |
| `tests/conftest.py` | Shared pytest fixtures (throttle disable) |
| `tests/test_security.py` | 17 security-focused tests (IDOR, permissions, auth) |

### Files Modified
| File | Change |
|------|--------|
| `core/settings.py` | SECRET_KEY hardening, security headers, throttles, middleware, file limits |
| `core/urls.py` | API docs permission restriction in production |
| `apps/orders/serializers.py` | F() atomic operations, file validation |
| `apps/orders/views.py` | Admin order management, status transitions, IDOR protection |
| `apps/products/views.py` | Upload permission fix (IsAdminUser) |
| `apps/products/serializers.py` | Image upload validation |
| `apps/coupons/serializers.py` | Added CouponPublicSerializer |
| `apps/coupons/views.py` | Role-based serializer selection |
| `apps/contacts/views.py` | Rate limiting on contact/newsletter |
| `apps/users/views.py` | Rate limiting on register |
| `apps/users/urls.py` | Throttled login/refresh views |
| `tests/test_orders.py` | Added 5 admin management tests |
| `tests/factories.py` | Fixed UserFactory password hashing |

---
---

## 📅 February 16, 2026

### Tasks Completed (8/8)

---

### 1. ✅ Wired Up Coupons App
- Added `apps.coupons` to `LOCAL_APPS` in `core/settings.py`
- Added `path('api/coupons/', include('apps.coupons.urls'))` to `core/urls.py`
- Created & applied migration `coupons/0001_initial.py`

### 2. ✅ Updated Order Serializers & Views (Coupon + Cancel + Clear Cart)
- **Order model new fields:**
  - `coupon_code` – stores applied coupon code
  - `discount_amount` – discount applied to the order
  - `payment_status` – unpaid / paid / refunded
  - `payment_id` – payment gateway transaction ID
  - `paid_at` – payment timestamp
  - `cancelled_at` – cancellation timestamp
  - `cancellation_reason` – user-provided reason
- **Checkout with coupon:** `CheckoutSerializer` now accepts optional `coupon_code`, validates it, calculates discount, and records `CouponUsage`
- **Cancel order:** `POST /api/orders/list/<id>/cancel/` – only pending orders, restores stock atomically
- **Clear cart:** `DELETE /api/orders/cart/clear/` – removes all items from cart
- Created & applied migration `orders/0003_order_cancellation_reason_order_cancelled_at_and_more.py`

### 3. ✅ Added Featured & Related Products
- **Product model new fields:** `is_featured`, `brand`, `tags`
- **New endpoints:**
  - `GET /api/products/featured/` – returns featured products (public)
  - `GET /api/products/<slug>/related/` – same-category products excluding self (public)
- **New filters:** `is_featured`, `brand` added to `filterset_fields`
- **New search fields:** `brand`, `tags` added to `search_fields`
- Created & applied migration `products/0002_product_brand_product_is_featured_product_tags.py`

### 4. ✅ Created Contacts & Newsletter App (`apps/contacts/`)
- **Files created:** `__init__.py`, `apps.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `migrations/__init__.py`
- **Models:**
  - `ContactMessage` – name, email, phone, subject, message, status (new/in_progress/resolved), admin_notes
  - `NewsletterSubscriber` – email (unique), is_active
- **Endpoints:**
  - `POST /api/contacts/` – public contact form submission
  - `GET/POST/PATCH/DELETE /api/contacts/admin/messages/` – admin CRUD for messages
  - `POST /api/contacts/newsletter/` – subscribe (reactivates if previously unsubscribed)
  - `POST /api/contacts/newsletter/unsubscribe/` – unsubscribe by email
- Added `apps.contacts` to `LOCAL_APPS` in settings
- Added URL route in `core/urls.py`
- Created & applied migration `contacts/0001_initial.py`

### 5. ✅ Created Admin Dashboard API
- **Endpoint:** `GET /api/auth/admin/dashboard/` (admin only)
- **Returns:**
  - Order stats: total orders, total revenue, pending/delivered/cancelled counts
  - Recent 30-day stats: order count & revenue
  - Product stats: total, active, out of stock, featured, total categories
  - Customer stats: total customers, new customers in last 30 days
  - Support stats: new contact messages, active newsletter subscribers

### 6. ✅ Updated Admin Registrations
- **Product admin:** added `is_featured` to `list_display`, `brand` to `list_filter`, `brand`/`tags` to `search_fields`
- **Order admin:** added `payment_status` to `list_display`/`list_filter`, `coupon_code` to `search_fields`, cancellation fields to `readonly_fields`

### 7. ✅ Ran Migrations & System Check
- 4 new migrations created and applied successfully:
  - `contacts/0001_initial.py`
  - `coupons/0001_initial.py`
  - `orders/0003_order_cancellation_reason_order_cancelled_at_and_more.py`
  - `products/0002_product_brand_product_is_featured_product_tags.py`
- `python manage.py check` → **System check identified no issues (0 silenced)**

### 8. ✅ Wrote Tests for All New Features
- **New test files:**
  - `tests/test_coupons.py` – 14 tests (CRUD, apply, model logic, checkout integration)
  - `tests/test_contacts.py` – 9 tests (contact form, admin CRUD, newsletter subscribe/unsubscribe)
- **Updated test files:**
  - `tests/test_orders.py` – added 4 tests (clear cart, cancel pending, cannot cancel non-pending)
  - `tests/test_products.py` – added 8 tests (featured list, related products, filter by featured/brand)
  - `tests/factories.py` – added `AdminFactory`, `CouponFactory`, `ContactMessageFactory`, `NewsletterSubscriberFactory`

### Test Results: 89 passed, 0 failed ✅

---

### Files Modified Today
| File | Change |
|------|--------|
| `core/settings.py` | Added `apps.coupons`, `apps.contacts` to LOCAL_APPS |
| `core/urls.py` | Added coupons & contacts URL routes |
| `apps/orders/models.py` | Added coupon, payment, cancellation fields to Order |
| `apps/orders/serializers.py` | Coupon checkout integration + CancelOrderSerializer |
| `apps/orders/views.py` | Added ClearCartView + cancel order action |
| `apps/orders/urls.py` | Added `/cart/clear/` route |
| `apps/orders/admin.py` | New fields in list/filter/readonly |
| `apps/products/models.py` | Added `is_featured`, `brand`, `tags` |
| `apps/products/serializers.py` | Exposed new fields in list & detail serializers |
| `apps/products/views.py` | Added `featured/` & `related/` actions + new filters |
| `apps/products/admin.py` | Featured/brand in list/filter |
| `apps/users/views.py` | Added AdminDashboardView |
| `apps/users/urls.py` | Added `/admin/dashboard/` route |
| `tests/factories.py` | Added 4 new factories |
| `tests/test_coupons.py` | Created – 14 tests |
| `tests/test_contacts.py` | Created – 9 tests |
| `tests/test_orders.py` | Added 4 new tests |
| `tests/test_products.py` | Added 8 new tests |

### New Files Created Today
| File | Purpose |
|------|---------|
| `apps/contacts/__init__.py` | Package init |
| `apps/contacts/apps.py` | App config |
| `apps/contacts/models.py` | ContactMessage + NewsletterSubscriber models |
| `apps/contacts/serializers.py` | Serializers for contact & newsletter |
| `apps/contacts/views.py` | Public contact form + admin CRUD + newsletter |
| `apps/contacts/urls.py` | URL routing |
| `apps/contacts/admin.py` | Admin panel registration |
| `apps/contacts/migrations/__init__.py` | Migrations package init |
