// frontend/src/components/RaceCard.tsx
import Link from "next/link";

interface RaceCardProps {
  circuitId: number;
  raceName: string;
  circuitName: string;
  country: string;
  raceDate: string;
  trackType: string;
  overtakeDifficulty: number;
  rainProbabilityPct: number;
  sprintWeekend: boolean;
}

function overtakeColor(difficulty: number): string {
  if (difficulty <= 3) return "text-green-400";
  if (difficulty <= 6) return "text-yellow-400";
  return "text-red-400";
}

function rainColor(pct: number): string {
  if (pct >= 40) return "text-red-400";
  if (pct >= 20) return "text-blue-400";
  return "text-green-400";
}

export default function RaceCard({
  circuitId,
  raceName,
  circuitName,
  country,
  raceDate,
  trackType,
  overtakeDifficulty,
  rainProbabilityPct,
  sprintWeekend,
}: RaceCardProps) {
  const dateStr = new Date(raceDate).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  const typeColor = trackType === "street" ? "bg-yellow-500/10 text-yellow-500" : "bg-green-500/10 text-green-500";

  return (
    <Link href={`/tracks/${circuitId}`}>
      <div className="min-w-[220px] bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-gray-500 transition-colors cursor-pointer">
        <div className="flex items-center justify-between mb-2">
          <span className="font-bold text-sm truncate">{circuitName}</span>
          <span className={`text-[10px] px-2 py-0.5 rounded ${typeColor}`}>
            {trackType === "street" ? "Street" : "Permanent"}
          </span>
        </div>
        <div className="text-xs text-gray-400 mb-1">{raceName}</div>
        <div className="text-xs text-gray-500 mb-2">{dateStr} &bull; {country}</div>
        <div className="flex gap-3 text-[11px] mb-2">
          <span className={overtakeColor(overtakeDifficulty)}>
            Overtaking: {10 - overtakeDifficulty}/10
          </span>
          <span className={rainColor(rainProbabilityPct)}>
            Rain: {rainProbabilityPct}%
          </span>
        </div>
        {sprintWeekend && (
          <span className="text-[10px] bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded">
            Sprint
          </span>
        )}
      </div>
    </Link>
  );
}
