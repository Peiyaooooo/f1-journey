// frontend/src/components/TrackStats.tsx
interface TrackStatsProps {
  overtakeDifficulty: number;
  avgOvertakes: number;
  rainProbabilityPct: number;
  trackLengthKm: number;
  numberOfTurns: number;
  drsZonesCount: number;
  atmosphereRating: number | null;
  trackType: string;
}

export default function TrackStats({
  overtakeDifficulty,
  avgOvertakes,
  rainProbabilityPct,
  trackLengthKm,
  numberOfTurns,
  drsZonesCount,
  atmosphereRating,
  trackType,
}: TrackStatsProps) {
  const stats = [
    { label: "Overtaking", value: `${10 - overtakeDifficulty}/10`, color: "text-yellow-400" },
    { label: "Avg Overtakes", value: String(avgOvertakes), color: "text-green-400" },
    { label: "Rain Risk", value: `${rainProbabilityPct}%`, color: rainProbabilityPct >= 40 ? "text-red-400" : "text-blue-400" },
    { label: "Length", value: `${trackLengthKm} km`, color: "text-blue-400" },
    { label: "Turns", value: String(numberOfTurns), color: "text-gray-300" },
    { label: "DRS Zones", value: String(drsZonesCount), color: "text-green-400" },
    { label: "Type", value: trackType === "street" ? "Street" : "Permanent", color: "text-gray-300" },
    ...(atmosphereRating ? [{ label: "Atmosphere", value: `${atmosphereRating}/5`, color: "text-yellow-400" }] : []),
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-gray-800 rounded-lg p-3 text-center">
          <div className={`text-xl font-bold ${stat.color}`}>{stat.value}</div>
          <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}
