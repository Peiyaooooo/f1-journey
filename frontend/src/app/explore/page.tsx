// frontend/src/app/explore/page.tsx
import ExploreClient from "@/components/ExploreClient";
import type { EnrichedCircuit } from "@/components/ExploreClient";
import { fetchCircuits, fetchRaceEvents } from "@/lib/api";

export default async function ExplorePage() {
  let enrichedCircuits: EnrichedCircuit[] = [];

  try {
    const [circuits, events] = await Promise.all([
      fetchCircuits(),
      fetchRaceEvents({ season: 2026, status: "upcoming" }),
    ]);

    // Build a map of circuit_id -> race event for date + sprint info
    const eventByCircuit = new Map(
      events.map((e) => [e.circuit_id, e]),
    );

    enrichedCircuits = circuits.map((c) => {
      const event = eventByCircuit.get(c.id);
      return {
        id: c.id,
        name: c.name,
        country: c.country,
        continent: c.continent,
        trackType: c.track_type,
        overtakeDifficulty: c.overtake_difficulty,
        rainProbabilityPct: c.rain_probability_pct,
        raceDate: event?.race_date ?? null,
        sprintWeekend: event?.sprint_weekend ?? false,
        cheapestTicketPrice: null, // Skipping per-circuit ticket fetch for performance
      };
    });
  } catch {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">Unable to connect to API</h2>
          <p className="text-gray-400">
            Make sure the backend is running on port 8000
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-6 py-8">
      <h1 className="text-2xl font-bold mb-1">Explore Circuits</h1>
      <p className="text-gray-400 text-sm mb-6">
        Browse and filter every circuit on the 2026 F1 calendar
      </p>
      <ExploreClient circuits={enrichedCircuits} />
    </div>
  );
}
