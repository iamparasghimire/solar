const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ||
  "http://127.0.0.1:8000";

type Primitive = string | number | boolean;

function toQueryString(params: Record<string, Primitive | undefined>) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  return searchParams.toString();
}

function authHeaders(token: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  const payload = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail =
      payload?.detail ||
      payload?.non_field_errors?.[0] ||
      Object.values(payload || {}).flat().join(" ") ||
      "Request failed";
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  return payload as T;
}

// ── Types ────────────────────────────────────

export interface Category {
  id: string;
  name: string;
  slug: string;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  category_name: string;
  category: string;
  price: string | number;
  discount_percent: string | number;
  discounted_price: string | number;
  capacity: string;
  warranty_years: number;
  brand: string;
  is_featured: boolean;
  primary_image: string | null;
  average_rating: number;
  review_count: number;
  in_stock: boolean;
}

export interface ProductDetail extends Product {
  description: string;
  technical_description: string;
  stock: number;
  delivery_days: number;
  installation_available: boolean;
  installation_fee: string | number;
  tags: string;
  images: { id: string; image: string; alt_text: string; is_primary: boolean }[];
  lifespan_years: number;
  sku: string;
}

interface PaginatedProducts {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

export interface CartItem {
  id: string;
  product: string;
  product_detail: Product;
  quantity: number;
  include_installation: boolean;
  unit_price: number;
  line_total: number;
}

export interface Cart {
  id: string;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  installation_total: number;
  grand_total: number;
}

export interface Address {
  id: string;
  label: string;
  address_type: string;
  full_name: string;
  phone: string;
  address_line1: string;
  address_line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

export interface OrderItem {
  id: string;
  product: string;
  product_name: string;
  sku: string;
  unit_price: number;
  quantity: number;
  include_installation: boolean;
  installation_fee: number;
  line_total: number;
}

export interface Order {
  id: string;
  order_number: string;
  status: string;
  payment_method: string;
  shipping_full_name: string;
  shipping_phone: string;
  shipping_address: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  shipping_country: string;
  subtotal: number;
  installation_total: number;
  discount_amount: number;
  coupon_code: string;
  grand_total: number;
  payment_status: string;
  note: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone_number: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

// ── Auth ─────────────────────────────────────

export async function login(email: string, password: string) {
  return request<AuthTokens>("/api/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function register(data: {
  email: string;
  username: string;
  phone_number?: string;
  password: string;
  password2: string;
}) {
  return request<{ user: UserProfile; tokens: AuthTokens }>(
    "/api/auth/register/",
    { method: "POST", body: JSON.stringify(data) }
  );
}

export async function fetchProfile(token: string) {
  return request<UserProfile>("/api/auth/profile/", {
    headers: authHeaders(token),
  });
}

export async function refreshToken(refresh: string) {
  return request<{ access: string }>("/api/auth/token/refresh/", {
    method: "POST",
    body: JSON.stringify({ refresh }),
  });
}

// ── Products ─────────────────────────────────

export async function fetchCategories() {
  const payload = await request<any>("/api/products/categories/");
  if (Array.isArray(payload)) return payload as Category[];
  if (payload && Array.isArray(payload.results))
    return payload.results as Category[];
  return [];
}

export async function fetchProducts(params: {
  search?: string;
  categorySlug?: string;
}) {
  const query = toQueryString({
    search: params.search,
    category__slug:
      params.categorySlug && params.categorySlug !== "all"
        ? params.categorySlug
        : undefined,
  });
  const suffix = query ? `?${query}` : "";
  return request<PaginatedProducts>(`/api/products/${suffix}`);
}

export async function fetchProductBySlug(slug: string) {
  return request<ProductDetail>(`/api/products/${slug}/`);
}

export async function fetchFeaturedProducts() {
  return request<Product[]>("/api/products/featured/");
}

export async function fetchRelatedProducts(slug: string) {
  return request<Product[]>(`/api/products/${slug}/related/`);
}

// ── Cart ─────────────────────────────────────

export async function fetchCart(token: string) {
  return request<Cart>("/api/orders/cart/", {
    headers: authHeaders(token),
  });
}

export async function addToCart(payload: {
  productId: string;
  quantity?: number;
  includeInstallation?: boolean;
  accessToken: string;
}) {
  return request<Cart>("/api/orders/cart/add/", {
    method: "POST",
    headers: authHeaders(payload.accessToken),
    body: JSON.stringify({
      product: payload.productId,
      quantity: payload.quantity ?? 1,
      include_installation: payload.includeInstallation ?? false,
    }),
  });
}

export async function updateCartItem(
  itemId: string,
  data: { quantity: number; include_installation?: boolean },
  token: string
) {
  return request<Cart>(`/api/orders/cart/items/${itemId}/`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export async function removeCartItem(itemId: string, token: string) {
  return request<Cart>(`/api/orders/cart/items/${itemId}/`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

export async function clearCart(token: string) {
  return request<Cart>("/api/orders/cart/clear/", {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

// ── Addresses ────────────────────────────────

export async function fetchAddresses(token: string) {
  return request<Address[]>("/api/auth/addresses/", {
    headers: authHeaders(token),
  });
}

export async function createAddress(
  data: Omit<Address, "id" | "is_default"> & { is_default?: boolean },
  token: string
) {
  return request<Address>("/api/auth/addresses/", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

// ── Checkout & Orders ────────────────────────

export async function checkout(
  data: {
    address_id: string;
    payment_method: string;
    coupon_code?: string;
    note?: string;
  },
  token: string
) {
  return request<Order>("/api/orders/checkout/", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export async function fetchOrders(token: string) {
  const payload = await request<any>("/api/orders/list/", {
    headers: authHeaders(token),
  });
  if (Array.isArray(payload)) return payload as Order[];
  if (payload && Array.isArray(payload.results))
    return payload.results as Order[];
  return [];
}

export async function fetchOrder(id: string, token: string) {
  return request<Order>(`/api/orders/list/${id}/`, {
    headers: authHeaders(token),
  });
}

export async function cancelOrder(id: string, reason: string, token: string) {
  return request<Order>(`/api/orders/list/${id}/cancel/`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

// ── Contacts & Newsletter ────────────────────

export async function submitContact(payload: {
  name: string;
  email: string;
  phone?: string;
  subject: string;
  message: string;
}) {
  return request<{ detail: string }>("/api/contacts/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function subscribeNewsletter(email: string) {
  return request<{ detail: string }>("/api/contacts/newsletter/", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}
