"use client";

import { useState, useEffect } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/auth-context";

const CURRENCIES = ["USD", "EUR", "GBP", "AUD", "CAD", "JPY", "CHF", "SGD", "AED", "BRL", "MXN"];
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}

function SettingsContent() {
  const { user, token } = useAuth();
  const [homeCity, setHomeCity] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [pwMsg, setPwMsg] = useState<string | null>(null);
  const [pwSaving, setPwSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setHomeCity(user.home_city || "");
      setCurrency(user.preferred_currency || "USD");
    }
  }, [user]);

  async function handleSaveProfile(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    setSaving(true);
    setMsg(null);
    try {
      const res = await fetch(`${API_URL}/api/auth/me`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ home_city: homeCity || null, preferred_currency: currency }),
      });
      if (!res.ok) throw new Error("Failed to update");
      setMsg("Settings saved!");
    } catch {
      setMsg("Failed to save settings");
    } finally {
      setSaving(false);
    }
  }

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault();
    setPwMsg(null);
    if (newPassword !== confirmPassword) {
      setPwMsg("Passwords do not match");
      return;
    }
    if (newPassword.length < 6) {
      setPwMsg("Password must be at least 6 characters");
      return;
    }
    if (!token) return;
    setPwSaving(true);
    try {
      const res = await fetch(`${API_URL}/api/auth/change-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to change password");
      }
      setPwMsg("Password changed successfully!");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: unknown) {
      setPwMsg(err instanceof Error ? err.message : "Failed to change password");
    } finally {
      setPwSaving(false);
    }
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-8">Settings</h1>

      {/* Profile Section */}
      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-4">Profile</h2>
        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div>
            <label className="text-sm text-gray-400 block mb-1">Email</label>
            <input
              type="email"
              value={user?.email || ""}
              disabled
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-500 cursor-not-allowed"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Home City</label>
            <input
              type="text"
              value={homeCity}
              onChange={(e) => setHomeCity(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-gray-500"
              placeholder="e.g. London"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Preferred Currency</label>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-gray-500"
            >
              {CURRENCIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={saving}
              className="bg-red-500 hover:bg-red-600 disabled:bg-gray-700 text-white font-medium py-2 px-5 rounded-lg text-sm"
            >
              {saving ? "Saving..." : "Save"}
            </button>
            {msg && <span className="text-sm text-green-400">{msg}</span>}
          </div>
        </form>
      </section>

      {/* Change Password Section */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Change Password</h2>
        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="text-sm text-gray-400 block mb-1">Current Password</label>
            <input
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-gray-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">New Password</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-gray-500"
              placeholder="At least 6 characters"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Confirm New Password</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-gray-500"
            />
          </div>
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={pwSaving}
              className="bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-5 rounded-lg text-sm"
            >
              {pwSaving ? "Changing..." : "Change Password"}
            </button>
            {pwMsg && (
              <span className={`text-sm ${pwMsg.includes("success") ? "text-green-400" : "text-red-400"}`}>
                {pwMsg}
              </span>
            )}
          </div>
        </form>
      </section>
    </div>
  );
}
