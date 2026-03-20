# EcoPlanet Solar Frontend

This frontend is integrated with the Django backend in `../solar_ecommerce`.

## Backend + Frontend Setup

1. Start backend (`/home/paras/Documents/solar/solar_ecommerce`):

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

2. Start frontend (`/home/paras/Documents/solar/solar_ecommerce_frontend`):

```bash
npm install
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

Open `http://localhost:3000`.

## Implemented Integration

- Product listing reads from `GET /api/products/`.
- Category filter reads from `GET /api/products/categories/`.
- Add to cart calls `POST /api/orders/cart/add/` (JWT access token required).
- Contact page sends data to `POST /api/contacts/`.
- Newsletter form sends data to `POST /api/contacts/newsletter/`.

## Notes

- Auth endpoints:
  - `POST /api/auth/register/`
  - `POST /api/auth/login/`
- Paste access token on the Products page before using Add to Cart.

## Build

If Turbopack build is restricted in your environment, use webpack:

```bash
npm run build -- --webpack
```
