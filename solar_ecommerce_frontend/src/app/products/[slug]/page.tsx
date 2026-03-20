'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { fetchProductBySlug, fetchRelatedProducts, type ProductDetail, type Product } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useCart } from '@/lib/cart-context';

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
});

function toNumber(v: string | number) {
  return typeof v === 'number' ? v : Number(v);
}

export default function ProductDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const { isAuthenticated } = useAuth();
  const { addToCart } = useCart();

  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [related, setRelated] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [includeInstallation, setIncludeInstallation] = useState(false);
  const [addedMessage, setAddedMessage] = useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchProductBySlug(slug)
      .then((data) => {
        setProduct(data);
        const primaryImg = data.images?.find((i) => i.is_primary)?.image || data.images?.[0]?.image || null;
        setSelectedImage(primaryImg);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));

    fetchRelatedProducts(slug)
      .then(setRelated)
      .catch(() => setRelated([]));
  }, [slug]);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      setAddedMessage('Please login to add products to cart.');
      return;
    }
    try {
      await addToCart(product!.id, quantity);
      setAddedMessage(`${quantity}x "${product!.name}" added to cart!`);
      setTimeout(() => setAddedMessage(''), 3000);
    } catch (err) {
      setAddedMessage(err instanceof Error ? err.message : 'Failed to add to cart.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading product...</p>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-xl mb-4">{error || 'Product not found'}</p>
          <Link href="/products" className="text-blue-600 hover:underline">
            ← Back to Products
          </Link>
        </div>
      </div>
    );
  }

  const originalPrice = toNumber(product.price);
  const discountedPrice = toNumber(product.discounted_price);
  const discount = toNumber(product.discount_percent);
  const installFee = toNumber(product.installation_fee);

  return (
    <div className="min-h-screen bg-white">
      {/* Breadcrumb */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <nav className="text-sm text-gray-500">
          <Link href="/" className="hover:text-blue-600">Home</Link>
          <span className="mx-2">/</span>
          <Link href="/products" className="hover:text-blue-600">Products</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">{product.name}</span>
        </nav>
      </div>

      {/* Product */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="grid md:grid-cols-2 gap-12">
          {/* Images */}
          <div>
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg h-96 flex items-center justify-center overflow-hidden border border-gray-200">
              {selectedImage ? (
                <img src={selectedImage} alt={product.name} className="w-full h-full object-contain p-4" />
              ) : (
                <div className="text-8xl">☀️</div>
              )}
            </div>
            {product.images && product.images.length > 1 && (
              <div className="flex gap-3 mt-4">
                {product.images.map((img) => (
                  <button
                    key={img.id}
                    onClick={() => setSelectedImage(img.image)}
                    className={`w-20 h-20 rounded-lg overflow-hidden border-2 transition ${
                      selectedImage === img.image ? 'border-blue-600' : 'border-gray-200 hover:border-gray-400'
                    }`}
                  >
                    <img src={img.image} alt={img.alt_text} className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Details */}
          <div>
            <p className="text-sm text-blue-600 font-bold uppercase mb-2">{product.category_name}</p>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>

            <div className="flex items-center gap-2 mb-4">
              <span className="text-yellow-500">★</span>
              <span className="font-bold">{product.average_rating}</span>
              <span className="text-gray-500">({product.review_count} reviews)</span>
              {product.brand && (
                <>
                  <span className="text-gray-300 mx-2">|</span>
                  <span className="text-gray-600">Brand: {product.brand}</span>
                </>
              )}
            </div>

            {/* Price */}
            <div className="mb-6">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold text-blue-600">{currency.format(discountedPrice)}</span>
                {discount > 0 && (
                  <>
                    <span className="text-lg text-gray-400 line-through">{currency.format(originalPrice)}</span>
                    <span className="bg-green-100 text-green-800 text-sm font-bold px-2 py-1 rounded">
                      {discount}% OFF
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Specs */}
            <div className="grid grid-cols-2 gap-4 mb-6 bg-gray-50 rounded-lg p-4">
              {product.capacity && (
                <div>
                  <span className="text-xs text-gray-500 block">Capacity</span>
                  <span className="font-bold text-gray-900">{product.capacity}</span>
                </div>
              )}
              <div>
                <span className="text-xs text-gray-500 block">Warranty</span>
                <span className="font-bold text-gray-900">{product.warranty_years} years</span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block">Delivery</span>
                <span className="font-bold text-gray-900">{product.delivery_days} days</span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block">Stock</span>
                <span className={`font-bold ${product.in_stock ? 'text-green-600' : 'text-red-600'}`}>
                  {product.in_stock ? `${product.stock} available` : 'Out of Stock'}
                </span>
              </div>
            </div>

            {/* Quantity */}
            <div className="mb-4">
              <label className="block text-sm font-bold text-gray-900 mb-2">Quantity</label>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                  className="w-10 h-10 rounded-lg border border-gray-300 flex items-center justify-center hover:bg-gray-50 text-lg font-bold"
                >
                  −
                </button>
                <span className="w-12 text-center font-bold text-lg">{quantity}</span>
                <button
                  onClick={() => setQuantity((q) => Math.min(product.stock, q + 1))}
                  className="w-10 h-10 rounded-lg border border-gray-300 flex items-center justify-center hover:bg-gray-50 text-lg font-bold"
                >
                  +
                </button>
              </div>
            </div>

            {/* Installation */}
            {product.installation_available && installFee > 0 && (
              <label className="flex items-center gap-3 mb-6 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeInstallation}
                  onChange={(e) => setIncludeInstallation(e.target.checked)}
                  className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-gray-700">
                  Include installation (+{currency.format(installFee)} per unit)
                </span>
              </label>
            )}

            {/* Add to Cart */}
            <button
              onClick={handleAddToCart}
              disabled={!product.in_stock}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 px-6 rounded-lg transition text-lg mb-3"
            >
              {product.in_stock ? 'Add to Cart' : 'Out of Stock'}
            </button>

            {addedMessage && (
              <p className={`text-sm mb-4 ${addedMessage.includes('login') ? 'text-amber-600' : 'text-green-600'}`}>
                {addedMessage}
              </p>
            )}

            {!isAuthenticated && (
              <p className="text-sm text-gray-500">
                <Link href="/login" className="text-blue-600 hover:underline">Login</Link> to add products to your cart.
              </p>
            )}

            {/* Description */}
            {product.description && (
              <div className="mt-8 border-t border-gray-200 pt-6">
                <h2 className="text-xl font-bold text-gray-900 mb-3">Description</h2>
                <p className="text-gray-600 whitespace-pre-line">{product.description}</p>
              </div>
            )}

            {product.technical_description && (
              <div className="mt-6 border-t border-gray-200 pt-6">
                <h2 className="text-xl font-bold text-gray-900 mb-3">Technical Specifications</h2>
                <p className="text-gray-600 whitespace-pre-line">{product.technical_description}</p>
              </div>
            )}
          </div>
        </div>

        {/* Related Products */}
        {related.length > 0 && (
          <div className="mt-16 border-t border-gray-200 pt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Related Products</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {related.map((p) => (
                <Link
                  key={p.id}
                  href={`/products/${p.slug}`}
                  className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition group"
                >
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 h-40 flex items-center justify-center overflow-hidden">
                    {p.primary_image ? (
                      <img src={p.primary_image} alt={p.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="text-4xl">☀️</div>
                    )}
                  </div>
                  <div className="p-4">
                    <p className="text-xs text-gray-500 font-bold uppercase">{p.category_name}</p>
                    <h3 className="font-bold text-gray-900 group-hover:text-blue-600 transition">{p.name}</h3>
                    <p className="text-blue-600 font-bold mt-1">{currency.format(toNumber(p.discounted_price))}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
