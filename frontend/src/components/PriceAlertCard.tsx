"use client";

interface PriceAlertCardProps {
  id: number;
  circuit_id: number;
  circuit_name?: string;
  seat_section_id: number | null;
  section_name?: string;
  target_price: number;
  is_active: boolean;
  triggered_at: string | null;
  onDelete: (id: number) => void;
}

export default function PriceAlertCard({
  id,
  circuit_name,
  section_name,
  target_price,
  is_active,
  triggered_at,
  onDelete,
}: PriceAlertCardProps) {
  const statusBadge = is_active
    ? "bg-green-500/10 text-green-400"
    : "bg-amber-500/10 text-amber-400";
  const statusLabel = is_active ? "Active" : "Triggered";

  return (
    <div className="bg-gray-800 rounded-lg p-4 flex items-center justify-between">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-sm truncate">
            {circuit_name || `Circuit #${id}`}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded ${statusBadge}`}>
            {statusLabel}
          </span>
        </div>
        <div className="text-xs text-gray-400">
          {section_name || "Any section"} &bull; Target: ${target_price.toFixed(0)}
        </div>
        {triggered_at && (
          <div className="text-xs text-gray-500 mt-0.5">
            Triggered {new Date(triggered_at).toLocaleDateString()}
          </div>
        )}
      </div>
      <button
        onClick={() => onDelete(id)}
        className="text-xs text-red-400 hover:text-red-300 px-2 py-1.5 ml-3"
      >
        Delete
      </button>
    </div>
  );
}
