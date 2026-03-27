"use client";

import { useEffect, useState } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import SavedSearchCard from "@/components/SavedSearchCard";
import PriceAlertCard from "@/components/PriceAlertCard";
import { useAuth } from "@/lib/auth-context";
import { apiGetSavedSearches, apiDeleteSavedSearch, apiGetPriceAlerts, apiDeletePriceAlert } from "@/lib/api";

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const { user, token } = useAuth();
  const [searches, setSearches] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loadingSearches, setLoadingSearches] = useState(true);
  const [loadingAlerts, setLoadingAlerts] = useState(true);

  useEffect(() => {
    if (!token) return;
    apiGetSavedSearches(token)
      .then(setSearches)
      .catch(() => {})
      .finally(() => setLoadingSearches(false));
    apiGetPriceAlerts(token)
      .then(setAlerts)
      .catch(() => {})
      .finally(() => setLoadingAlerts(false));
  }, [token]);

  async function handleDeleteSearch(id: number) {
    if (!token) return;
    await apiDeleteSavedSearch(token, id);
    setSearches((prev) => prev.filter((s) => s.id !== id));
  }

  async function handleDeleteAlert(id: number) {
    if (!token) return;
    await apiDeletePriceAlert(token, id);
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-1">Dashboard</h1>
      <p className="text-gray-400 text-sm mb-8">Welcome back, {user?.email}</p>

      {/* Saved Searches */}
      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-4">Saved Searches</h2>
        {loadingSearches ? (
          <div className="text-gray-500 text-sm">Loading...</div>
        ) : searches.length === 0 ? (
          <div className="bg-gray-800/50 rounded-lg p-6 text-center text-gray-500 text-sm">
            No saved searches yet. Use the Explore page to save filter searches or the Travel tab to save trips.
          </div>
        ) : (
          <div className="space-y-2">
            {searches.map((s) => (
              <SavedSearchCard
                key={s.id}
                id={s.id}
                name={s.name}
                search_type={s.search_type}
                data={typeof s.data === "string" ? JSON.parse(s.data) : s.data}
                created_at={s.created_at}
                onDelete={handleDeleteSearch}
              />
            ))}
          </div>
        )}
      </section>

      {/* Price Alerts */}
      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-4">Price Alerts</h2>
        {loadingAlerts ? (
          <div className="text-gray-500 text-sm">Loading...</div>
        ) : alerts.length === 0 ? (
          <div className="bg-gray-800/50 rounded-lg p-6 text-center text-gray-500 text-sm">
            No price alerts yet. Browse track tickets and set alerts to get notified when prices drop.
          </div>
        ) : (
          <div className="space-y-2">
            {alerts.map((a) => (
              <PriceAlertCard
                key={a.id}
                id={a.id}
                circuit_id={a.circuit_id}
                circuit_name={a.circuit_name}
                seat_section_id={a.seat_section_id}
                section_name={a.section_name}
                target_price={a.target_price}
                is_active={a.is_active}
                triggered_at={a.triggered_at}
                onDelete={handleDeleteAlert}
              />
            ))}
          </div>
        )}
      </section>

      {/* Google Calendar */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Google Calendar</h2>
        <div className="bg-gray-800/50 rounded-lg p-6 text-center">
          <p className="text-gray-400 text-sm mb-3">
            Connect your Google Calendar to add race events directly to your schedule.
          </p>
          <button
            disabled
            className="bg-gray-700 text-gray-400 text-sm font-medium px-4 py-2 rounded-lg cursor-not-allowed"
          >
            Connect Google Calendar (Coming Soon)
          </button>
        </div>
      </section>
    </div>
  );
}
