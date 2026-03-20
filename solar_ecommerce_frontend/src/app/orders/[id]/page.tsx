'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { fetchOrder, cancelOrder, type Order } from '@/lib/api';

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
});

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  processing: 'bg-purple-100 text-purple-800',
  shipped: 'bg-indigo-100 text-indigo-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

export default function OrderDetailPage() {
  const params = useParams();
  const orderId = params.id as string;
  const { isAuthenticated, accessToken } = useAuth();

  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelling, setCancelling] = useState(false);
  const [isNewOrder, setIsNewOrder] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || !orderId) return;
    fetchOrder(orderId, accessToken)
      .then((data) => {
        setOrder(data);
        // If order was created in the last 30 seconds, show success animation
        const created = new Date(data.created_at).getTime();
        if (Date.now() - created < 30000) setIsNewOrder(true);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [orderId, isAuthenticated, accessToken]);

  const handleCancel = async () => {
    if (!order || !confirm('Are you sure you want to cancel this order?')) return;
    setCancelling(true);
    try {
      const updated = await cancelOrder(order.id, 'Customer requested cancellation', accessToken);
      setOrder(updated);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to cancel order.');
    } finally {
      setCancelling(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please login to view order details.</p>
          <Link href="/login" className="text-blue-600 hover:underline">Login</Link>
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

  if (error || !order) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-xl mb-4">{error || 'Order not found'}</p>
          <Link href="/orders" className="text-blue-600 hover:underline">← Back to Orders</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success banner for new orders */}
        {isNewOrder && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8 text-center">
            <div className="text-5xl mb-3">🎉</div>
            <h2 className="text-2xl font-bold text-green-800 mb-2">Order Placed Successfully!</h2>
            <p className="text-green-700">
              Thank you for your order. You&apos;ll pay{' '}
              <strong>{currency.format(order.grand_total)}</strong> upon delivery.
            </p>
          </div>
        )}

        {/* Order Header */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Order {order.order_number}</h1>
              <p className="text-sm text-gray-500 mt-1">
                Placed on {new Date(order.created_at).toLocaleDateString('en-IN', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-bold capitalize ${statusColors[order.status] || 'bg-gray-100 text-gray-800'}`}>
                {order.status}
              </span>
              {order.status === 'pending' && (
                <button
                  onClick={handleCancel}
                  disabled={cancelling}
                  className="text-red-600 hover:text-red-700 text-sm font-medium"
                >
                  {cancelling ? 'Cancelling...' : 'Cancel Order'}
                </button>
              )}
            </div>
          </div>

          {/* Payment Info */}
          <div className="grid sm:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Payment Method:</span>
              <span className="ml-2 font-medium text-gray-900 capitalize">{order.payment_method === 'cod' ? 'Cash on Delivery' : order.payment_method}</span>
            </div>
            <div>
              <span className="text-gray-500">Payment Status:</span>
              <span className={`ml-2 font-medium capitalize ${order.payment_status === 'paid' ? 'text-green-600' : 'text-amber-600'}`}>
                {order.payment_status}
              </span>
            </div>
          </div>
        </div>

        {/* Items */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Items ({order.items.length})</h2>
          <div className="space-y-4">
            {order.items.map((item) => (
              <div key={item.id} className="flex justify-between items-center py-3 border-b border-gray-100 last:border-0">
                <div>
                  <p className="font-medium text-gray-900">{item.product_name}</p>
                  <p className="text-sm text-gray-500">
                    SKU: {item.sku} • Qty: {item.quantity} × {currency.format(item.unit_price)}
                  </p>
                  {item.include_installation && (
                    <p className="text-sm text-blue-600">+ Installation: {currency.format(item.installation_fee)}/unit</p>
                  )}
                </div>
                <p className="font-bold text-gray-900">{currency.format(item.line_total)}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-6">
          {/* Shipping */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Shipping Address</h2>
            <p className="font-medium text-gray-900">{order.shipping_full_name}</p>
            <p className="text-sm text-gray-600">{order.shipping_address}</p>
            <p className="text-sm text-gray-600">
              {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}
            </p>
            <p className="text-sm text-gray-600">{order.shipping_country}</p>
            <p className="text-sm text-gray-600 mt-1">📞 {order.shipping_phone}</p>
          </div>

          {/* Totals */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Order Total</h2>
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Subtotal</span>
                <span>{currency.format(order.subtotal)}</span>
              </div>
              {order.installation_total > 0 && (
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Installation</span>
                  <span>{currency.format(order.installation_total)}</span>
                </div>
              )}
              {order.discount_amount > 0 && (
                <div className="flex justify-between text-sm text-green-600">
                  <span>Discount {order.coupon_code ? `(${order.coupon_code})` : ''}</span>
                  <span>−{currency.format(order.discount_amount)}</span>
                </div>
              )}
              <div className="border-t border-gray-200 pt-2">
                <div className="flex justify-between text-lg font-bold text-gray-900">
                  <span>Grand Total</span>
                  <span>{currency.format(order.grand_total)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {order.note && (
          <div className="bg-white rounded-lg border border-gray-200 p-6 mt-6">
            <h2 className="text-lg font-bold text-gray-900 mb-2">Order Note</h2>
            <p className="text-gray-600">{order.note}</p>
          </div>
        )}

        <div className="mt-8 flex gap-4">
          <Link href="/orders" className="text-blue-600 hover:underline font-medium">
            ← My Orders
          </Link>
          <Link href="/products" className="text-blue-600 hover:underline font-medium">
            Continue Shopping
          </Link>
        </div>
      </div>
    </div>
  );
}
