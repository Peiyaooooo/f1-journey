export const dynamic = "force-dynamic";

import ComparisonView from "@/components/ComparisonView";
import { fetchCircuits, fetchRaceEvents } from "@/lib/api";

export default async function ComparePage() {
  try {
    const [circuits, events] = await Promise.all([
      fetchCircuits(),
      fetchRaceEvents({ season: 2026, status: "upcoming" }),
    ]);

    // Pass empty ticket map — prices shown as N/A, users can visit track detail for pricing
    const ticketMap: Record<number, number | null> = {};

    return (
      <div className="px-6 py-8">
        <h1 className="text-2xl font-bold mb-1">Compare Circuits</h1>
        <p className="text-gray-400 text-sm mb-6">
          Select two circuits to see how they stack up side by side
        </p>
        <ComparisonView
          circuits={circuits}
          raceEvents={events}
          ticketMap={ticketMap}
        />
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
