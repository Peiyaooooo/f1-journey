"use client";

import { useState, useMemo } from "react";
import type { CircuitListItem, RaceEvent } from "@/lib/api";

interface ComparisonViewProps {
  circuits: CircuitListItem[];
  raceEvents: RaceEvent[];
  ticketMap: Record<number, number | null>;
}

function ComparisonRow({
  label,
  valueA,
  valueB,
  highlightA,
  highlightB,
}: {
  label: string;
  valueA: string;
  valueB: string;
  highlightA: boolean;
  highlightB: boolean;
}) {
  return (
    <div className="grid grid-cols-3 text-sm border-b border-gray-700 last:border-b-0">
      <div className="py-3 px-4 text-gray-400 font-medium">{label}</div>
      <div
        className={`py-3 px-4 text-center ${
          highlightA ? "bg-green-500/10 text-green-400 font-semibold" : "text-gray-200"
        }`}
      >
        {valueA}
      </div>
      <div
        className={`py-3 px-4 text-center ${
          highlightB ? "bg-green-500/10 text-green-400 font-semibold" : "text-gray-200"
        }`}
      >
        {valueB}
      </div>
    </div>
  );
}

export default function ComparisonView({
  circuits,
  raceEvents,
  ticketMap,
}: ComparisonViewProps) {
  const [circuitAId, setCircuitAId] = useState<number | null>(null);
  const [circuitBId, setCircuitBId] = useState<number | null>(null);

  const eventByCircuit = useMemo(
    () => new Map(raceEvents.map((e) => [e.circuit_id, e])),
    [raceEvents],
  );

  const circuitA = useMemo(
    () => circuits.find((c) => c.id === circuitAId) ?? null,
    [circuits, circuitAId],
  );
  const circuitB = useMemo(
    () => circuits.find((c) => c.id === circuitBId) ?? null,
    [circuits, circuitBId],
  );

  const eventA = circuitA ? eventByCircuit.get(circuitA.id) ?? null : null;
  const eventB = circuitB ? eventByCircuit.get(circuitB.id) ?? null : null;

  const selectClass =
    "w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 focus:outline-none focus:border-green-500";

  const formatDate = (date: string | undefined | null) => {
    if (!date) return "TBD";
    return new Date(date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const bothSelected = circuitA && circuitB;

  return (
    <div>
      {/* Selectors */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <div>
          <label className="text-xs text-gray-400 mb-1 block">Circuit A</label>
          <select
            value={circuitAId ?? ""}
            onChange={(e) =>
              setCircuitAId(e.target.value ? Number(e.target.value) : null)
            }
            className={selectClass}
          >
            <option value="">Select a circuit...</option>
            {circuits.map((c) => (
              <option key={c.id} value={c.id} disabled={c.id === circuitBId}>
                {c.name} ({c.country})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-400 mb-1 block">Circuit B</label>
          <select
            value={circuitBId ?? ""}
            onChange={(e) =>
              setCircuitBId(e.target.value ? Number(e.target.value) : null)
            }
            className={selectClass}
          >
            <option value="">Select a circuit...</option>
            {circuits.map((c) => (
              <option key={c.id} value={c.id} disabled={c.id === circuitAId}>
                {c.name} ({c.country})
              </option>
            ))}
          </select>
        </div>
      </div>

      {!bothSelected && (
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg">Select two circuits to compare</p>
          <p className="text-sm mt-1">
            Use the dropdowns above to pick your circuits
          </p>
        </div>
      )}

      {bothSelected && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          {/* Header */}
          <div className="grid grid-cols-3 border-b border-gray-700 bg-gray-900">
            <div className="py-3 px-4 text-xs text-gray-500 uppercase tracking-wider">
              Stat
            </div>
            <div className="py-3 px-4 text-center font-bold text-sm text-gray-100">
              {circuitA.name}
            </div>
            <div className="py-3 px-4 text-center font-bold text-sm text-gray-100">
              {circuitB.name}
            </div>
          </div>

          {/* Rows */}
          {(() => {
            const overtakeA = 10 - circuitA.overtake_difficulty;
            const overtakeB = 10 - circuitB.overtake_difficulty;
            const rainA = circuitA.rain_probability_pct;
            const rainB = circuitB.rain_probability_pct;
            const avgOvertakesA = circuitA.avg_overtakes_per_race;
            const avgOvertakesB = circuitB.avg_overtakes_per_race;
            const priceA = ticketMap[circuitA.id] ?? null;
            const priceB = ticketMap[circuitB.id] ?? null;

            return (
              <>
                <ComparisonRow
                  label="Overtaking"
                  valueA={`${overtakeA}/10`}
                  valueB={`${overtakeB}/10`}
                  highlightA={overtakeA > overtakeB}
                  highlightB={overtakeB > overtakeA}
                />
                <ComparisonRow
                  label="Rain Risk"
                  valueA={`${rainA}%`}
                  valueB={`${rainB}%`}
                  highlightA={rainA < rainB}
                  highlightB={rainB < rainA}
                />
                <ComparisonRow
                  label="Track Type"
                  valueA={circuitA.track_type === "street" ? "Street" : "Permanent"}
                  valueB={circuitB.track_type === "street" ? "Street" : "Permanent"}
                  highlightA={false}
                  highlightB={false}
                />
                <ComparisonRow
                  label="Avg Overtakes"
                  valueA={String(avgOvertakesA)}
                  valueB={String(avgOvertakesB)}
                  highlightA={avgOvertakesA > avgOvertakesB}
                  highlightB={avgOvertakesB > avgOvertakesA}
                />
                <ComparisonRow
                  label="Race Date"
                  valueA={formatDate(eventA?.race_date)}
                  valueB={formatDate(eventB?.race_date)}
                  highlightA={false}
                  highlightB={false}
                />
                <ComparisonRow
                  label="Sprint Weekend"
                  valueA={eventA?.sprint_weekend ? "Yes" : "No"}
                  valueB={eventB?.sprint_weekend ? "Yes" : "No"}
                  highlightA={false}
                  highlightB={false}
                />
                <ComparisonRow
                  label="Cheapest Ticket"
                  valueA={priceA !== null ? `$${priceA.toLocaleString()}` : "N/A"}
                  valueB={priceB !== null ? `$${priceB.toLocaleString()}` : "N/A"}
                  highlightA={
                    priceA !== null && priceB !== null && priceA < priceB
                  }
                  highlightB={
                    priceA !== null && priceB !== null && priceB < priceA
                  }
                />
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}
