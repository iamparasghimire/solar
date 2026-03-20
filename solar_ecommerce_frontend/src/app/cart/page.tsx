'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { useCart } from '@/lib/cart-context';

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
});

export default function CartPage() {
  const { isAuthenticated } = useAuth();
  const { cart, loading, updateItem, removeItem, clear } = useCart();

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-white">
        <div className="max-w-4xl mx-auto px-4 py-20 text-center">
          <div className="text-6xl mb-6">🛒</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Your Cart</h1>
          <p className="text-gray-600 mb-8">Please login to view your cart.</p>
          <Link
            href="/login"
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition"
          >
            Login to Continue
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  const items = cart?.items ?? [];
  const isEmpty = items.length === 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
            <p className="text-gray-600 mt-1">{cart?.total_items ?? 0} items in cart</p>
          </div>
          {!isEmpty && (
            <button
              onClick={clear}
              className="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              Clear Cart
            </button>
          )}
        </div>

        {isEmpty ? (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            <div className="text-6xl mb-4">🛒</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
            <p className="text-gray-600 mb-6">Add some solar products to get started!</p>
            <Link
              href="/products"
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition inline-block"
            >
              Browse Products
            </Link>
          </div>
        ) : (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2 space-y-4">
              {items.map((item) => {
                const detail = item.product_detail;
                return (
                  <div key={item.id} className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex gap-6">
                      <div className="w-24 h-24 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg flex-shrink-0 flex items-center justify-center overflow-hidden">
                        {detail?.primary_image ? (
                          <img src={detail.primary_image} alt={detail.name} className="w-full h-full object-cover" />
                        ) : (
                          <div className="text-3xl">☀️</div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between">
                          <div>
                            <Link
                              href={`/products/${detail?.slug || ''}`}
                              className="font-bold text-gray-900 hover:text-blue-600 transition"
                            >
                              {detail?.name || 'Product'}
                            </Link>
                            <p className="text-sm text-gray-500 mt-1">
                              {detail?.category_name} {detail?.brand ? `• ${detail.brand}` : ''}
                            </p>
                          </div>
                          <p className="text-lg font-bold text-blue-600">
                            {currency.format(item.line_total)}
                          </p>
                        </div>

                        <div className="flex items-center justify-between mt-4">
                          <div className="flex items-center gap-3">
                            <button
                              onClick={() => updateItem(item.id, Math.max(1, item.quantity - 1))}
                              className="w-8 h-8 rounded border border-gray-300 flex items-center justify-center hover:bg-gray-50 text-sm font-bold"
                            >
                              −
                            </button>
                            <span className="w-8 text-center font-bold">{item.quantity}</span>
                            <button
                              onClick={() => updateItem(item.id, item.quantity + 1)}
                              className="w-8 h-8 rounded border border-gray-300 flex items-center justify-center hover:bg-gray-50 text-sm font-bold"
                            >
                              +
                            </button>
                            <span className="text-sm text-gray-500 ml-2">
                              × {currency.format(item.unit_price)} each
                            </span>
                          </div>
                          <button
                            onClick={() => removeItem(item.id)}
                            className="text-red-500 hover:text-red-700 text-sm font-medium"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-24">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>

                <div className="space-y-3 mb-6">
                  <div className="flex justify-between text-gray-600">
                    <span>Subtotal</span>
                    <span>{currency.format(cart?.subtotal ?? 0)}</span>
                  </div>
                  {(cart?.installation_total ?? 0) > 0 && (
                    <div className="flex justify-between text-gray-600">
                      <span>Installation</span>
                      <span>{currency.format(cart?.installation_total ?? 0)}</span>
                    </div>
                  )}
                  <div className="border-t border-gray-200 pt-3">
                    <div className="flex justify-between text-lg font-bold text-gray-900">
                      <span>Total</span>
                      <span>{currency.format(cart?.grand_total ?? 0)}</span>
                    </div>
                  </div>
                </div>

                <Link
                  href="/checkout"
                  className="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition text-center"
                >
                  Proceed to Checkout
                </Link>

                <Link
                  href="/products"
                  className="block w-full text-center text-blue-600 hover:text-blue-700 font-medium mt-3"
                >
                  Continue Shopping
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
