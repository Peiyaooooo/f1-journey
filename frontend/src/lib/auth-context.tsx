"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { apiLogin, apiRegister, apiGetMe, type User, type TokenResponse } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, homeCity?: string, currency?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("f1_token");
    if (stored) {
      setToken(stored);
      apiGetMe(stored).then(setUser).catch(() => { localStorage.removeItem("f1_token"); setToken(null); });
    }
  }, []);

  async function login(email: string, password: string) {
    const resp = await apiLogin(email, password);
    localStorage.setItem("f1_token", resp.access_token);
    localStorage.setItem("f1_refresh", resp.refresh_token);
    setToken(resp.access_token);
    const me = await apiGetMe(resp.access_token);
    setUser(me);
  }

  async function register(email: string, password: string, homeCity?: string, currency?: string) {
    const resp = await apiRegister(email, password, homeCity, currency);
    localStorage.setItem("f1_token", resp.access_token);
    localStorage.setItem("f1_refresh", resp.refresh_token);
    setToken(resp.access_token);
    const me = await apiGetMe(resp.access_token);
    setUser(me);
  }

  function logout() {
    localStorage.removeItem("f1_token");
    localStorage.removeItem("f1_refresh");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
