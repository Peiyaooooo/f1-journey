"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-gray-950">
      <div className="flex items-center gap-8">
        <Link href="/" className="text-lg font-bold text-red-500">
          F1 Journey
        </Link>
        <Link href="/explore" className="text-sm text-gray-400 hover:text-white">Explore</Link>
        <Link href="/quiz" className="text-sm text-gray-400 hover:text-white">Quiz</Link>
        <Link href="/compare" className="text-sm text-gray-400 hover:text-white">Compare</Link>
      </div>
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search tracks..."
          className="bg-gray-800 text-sm text-gray-300 px-3 py-1.5 rounded-md w-48 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-600"
          readOnly
        />
        {isAuthenticated ? (
          <>
            <span className="text-xs text-gray-400 hidden sm:inline">{user?.email}</span>
            <Link href="/dashboard" className="text-sm text-gray-400 hover:text-white">Dashboard</Link>
            <button
              onClick={logout}
              className="text-sm text-gray-400 hover:text-white"
            >
              Logout
            </button>
          </>
        ) : (
          <Link href="/login" className="text-sm text-gray-400 hover:text-white">Login</Link>
        )}
      </div>
    </nav>
  );
}
