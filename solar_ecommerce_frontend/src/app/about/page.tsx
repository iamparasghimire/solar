'use client';

import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Page Header */}
      <section className="bg-gradient-to-r from-blue-50 to-indigo-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">About Us</h1>
          <p className="text-xl text-gray-600">Leading the renewable energy revolution with premium solar solutions</p>
        </div>
      </section>

      {/* Company Story */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Story</h2>
              <p className="text-lg text-gray-600 mb-4">
                Solar E-Commerce was founded in 2020 with a mission to make renewable energy accessible to everyone. We started with a small team of solar enthusiasts and have grown into a leading provider of premium solar products and solutions.
              </p>
              <p className="text-lg text-gray-600 mb-4">
                Our journey began when our founder realized the lack of quality solar products available at competitive prices. We decided to bridge that gap by partnering with the world&apos;s leading solar manufacturers to bring you the best products at the most affordable prices.
              </p>
              <p className="text-lg text-gray-600">
                Today, we serve thousands of customers across the country, helping them transition to clean, renewable energy and reduce their carbon footprint.
              </p>
            </div>
            <div className="bg-gradient-to-br from-blue-400 to-indigo-600 rounded-lg h-96 flex items-center justify-center">
              <div className="text-white text-center">
                <div className="text-7xl mb-4">🌍</div>
                <p className="text-2xl font-bold">Sustainable Future</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-12 text-center">Our Mission & Vision</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="text-5xl mb-4">🎯</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Our Mission</h3>
              <p className="text-gray-600 text-lg">
                To make renewable solar energy affordable and accessible to everyone by providing premium products, expert knowledge, and exceptional customer service.
              </p>
            </div>
            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="text-5xl mb-4">🚀</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Our Vision</h3>
              <p className="text-gray-600 text-lg">
                To create a world powered by clean, renewable energy where every home and business can harness the power of the sun sustainably.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Core Values */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-12 text-center">Our Core Values</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <div className="text-5xl mb-4">💡</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Innovation</h3>
              <p className="text-gray-600">
                We constantly innovate to bring you the latest and most efficient solar technology available.
              </p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <div className="text-5xl mb-4">🤝</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Integrity</h3>
              <p className="text-gray-600">
                We believe in transparency, honesty, and doing business with integrity.
              </p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <div className="text-5xl mb-4">♻️</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Sustainability</h3>
              <p className="text-gray-600">
                Environmental responsibility is at the core of everything we do.
              </p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <div className="text-5xl mb-4">⭐</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Excellence</h3>
              <p className="text-gray-600">
                We strive for excellence in every product, service, and customer interaction.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Stats */}
      <section className="bg-blue-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-5xl font-bold text-white mb-2">5000+</div>
              <p className="text-blue-100 text-lg">Happy Customers</p>
            </div>
            <div>
              <div className="text-5xl font-bold text-white mb-2">10000+</div>
              <p className="text-blue-100 text-lg">Solar Panels Installed</p>
            </div>
            <div>
              <div className="text-5xl font-bold text-white mb-2">50+</div>
              <p className="text-blue-100 text-lg">Expert Team Members</p>
            </div>
            <div>
              <div className="text-5xl font-bold text-white mb-2">15+</div>
              <p className="text-blue-100 text-lg">Years Combined Experience</p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-12 text-center">Why Choose Solar E-Commerce?</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="flex gap-4">
              <div className="text-4xl flex-shrink-0">✅</div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Certified Products</h3>
                <p className="text-gray-600">All our products are certified and meet international standards for quality and safety.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-4xl flex-shrink-0">📞</div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Expert Support</h3>
                <p className="text-gray-600">Our team of solar experts is here to help you choose the right products.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-4xl flex-shrink-0">💰</div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Competitive Prices</h3>
                <p className="text-gray-600">We offer the most competitive prices on premium solar products.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-4xl flex-shrink-0">🚚</div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Fast Delivery</h3>
                <p className="text-gray-600">Quick and reliable shipping to get your products when you need them.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-4xl flex-shrink-0">🔧</div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Installation Help</h3>
                <p className="text-gray-600">We provide guidance and resources for professional installation.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-4xl flex-shrink-0">🛡️</div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Warranty Protection</h3>
                <p className="text-gray-600">Comprehensive warranties and after-sales support for all products.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-50 to-indigo-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">Ready to Go Solar?</h2>
          <p className="text-xl text-gray-600 mb-8">Join thousands of customers saving money and the environment</p>
          <Link
            href="/products"
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-12 rounded-lg transition text-lg inline-block"
          >
            Explore Products
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-bold text-lg mb-4">About</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about" className="hover:text-white">About Us</Link></li>
                <li><Link href="/contact" className="hover:text-white">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Products</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/products" className="hover:text-white">Shop</Link></li>
                <li><a href="#" className="hover:text-white">Deals</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">FAQ</a></li>
                <li><a href="#" className="hover:text-white">Help Center</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2026 Solar E-Commerce. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
