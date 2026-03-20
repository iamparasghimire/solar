'use client';

import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import {
  fetchCart,
  addToCart as apiAddToCart,
  updateCartItem as apiUpdateCartItem,
  removeCartItem as apiRemoveCartItem,
  clearCart as apiClearCart,
  type Cart,
} from '@/lib/api';
import { useAuth } from '@/lib/auth-context';

interface CartContextValue {
  cart: Cart | null;
  loading: boolean;
  totalItems: number;
  addToCart: (productId: string, quantity?: number) => Promise<void>;
  updateItem: (itemId: string, quantity: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  clear: () => Promise<void>;
  refresh: () => Promise<void>;
}

const CartContext = createContext<CartContextValue | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const { accessToken, isAuthenticated } = useAuth();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    if (!accessToken) {
      setCart(null);
      return;
    }
    setLoading(true);
    try {
      const data = await fetchCart(accessToken);
      setCart(data);
    } catch {
      setCart(null);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    if (isAuthenticated) {
      refresh();
    } else {
      setCart(null);
    }
  }, [isAuthenticated, refresh]);

  const addToCart = useCallback(
    async (productId: string, quantity = 1) => {
      if (!accessToken) return;
      const updated = await apiAddToCart({
        productId,
        quantity,
        accessToken,
      });
      setCart(updated);
    },
    [accessToken]
  );

  const updateItem = useCallback(
    async (itemId: string, quantity: number) => {
      if (!accessToken) return;
      const updated = await apiUpdateCartItem(itemId, { quantity }, accessToken);
      setCart(updated);
    },
    [accessToken]
  );

  const removeItem = useCallback(
    async (itemId: string) => {
      if (!accessToken) return;
      const updated = await apiRemoveCartItem(itemId, accessToken);
      setCart(updated);
    },
    [accessToken]
  );

  const clear = useCallback(async () => {
    if (!accessToken) return;
    const updated = await apiClearCart(accessToken);
    setCart(updated);
  }, [accessToken]);

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        totalItems: cart?.total_items ?? 0,
        addToCart,
        updateItem,
        removeItem,
        clear,
        refresh,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used inside CartProvider');
  return ctx;
}
