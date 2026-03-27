// frontend/src/components/CircuitCard.tsx
import Link from "next/link";

export interface CircuitCardProps {
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

function overtakingColor(score: number): string {
  if (score >= 7) return "text-green-400";
  if (score >= 4) return "text-yellow-400";
  return "text-red-400";
}

function rainColor(pct: number): string {
  if (pct >= 40) return "text-red-400";
  if (pct >= 20) return "text-blue-400";
  return "text-green-400";
}

export default function CircuitCard({
  id,
  name,
  country,
  trackType,
  overtakeDifficulty,
  rainProbabilityPct,
  raceDate,
  sprintWeekend,
  cheapestTicketPrice,
}: CircuitCardProps) {
  const overtakingScore = 10 - overtakeDifficulty;

  const typeColor =
    trackType === "street"
      ? "bg-yellow-500/10 text-yellow-500"
      : "bg-green-500/10 text-green-500";

  const dateStr = raceDate
    ? new Date(raceDate).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : null;

  return (
    <Link href={`/tracks/${id}`} className="block">
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-gray-500 transition-colors cursor-pointer h-full flex flex-col">
        {/* Header: name + track type badge */}
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="font-bold text-sm text-gray-100 leading-tight">
            {name}
          </h3>
          <span
            className={`text-[10px] px-2 py-0.5 rounded whitespace-nowrap ${typeColor}`}
          >
            {trackType === "street" ? "Street" : "Permanent"}
          </span>
        </div>

        {/* Country */}
        <p className="text-xs text-gray-400 mb-3">{country}</p>

        {/* Stats */}
        <div className="flex gap-3 text-[11px] mb-3">
          <span className={overtakingColor(overtakingScore)}>
            Overtaking: {overtakingScore}/10
          </span>
          <span className={rainColor(rainProbabilityPct)}>
            Rain: {rainProbabilityPct}%
          </span>
        </div>

        {/* Spacer to push bottom content down */}
        <div className="mt-auto">
          {/* Date + Sprint */}
          <div className="flex items-center gap-2 mb-2">
            {dateStr && (
              <span className="text-xs text-gray-500">{dateStr}</span>
            )}
            {sprintWeekend && (
              <span className="text-[10px] bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded">
                Sprint
              </span>
            )}
          </div>

          {/* Ticket price */}
          <div className="text-xs text-gray-300">
            {cheapestTicketPrice !== null ? (
              <span>
                From{" "}
                <span className="font-semibold text-gray-100">
                  ${cheapestTicketPrice.toLocaleString()}
                </span>
              </span>
            ) : (
              <span className="text-gray-500">Check prices</span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
