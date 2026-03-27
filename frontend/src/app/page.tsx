// frontend/src/app/page.tsx
import RaceCard from "@/components/RaceCard";
import { fetchCircuits, fetchRaceEvents } from "@/lib/api";

export default async function Home() {
  let circuits;
  let raceEvents;

  try {
    [circuits, raceEvents] = await Promise.all([
      fetchCircuits(),
      fetchRaceEvents({ season: 2026, status: "upcoming" }),
    ]);
  } catch {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">Unable to connect to API</h2>
          <p className="text-gray-400">Make sure the backend is running on port 8000</p>
        </div>
      </div>
    );
  }

  const circuitMap = Object.fromEntries(circuits.map((c) => [c.id, c]));

  return (
    <div>
      {/* Hero */}
      <div className="px-6 py-8 bg-gradient-to-br from-indigo-950 to-gray-950">
        <h1 className="text-2xl font-bold mb-1">Find your perfect F1 weekend</h1>
        <p className="text-gray-400 text-sm">
          Compare tracks, seats, and travel costs across every Grand Prix
        </p>
      </div>

      {/* Upcoming Races */}
      <div className="px-6 py-6">
        <h2 className="text-lg font-bold mb-4">Upcoming Races — 2026</h2>
        <div className="flex gap-3 overflow-x-auto pb-2">
          {raceEvents.map((event) => {
            const circuit = circuitMap[event.circuit_id];
            if (!circuit) return null;
            return (
              <RaceCard
                key={event.id}
                circuitId={circuit.id}
                raceName={event.race_name}
                circuitName={circuit.name}
                country={circuit.country}
                raceDate={event.race_date}
                trackType={circuit.track_type}
                overtakeDifficulty={circuit.overtake_difficulty}
                rainProbabilityPct={circuit.rain_probability_pct}
                sprintWeekend={event.sprint_weekend}
              />
            );
          })}
        </div>
      </div>

      {/* All Circuits Table */}
      <div className="px-6 py-6">
        <h2 className="text-lg font-bold mb-4">All Circuits</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400 text-left">
                <th className="pb-2 pr-4">Circuit</th>
                <th className="pb-2 pr-4">Country</th>
                <th className="pb-2 pr-4">Continent</th>
                <th className="pb-2 pr-4">Type</th>
                <th className="pb-2 pr-4">Overtaking</th>
                <th className="pb-2 pr-4">Avg Overtakes</th>
                <th className="pb-2">Rain %</th>
              </tr>
            </thead>
            <tbody>
              {circuits.map((circuit) => (
                <tr key={circuit.id} className="border-b border-gray-800/50 hover:bg-gray-900">
                  <td className="py-2 pr-4">
                    <a href={`/tracks/${circuit.id}`} className="text-blue-400 hover:underline">
                      {circuit.name}
                    </a>
                  </td>
                  <td className="py-2 pr-4 text-gray-400">{circuit.country}</td>
                  <td className="py-2 pr-4 text-gray-400">{circuit.continent}</td>
                  <td className="py-2 pr-4">
                    <span className={`text-xs px-2 py-0.5 rounded ${circuit.track_type === "street" ? "bg-yellow-500/10 text-yellow-500" : "bg-green-500/10 text-green-500"}`}>
                      {circuit.track_type}
                    </span>
                  </td>
                  <td className="py-2 pr-4">{10 - circuit.overtake_difficulty}/10</td>
                  <td className="py-2 pr-4">{circuit.avg_overtakes_per_race}</td>
                  <td className="py-2">{circuit.rain_probability_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
