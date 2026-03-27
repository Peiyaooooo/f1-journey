"use client";

import { useRouter } from "next/navigation";

interface SavedSearchCardProps {
  id: number;
  name: string;
  search_type: string;
  data: Record<string, any>;
  created_at: string;
  onDelete: (id: number) => void;
}

export default function SavedSearchCard({ id, name, search_type, data, created_at, onDelete }: SavedSearchCardProps) {
  const router = useRouter();

  function handleLoad() {
    if (search_type === "trip" && data.circuit_id) {
      const params = new URLSearchParams();
      if (data.origin) params.set("origin", data.origin);
      router.push(`/tracks/${data.circuit_id}?tab=travel&${params.toString()}`);
    } else {
      const params = new URLSearchParams();
      if (data.continent) params.set("continent", data.continent);
      if (data.track_type) params.set("track_type", data.track_type);
      router.push(`/explore?${params.toString()}`);
    }
  }

  const typeBadge = search_type === "trip"
    ? "bg-blue-500/10 text-blue-400"
    : "bg-green-500/10 text-green-400";

  return (
    <div className="bg-gray-800 rounded-lg p-4 flex items-center justify-between">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-sm truncate">{name}</span>
          <span className={`text-xs px-2 py-0.5 rounded ${typeBadge}`}>
            {search_type}
          </span>
        </div>
        <div className="text-xs text-gray-500">
          {new Date(created_at).toLocaleDateString()}
        </div>
      </div>
      <div className="flex items-center gap-2 ml-3">
        <button
          onClick={handleLoad}
          className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1.5 rounded"
        >
          Load
        </button>
        <button
          onClick={() => onDelete(id)}
          className="text-xs text-red-400 hover:text-red-300 px-2 py-1.5"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
