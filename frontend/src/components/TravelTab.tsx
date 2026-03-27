"use client";

import { useState, useEffect } from "react";
import { fetchTravelEstimate, fetchCitySuggestions, apiCreateSavedSearch } from "@/lib/api";
import type { TravelEstimate, ExchangeRate, TicketListing } from "@/lib/api";
import { detectUserCurrency, convertCurrency, formatCurrency } from "@/lib/currency";
import CurrencySelector from "@/components/CurrencySelector";
import { useAuth } from "@/lib/auth-context";

interface TravelTabProps {
  circuitId: number;
  exchangeRates: ExchangeRate[];
  tickets: TicketListing[];
}

export default function TravelTab({ circuitId, exchangeRates, tickets }: TravelTabProps) {
  const { isAuthenticated, token } = useAuth();
  const [origin, setOrigin] = useState("");
  const [groupSize, setGroupSize] = useState(2);
  const [nights, setNights] = useState(2);
  const [currency, setCurrency] = useState("USD");
  const [estimate, setEstimate] = useState<TravelEstimate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [tripSaveMsg, setTripSaveMsg] = useState<string | null>(null);

  async function handleSaveTrip() {
    if (!token) return;
    const name = window.prompt("Name this trip:");
    if (!name) return;
    try {
      await apiCreateSavedSearch(token, {
        search_type: "trip",
        name,
        data: { circuit_id: circuitId, origin, group_size: groupSize, nights },
      });
      setTripSaveMsg("Trip saved!");
      setTimeout(() => setTripSaveMsg(null), 3000);
    } catch {
      setTripSaveMsg("Failed to save");
      setTimeout(() => setTripSaveMsg(null), 3000);
    }
  }

  // Build rates lookup
  const rates: Record<string, number> = {};
  for (const r of exchangeRates) {
    rates[r.currency_code] = r.rate_from_usd;
  }

  useEffect(() => {
    setCurrency(detectUserCurrency());
    fetchCitySuggestions().then(setSuggestions).catch(() => {});
  }, []);

  function fmt(usd: number): string {
    return formatCurrency(convertCurrency(usd, rates, currency), currency);
  }

  async function handleSearch() {
    if (!origin.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchTravelEstimate(circuitId, origin.trim());
      setEstimate(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to fetch estimate");
      setEstimate(null);
    } finally {
      setLoading(false);
    }
  }

  // Convert ticket prices to USD for consistent total calculation
  // Tickets may be in different currencies — normalize using exchange rates
  const cheapestTicket = tickets.length > 0
    ? Math.min(...tickets.map((t) => {
        const ticketRate = rates[t.currency] || 1;
        return ticketRate > 0 ? t.price / ticketRate : t.price; // convert to USD
      }))
    : null;

  const filteredSuggestions = origin.length >= 2
    ? suggestions.filter((s) => s.startsWith(origin.toLowerCase())).slice(0, 8)
    : [];

  return (
    <div>
      {/* Input Section */}
      <div className="flex gap-3 flex-wrap items-end mb-6">
        <div className="relative">
          <label className="text-xs text-gray-500 block mb-1">From</label>
          <input
            type="text"
            value={origin}
            onChange={(e) => { setOrigin(e.target.value); setShowSuggestions(true); }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Enter city..."
            className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-2 w-48"
          />
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div className="absolute z-10 mt-1 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg max-h-40 overflow-y-auto">
              {filteredSuggestions.map((s) => (
                <button
                  key={s}
                  onMouseDown={() => { setOrigin(s); setShowSuggestions(false); }}
                  className="block w-full text-left px-3 py-1.5 text-sm text-gray-300 hover:bg-gray-700 capitalize"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Group Size</label>
          <select value={groupSize} onChange={(e) => setGroupSize(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-2">
            {[1,2,3,4,5,6,7,8,9,10].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Nights</label>
          <select value={nights} onChange={(e) => setNights(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-2">
            {[1,2,3,4,5].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Currency</label>
          <CurrencySelector value={currency} onChange={setCurrency} />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading || !origin.trim()}
          className="bg-red-500 hover:bg-red-600 disabled:bg-gray-700 text-white text-sm font-medium px-5 py-2 rounded-lg"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {error && <div className="text-red-400 text-sm mb-4">{error}</div>}

      {/* Results */}
      {estimate && (
        <div>
          {/* Travel Details */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Flights</div>
              {estimate.flight_price_min > 0 ? (
                <>
                  <div className="text-lg font-bold text-blue-400">
                    {fmt(estimate.flight_price_min)} – {fmt(estimate.flight_price_max)}
                  </div>
                  <div className="text-xs text-gray-400">
                    {estimate.flight_duration_hours}h · {estimate.flight_stops === 0 ? "Direct" : `${estimate.flight_stops} stop${estimate.flight_stops > 1 ? "s" : ""}`}
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-500">No flight data</div>
              )}
            </div>

            {estimate.train_available && (
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Train</div>
                <div className="text-lg font-bold text-green-400">
                  {estimate.train_price_min !== null ? fmt(estimate.train_price_min) : "—"}
                  {estimate.train_price_max !== null && estimate.train_price_max !== estimate.train_price_min
                    ? ` – ${fmt(estimate.train_price_max)}` : ""}
                </div>
                {estimate.train_duration_hours && (
                  <div className="text-xs text-gray-400">{estimate.train_duration_hours}h</div>
                )}
              </div>
            )}

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Local Transport</div>
              <div className="text-lg font-bold text-yellow-400">{fmt(estimate.local_transport_cost)}</div>
              <div className="text-xs text-gray-400">to circuit (each way)</div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Hotel</div>
              <div className="text-lg font-bold text-purple-400">{fmt(estimate.hotel_avg_per_night)}</div>
              <div className="text-xs text-gray-400">per night avg</div>
            </div>
          </div>

          {/* Total Cost Card */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 className="font-bold text-lg mb-4">Total Trip Cost Estimate</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Tickets (cheapest)</span>
                <span>{cheapestTicket ? fmt(cheapestTicket) : "N/A"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Flights (min)</span>
                <span>{estimate.flight_price_min > 0 ? fmt(estimate.flight_price_min) : "N/A"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Hotel ({nights} night{nights > 1 ? "s" : ""})</span>
                <span>{fmt(estimate.hotel_avg_per_night * nights)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Local transport (return)</span>
                <span>{fmt(estimate.local_transport_cost * 2)}</span>
              </div>
              <div className="border-t border-gray-700 pt-2 mt-2">
                <div className="flex justify-between font-bold text-lg">
                  <span>Per person</span>
                  <span className="text-green-400">
                    {fmt(
                      (cheapestTicket || 0) +
                      estimate.flight_price_min +
                      estimate.hotel_avg_per_night * nights +
                      estimate.local_transport_cost * 2
                    )}
                  </span>
                </div>
                {groupSize > 1 && (
                  <div className="flex justify-between font-bold text-lg mt-1">
                    <span>Group total ({groupSize})</span>
                    <span className="text-green-400">
                      {fmt(
                        ((cheapestTicket || 0) +
                        estimate.flight_price_min +
                        estimate.hotel_avg_per_night * nights +
                        estimate.local_transport_cost * 2) * groupSize
                      )}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Save Trip Button */}
          {isAuthenticated && (
            <div className="mt-4 flex items-center gap-3">
              <button
                onClick={handleSaveTrip}
                className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1.5 rounded"
              >
                Save Trip
              </button>
              {tripSaveMsg && <span className="text-xs text-green-400">{tripSaveMsg}</span>}
            </div>
          )}
        </div>
      )}

      {!estimate && !loading && !error && (
        <div className="text-center text-gray-500 py-12">
          Enter your origin city to see travel cost estimates
        </div>
      )}
    </div>
  );
}
