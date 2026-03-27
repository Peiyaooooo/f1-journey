import { fetchCircuits, fetchRaceEvents, fetchCitySuggestions } from "@/lib/api";
import QuizPageClient from "./QuizPageClient";

export default async function QuizPage() {
  try {
    const [circuits, events, cities] = await Promise.all([
      fetchCircuits(),
      fetchRaceEvents({ season: 2026, status: "upcoming" }),
      fetchCitySuggestions(),
    ]);

    const eventByCircuit = new Map(
      events.map((e) => [e.circuit_id, e]),
    );

    const enrichedCircuits = circuits.map((c) => {
      const event = eventByCircuit.get(c.id);
      return {
        id: c.id,
        name: c.name,
        country: c.country,
        continent: c.continent,
        overtake_difficulty: c.overtake_difficulty,
        rain_probability_pct: c.rain_probability_pct,
        atmosphere_rating: null as number | null,
        raceDate: event?.race_date ?? null,
        cheapestPrice: null as number | null,
      };
    });

    return (
      <div className="px-6 py-8">
        <h1 className="text-2xl font-bold mb-1">Find Your Perfect Race</h1>
        <p className="text-gray-400 text-sm mb-8">
          Answer 5 quick questions and we&apos;ll recommend the best circuits for you
        </p>
        <QuizPageClient circuits={enrichedCircuits} cities={cities} />
      </div>
    );
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
}
