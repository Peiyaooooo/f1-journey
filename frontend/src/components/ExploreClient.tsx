"use client";

import { useMemo, useState } from "react";
import CircuitCard from "@/components/CircuitCard";

export interface EnrichedCircuit {
  id: number;
  name: string;
  country: string;
  continent: string;
  trackType: string;
  overtakeDifficulty: number;
  rainProbabilityPct: number;
  raceDate: string | null;
  sprintWeekend: boolean;
  cheapestTicketPrice: number | null;
}

interface ExploreClientProps {
  circuits: EnrichedCircuit[];
}

type SortField = "name" | "overtaking" | "rain" | "date";

export default function ExploreClient({ circuits }: ExploreClientProps) {
  const [continentFilter, setContinentFilter] = useState("");
  const [trackTypeFilter, setTrackTypeFilter] = useState("");
  const [minOvertaking, setMinOvertaking] = useState(0);
  const [maxRain, setMaxRain] = useState(100);
  const [sortBy, setSortBy] = useState<SortField>("date");

  // Derive unique continents from data
  const continents = useMemo(
    () => [...new Set(circuits.map((c) => c.continent))].sort(),
    [circuits],
  );

  const filtered = useMemo(() => {
    let result = circuits;

    if (continentFilter) {
      result = result.filter((c) => c.continent === continentFilter);
    }
    if (trackTypeFilter) {
      result = result.filter((c) => c.trackType === trackTypeFilter);
    }
    result = result.filter(
      (c) => 10 - c.overtakeDifficulty >= minOvertaking,
    );
    result = result.filter((c) => c.rainProbabilityPct <= maxRain);

    // Sort
    result = [...result].sort((a, b) => {
      switch (sortBy) {
        case "name":
          return a.name.localeCompare(b.name);
        case "overtaking":
          return a.overtakeDifficulty - b.overtakeDifficulty; // lower difficulty = better overtaking, sort first
        case "rain":
          return a.rainProbabilityPct - b.rainProbabilityPct;
        case "date": {
          if (!a.raceDate && !b.raceDate) return 0;
          if (!a.raceDate) return 1;
          if (!b.raceDate) return -1;
          return (
            new Date(a.raceDate).getTime() - new Date(b.raceDate).getTime()
          );
        }
        default:
          return 0;
      }
    });

    return result;
  }, [
    circuits,
    continentFilter,
    trackTypeFilter,
    minOvertaking,
    maxRain,
    sortBy,
  ]);

  const selectClass =
    "bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-gray-500";

  return (
    <div>
      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        {/* Continent */}
        <select
          value={continentFilter}
          onChange={(e) => setContinentFilter(e.target.value)}
          className={selectClass}
        >
          <option value="">All Continents</option>
          {continents.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        {/* Track Type */}
        <select
          value={trackTypeFilter}
          onChange={(e) => setTrackTypeFilter(e.target.value)}
          className={selectClass}
        >
          <option value="">All Track Types</option>
          <option value="permanent">Permanent</option>
          <option value="street">Street</option>
        </select>

        {/* Min Overtaking */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-400 whitespace-nowrap">
            Min Overtaking
          </label>
          <select
            value={minOvertaking}
            onChange={(e) => setMinOvertaking(Number(e.target.value))}
            className={selectClass}
          >
            {Array.from({ length: 11 }, (_, i) => (
              <option key={i} value={i}>
                {i}/10
              </option>
            ))}
          </select>
        </div>

        {/* Max Rain */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-400 whitespace-nowrap">
            Max Rain
          </label>
          <select
            value={maxRain}
            onChange={(e) => setMaxRain(Number(e.target.value))}
            className={selectClass}
          >
            {[10, 20, 30, 40, 50, 60, 70, 80, 90, 100].map((v) => (
              <option key={v} value={v}>
                {v}%
              </option>
            ))}
          </select>
        </div>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortField)}
          className={selectClass}
        >
          <option value="date">Sort: Date</option>
          <option value="name">Sort: Name</option>
          <option value="overtaking">Sort: Overtaking</option>
          <option value="rain">Sort: Rain %</option>
        </select>
      </div>

      {/* Count */}
      <p className="text-sm text-gray-400 mb-4">
        Showing {filtered.length} of {circuits.length} circuits
      </p>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((c) => (
          <CircuitCard
            key={c.id}
            id={c.id}
            name={c.name}
            country={c.country}
            continent={c.continent}
            trackType={c.trackType}
            overtakeDifficulty={c.overtakeDifficulty}
            rainProbabilityPct={c.rainProbabilityPct}
            raceDate={c.raceDate}
            sprintWeekend={c.sprintWeekend}
            cheapestTicketPrice={c.cheapestTicketPrice}
          />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No circuits match your filters. Try adjusting the criteria.
        </div>
      )}
    </div>
  );
}
