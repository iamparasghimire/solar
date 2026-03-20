'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { useCart } from '@/lib/cart-context';
import {
  fetchAddresses,
  createAddress,
  checkout,
  type Address,
} from '@/lib/api';

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
});

const emptyAddress = {
  label: 'Home',
  address_type: 'shipping',
  full_name: '',
  phone: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: 'India',
};

export default function CheckoutPage() {
  const router = useRouter();
  const { isAuthenticated, accessToken, user } = useAuth();
  const { cart, refresh: refreshCart } = useCart();

  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<string>('');
  const [showNewAddress, setShowNewAddress] = useState(false);
  const [newAddress, setNewAddress] = useState(emptyAddress);
  const [couponCode, setCouponCode] = useState('');
  const [note, setNote] = useState('');
  const [placing, setPlacing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) return;
    fetchAddresses(accessToken)
      .then((list) => {
        const addrs = Array.isArray(list) ? list : [];
        setAddresses(addrs);
        const defaultAddr = addrs.find((a) => a.is_default);
        if (defaultAddr) setSelectedAddressId(defaultAddr.id);
        else if (addrs.length > 0) setSelectedAddressId(addrs[0].id);
        else setShowNewAddress(true);
      })
      .catch(() => setShowNewAddress(true));
  }, [isAuthenticated, accessToken]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-white">
        <div className="max-w-4xl mx-auto px-4 py-20 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Checkout</h1>
          <p className="text-gray-600 mb-8">Please login to complete your order.</p>
          <Link href="/login" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition">
            Login to Continue
          </Link>
        </div>
      </div>
    );
  }

  const items = cart?.items ?? [];
  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-white">
        <div className="max-w-4xl mx-auto px-4 py-20 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Checkout</h1>
          <p className="text-gray-600 mb-8">Your cart is empty. Add products before checkout.</p>
          <Link href="/products" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition">
            Browse Products
          </Link>
        </div>
      </div>
    );
  }

  const handleSaveAddress = async () => {
    const { full_name, phone, address_line1, city, state, postal_code } = newAddress;
    if (!full_name || !phone || !address_line1 || !city || !state || !postal_code) {
      setError('Please fill all required address fields.');
      return;
    }
    try {
      const addr = await createAddress({ ...newAddress, is_default: addresses.length === 0 }, accessToken);
      setAddresses((prev) => [...prev, addr]);
      setSelectedAddressId(addr.id);
      setShowNewAddress(false);
      setNewAddress(emptyAddress);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save address.');
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddressId) {
      setError('Please select or add a shipping address.');
      return;
    }
    setPlacing(true);
    setError('');
    try {
      const order = await checkout(
        {
          address_id: selectedAddressId,
          payment_method: 'cod',
          coupon_code: couponCode || undefined,
          note: note || undefined,
        },
        accessToken,
      );
      await refreshCart();
      router.push(`/orders/${order.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to place order.');
    } finally {
      setPlacing(false);
    }
  };

  const updateField = (field: string, value: string) => {
    setNewAddress((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">
            {error}
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left: Address + Payment */}
          <div className="lg:col-span-2 space-y-6">
            {/* Shipping Address */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Shipping Address</h2>

              {addresses.length > 0 && !showNewAddress && (
                <div className="space-y-3 mb-4">
                  {addresses.map((addr) => (
                    <label
                      key={addr.id}
                      className={`flex items-start gap-3 p-4 border rounded-lg cursor-pointer transition ${
                        selectedAddressId === addr.id
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-400'
                      }`}
                    >
                      <input
                        type="radio"
                        name="address"
                        value={addr.id}
                        checked={selectedAddressId === addr.id}
                        onChange={() => setSelectedAddressId(addr.id)}
                        className="mt-1"
                      />
                      <div>
                        <p className="font-bold text-gray-900">
                          {addr.full_name}
                          <span className="ml-2 text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{addr.label}</span>
                        </p>
                        <p className="text-sm text-gray-600">{addr.address_line1}</p>
                        {addr.address_line2 && <p className="text-sm text-gray-600">{addr.address_line2}</p>}
                        <p className="text-sm text-gray-600">
                          {addr.city}, {addr.state} {addr.postal_code}
                        </p>
                        <p className="text-sm text-gray-600">📞 {addr.phone}</p>
                      </div>
                    </label>
                  ))}
                </div>
              )}

              {!showNewAddress ? (
                <button
                  onClick={() => setShowNewAddress(true)}
                  className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                >
                  + Add New Address
                </button>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                      <input
                        type="text"
                        value={newAddress.full_name}
                        onChange={(e) => updateField('full_name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder={user?.full_name || ''}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
                      <input
                        type="text"
                        value={newAddress.phone}
                        onChange={(e) => updateField('phone', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="+91 98765 43210"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1 *</label>
                    <input
                      type="text"
                      value={newAddress.address_line1}
                      onChange={(e) => updateField('address_line1', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Street address, apartment, suite..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 2</label>
                    <input
                      type="text"
                      value={newAddress.address_line2}
                      onChange={(e) => updateField('address_line2', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Landmark, building name..."
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">City *</label>
                      <input
                        type="text"
                        value={newAddress.city}
                        onChange={(e) => updateField('city', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                      <input
                        type="text"
                        value={newAddress.state}
                        onChange={(e) => updateField('state', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code *</label>
                      <input
                        type="text"
                        value={newAddress.postal_code}
                        onChange={(e) => updateField('postal_code', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                      <input
                        type="text"
                        value={newAddress.country}
                        onChange={(e) => updateField('country', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={handleSaveAddress}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition"
                    >
                      Save Address
                    </button>
                    {addresses.length > 0 && (
                      <button
                        onClick={() => setShowNewAddress(false)}
                        className="text-gray-600 hover:text-gray-700 font-medium py-2 px-6"
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Payment Method */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Payment Method</h2>
              <label className="flex items-center gap-3 p-4 border-2 border-blue-600 bg-blue-50 rounded-lg cursor-pointer">
                <input type="radio" name="payment" value="cod" defaultChecked className="text-blue-600" />
                <div>
                  <p className="font-bold text-gray-900">💵 Cash on Delivery</p>
                  <p className="text-sm text-gray-600">Pay when your order arrives</p>
                </div>
              </label>
            </div>

            {/* Coupon & Note */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Additional Info</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Coupon Code (optional)</label>
                  <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter coupon code"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Order Note (optional)</label>
                  <textarea
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Any special instructions..."
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Right: Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-24">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>

              <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                {items.map((item) => (
                  <div key={item.id} className="flex justify-between text-sm">
                    <span className="text-gray-600 truncate mr-2">
                      {item.product_detail?.name || 'Product'} × {item.quantity}
                    </span>
                    <span className="font-medium text-gray-900 flex-shrink-0">
                      {currency.format(item.line_total)}
                    </span>
                  </div>
                ))}
              </div>

              <div className="border-t border-gray-200 pt-4 space-y-2">
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
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span className="text-green-600 font-medium">Free</span>
                </div>
                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between text-xl font-bold text-gray-900">
                    <span>Total</span>
                    <span>{currency.format(cart?.grand_total ?? 0)}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Payment: Cash on Delivery</p>
                </div>
              </div>

              <button
                onClick={handlePlaceOrder}
                disabled={placing || !selectedAddressId}
                className="w-full mt-6 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 rounded-lg transition text-lg"
              >
                {placing ? 'Placing Order...' : 'Place Order (COD)'}
              </button>

              <Link href="/cart" className="block text-center text-sm text-blue-600 hover:underline mt-3">
                ← Back to Cart
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
