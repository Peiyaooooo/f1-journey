"use client";

import type { SeatSection } from "@/lib/api";

interface CircuitMapProps {
  mapImageUrl: string | null;
  circuitName: string;
  sections: SeatSection[];
  selectedSectionId: number | null;
  onSectionClick: (section: SeatSection) => void;
}

const TYPE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  grandstand: { bg: "bg-blue-500/10", border: "border-blue-500", text: "text-blue-400" },
  general_admission: { bg: "bg-green-500/10", border: "border-green-500", text: "text-green-400" },
  hospitality: { bg: "bg-yellow-500/10", border: "border-yellow-500", text: "text-yellow-400" },
  vip: { bg: "bg-yellow-500/10", border: "border-yellow-500", text: "text-yellow-400" },
};

export default function CircuitMap({
  mapImageUrl,
  circuitName,
  sections,
  selectedSectionId,
  onSectionClick,
}: CircuitMapProps) {
  if (!mapImageUrl) {
    return (
      <div className="w-full h-[400px] bg-gray-800 rounded-lg flex items-center justify-center">
        <span className="text-gray-500">No circuit map available</span>
      </div>
    );
  }

  return (
    <div>
      {/* Circuit map image */}
      <div className="relative w-full rounded-lg overflow-hidden bg-gray-900 border border-gray-700">
        <img
          src={mapImageUrl}
          alt={`${circuitName} circuit map with grandstand locations`}
          className="w-full h-auto"
        />
      </div>

      {/* Section chips below map - clickable to select */}
      <div className="mt-4 flex flex-wrap gap-2">
        {sections.map((section) => {
          const colors = TYPE_COLORS[section.section_type] || TYPE_COLORS.grandstand;
          const isSelected = selectedSectionId === section.id;
          return (
            <button
              key={section.id}
              onClick={() => onSectionClick(section)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all cursor-pointer ${
                isSelected
                  ? `${colors.bg} ${colors.border} ${colors.text} ring-1 ring-white/30`
                  : `bg-gray-800 border-gray-700 text-gray-300 hover:${colors.border} hover:${colors.text}`
              }`}
            >
              {section.name}
              {section.location_on_track && (
                <span className="text-gray-500 ml-1">· {section.location_on_track}</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
