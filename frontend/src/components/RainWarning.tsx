interface RainWarningProps {
  rainProbabilityPct: number;
}

export default function RainWarning({ rainProbabilityPct }: RainWarningProps) {
  if (rainProbabilityPct <= 40) return null;

  return (
    <div className="mx-6 mt-4 px-4 py-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-300 text-sm flex items-start gap-2">
      <span className="font-semibold shrink-0">Rain Risk</span>
      <span>
        This circuit has <strong>{rainProbabilityPct}%</strong> chance of rain during race weekend
        &mdash; consider a covered grandstand.
      </span>
    </div>
  );
}
