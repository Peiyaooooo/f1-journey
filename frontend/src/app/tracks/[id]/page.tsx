// frontend/src/app/tracks/[id]/page.tsx
import { fetchCircuit, fetchRaceEvents } from "@/lib/api";
import TrackStats from "@/components/TrackStats";
import { notFound } from "next/navigation";

export default async function TrackDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const circuitId = parseInt(id, 10);
  if (isNaN(circuitId)) notFound();

  let circuit;
  try {
    circuit = await fetchCircuit(circuitId);
  } catch {
    notFound();
  }

  let raceEvents;
  try {
    raceEvents = await fetchRaceEvents({ season: 2026 });
    raceEvents = raceEvents.filter((e) => e.circuit_id === circuitId);
  } catch {
    raceEvents = [];
  }

  return (
    <div>
      {/* Header */}
      <div className="px-6 py-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold">{circuit.name}</h1>
        <p className="text-gray-400 text-sm">
          {circuit.city}, {circuit.country} &bull; {circuit.continent}
        </p>
        {circuit.nearest_airport && (
          <p className="text-gray-500 text-xs mt-1">Nearest airport: {circuit.nearest_airport}</p>
        )}
      </div>

      {/* Stats */}
      <div className="px-6 py-6">
        <h2 className="text-lg font-bold mb-4">Track Statistics</h2>
        <TrackStats
          overtakeDifficulty={circuit.overtake_difficulty}
          avgOvertakes={circuit.avg_overtakes_per_race}
          rainProbabilityPct={circuit.rain_probability_pct}
          trackLengthKm={circuit.track_length_km}
          numberOfTurns={circuit.number_of_turns}
          drsZonesCount={circuit.drs_zones_count}
          atmosphereRating={circuit.atmosphere_rating}
          trackType={circuit.track_type}
        />
      </div>

      {/* Upcoming Races */}
      {raceEvents.length > 0 && (
        <div className="px-6 py-6">
          <h2 className="text-lg font-bold mb-4">2026 Race</h2>
          {raceEvents.map((event) => (
            <div key={event.id} className="bg-gray-800 rounded-lg p-4 flex items-center justify-between">
              <div>
                <div className="font-bold">{event.race_name}</div>
                <div className="text-sm text-gray-400">
                  {new Date(event.race_date).toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })}
                </div>
              </div>
              <div className="flex gap-2">
                {event.sprint_weekend && (
                  <span className="text-xs bg-purple-500/10 text-purple-400 px-2 py-1 rounded">
                    Sprint Weekend
                  </span>
                )}
                <span className="text-xs bg-blue-500/10 text-blue-400 px-2 py-1 rounded">
                  {event.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Placeholder for future subsystems */}
      <div className="px-6 py-6 text-center text-gray-600 text-sm">
        Seat map, ticket prices, and travel planning coming in future updates.
      </div>
    </div>
  );
}
