'use client';

import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import {
  login as apiLogin,
  register as apiRegister,
  fetchProfile,
  refreshToken as apiRefreshToken,
  type AuthTokens,
  type UserProfile,
} from '@/lib/api';

interface AuthState {
  user: UserProfile | null;
  accessToken: string;
  refreshTokenStr: string;
  loading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    username: string;
    phone_number?: string;
    password: string;
    password2: string;
  }) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const STORAGE_KEYS = {
  access: 'solar_access_token',
  refresh: 'solar_refresh_token',
} as const;

function saveTokens(tokens: AuthTokens) {
  localStorage.setItem(STORAGE_KEYS.access, tokens.access);
  localStorage.setItem(STORAGE_KEYS.refresh, tokens.refresh);
}

function clearTokens() {
  localStorage.removeItem(STORAGE_KEYS.access);
  localStorage.removeItem(STORAGE_KEYS.refresh);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: '',
    refreshTokenStr: '',
    loading: true,
  });

  // Boot: try to restore session
  useEffect(() => {
    const access = localStorage.getItem(STORAGE_KEYS.access) || '';
    const refresh = localStorage.getItem(STORAGE_KEYS.refresh) || '';

    if (!access) {
      setState((s) => ({ ...s, loading: false }));
      return;
    }

    fetchProfile(access)
      .then((user) => {
        setState({ user, accessToken: access, refreshTokenStr: refresh, loading: false });
      })
      .catch(async () => {
        // Try refresh
        if (refresh) {
          try {
            const res = await apiRefreshToken(refresh);
            const newAccess = res.access;
            localStorage.setItem(STORAGE_KEYS.access, newAccess);
            const user = await fetchProfile(newAccess);
            setState({ user, accessToken: newAccess, refreshTokenStr: refresh, loading: false });
            return;
          } catch {
            // fall through
          }
        }
        clearTokens();
        setState({ user: null, accessToken: '', refreshTokenStr: '', loading: false });
      });
  }, []);

  const loginFn = useCallback(async (email: string, password: string) => {
    const tokens = await apiLogin(email, password);
    saveTokens(tokens);
    const user = await fetchProfile(tokens.access);
    setState({ user, accessToken: tokens.access, refreshTokenStr: tokens.refresh, loading: false });
  }, []);

  const registerFn = useCallback(
    async (data: {
      email: string;
      username: string;
      phone_number?: string;
      password: string;
      password2: string;
    }) => {
      const res = await apiRegister(data);
      saveTokens(res.tokens);
      setState({
        user: res.user,
        accessToken: res.tokens.access,
        refreshTokenStr: res.tokens.refresh,
        loading: false,
      });
    },
    []
  );

  const logout = useCallback(() => {
    clearTokens();
    setState({ user: null, accessToken: '', refreshTokenStr: '', loading: false });
  }, []);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login: loginFn,
        register: registerFn,
        logout,
        isAuthenticated: !!state.user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
