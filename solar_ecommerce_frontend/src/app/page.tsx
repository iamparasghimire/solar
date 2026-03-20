'use client';

import Link from 'next/link';
import { useState } from 'react';

import { subscribeNewsletter } from '@/lib/api';

export default function Home() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleNewsletter = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setMessage('');
    try {
      const res = await subscribeNewsletter(email.trim());
      setMessage(res.detail);
      setEmail('');
    } catch (err) {
      const text = err instanceof Error ? err.message : 'Unable to subscribe right now.';
      setMessage(text);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <section className="bg-gradient-to-r from-blue-50 to-indigo-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl font-bold text-gray-900 mb-6">EcoPlanet Solar Store</h1>
              <p className="text-xl text-gray-600 mb-8">
                Ecommerce platform for solar panels, inverters, batteries, and installation-ready accessories.
              </p>
              <div className="flex gap-4">
                <Link
                  href="/products"
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition"
                >
                  Shop Products
                </Link>
                <Link
                  href="/contact"
                  className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-bold py-3 px-8 rounded-lg transition"
                >
                  Talk to Sales
                </Link>
              </div>
            </div>
            <div className="bg-gradient-to-br from-blue-400 to-indigo-600 rounded-lg h-96 flex items-center justify-center">
              <div className="text-white text-center">
                <div className="text-6xl mb-4">☀️</div>
                <p className="text-xl">Clean Energy Commerce</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-12 text-center">What You Can Buy</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Solar Panels</h3>
              <p className="text-gray-600">High-output monocrystalline and polycrystalline modules.</p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <div className="text-4xl mb-4">🔋</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Storage Systems</h3>
              <p className="text-gray-600">Hybrid batteries and backup energy systems for homes and offices.</p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <div className="text-4xl mb-4">🛠️</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Installation Gear</h3>
              <p className="text-gray-600">Mounting kits, charge controllers, and certified accessories.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-blue-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Subscribe to Newsletter</h2>
          <p className="text-blue-100 mb-8">Receive product launches and discounts</p>
          <form onSubmit={handleNewsletter} className="flex gap-2 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 px-4 py-3 rounded-lg focus:outline-none bg-white text-black"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-white text-blue-600 hover:bg-gray-100 disabled:bg-gray-200 font-bold px-8 py-3 rounded-lg transition"
            >
              {loading ? 'Submitting...' : 'Subscribe'}
            </button>
          </form>
          {message ? <p className="text-white mt-4">{message}</p> : null}
        </div>
      </section>
    </div>
  );
}
