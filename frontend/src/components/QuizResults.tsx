"use client";

import Link from "next/link";
import type { CircuitScore } from "@/lib/scoring";

interface QuizResultsProps {
  results: CircuitScore[];
  onRetake: () => void;
}

export default function QuizResults({ results, onRetake }: QuizResultsProps) {
  const top10 = results.slice(0, 10);
  const maxScore = top10.length > 0 ? top10[0].score : 100;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Your Top Circuits</h2>
          <p className="text-sm text-gray-400 mt-1">
            Based on your preferences, ranked by match score
          </p>
        </div>
        <button
          onClick={onRetake}
          className="px-4 py-2 rounded-lg border border-gray-600 text-sm text-gray-300 hover:border-gray-500 transition-colors"
        >
          Retake quiz
        </button>
      </div>

      <div className="space-y-3">
        {top10.map((result, idx) => {
          const barWidth = maxScore > 0 ? (result.score / maxScore) * 100 : 0;
          const dateStr = result.raceDate
            ? new Date(result.raceDate).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })
            : null;

          return (
            <div
              key={result.circuitId}
              className="bg-gray-800 rounded-xl border border-gray-700 p-4"
            >
              <div className="flex items-start gap-4">
                {/* Rank */}
                <div className="text-lg font-bold text-gray-500 w-8 text-right shrink-0">
                  #{idx + 1}
                </div>

                <div className="flex-1 min-w-0">
                  {/* Name + country + date */}
                  <div className="flex items-baseline gap-2 flex-wrap mb-1">
                    <span className="font-bold text-gray-100">
                      {result.circuitName}
                    </span>
                    <span className="text-sm text-gray-400">
                      {result.country}
                    </span>
                    {dateStr && (
                      <span className="text-xs text-gray-500">{dateStr}</span>
                    )}
                  </div>

                  {/* Score bar */}
                  <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                    <div
                      className="h-2 rounded-full transition-all duration-500"
                      style={{
                        width: `${barWidth}%`,
                        background: `linear-gradient(90deg, #22c55e, #4ade80)`,
                      }}
                    />
                  </div>

                  {/* Stats row */}
                  <div className="flex items-center gap-4 text-xs text-gray-400 mb-2">
                    <span>Score: {result.score}/100</span>
                    <span>Overtaking: {result.overtakingScore}/10</span>
                    <span>Rain: {result.rainPct}%</span>
                    {result.cheapestPrice !== null && (
                      <span>From ${result.cheapestPrice.toLocaleString()}</span>
                    )}
                  </div>

                  {/* Reason badges */}
                  {result.reasons.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {result.reasons.map((reason) => (
                        <span
                          key={reason}
                          className="text-[11px] px-2 py-0.5 rounded-full bg-green-500/10 text-green-400"
                        >
                          {reason}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* View details */}
                  <Link
                    href={`/tracks/${result.circuitId}`}
                    className="text-xs text-green-400 hover:text-green-300 transition-colors"
                  >
                    View details &rarr;
                  </Link>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {top10.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No results to display. Try retaking the quiz.
        </div>
      )}
    </div>
  );
}
