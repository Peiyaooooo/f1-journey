"use client";

import { useState } from "react";
import type { SeatSection } from "@/lib/api";
import { getCircuitMapImage } from "@/lib/circuit-maps";
import CircuitMap from "@/components/CircuitMap";
import SectionSidebar from "@/components/SectionSidebar";
import SectionTable from "@/components/SectionTable";

interface TrackDetailClientProps {
  circuitName: string;
  centerLat: number;
  centerLng: number;
  sections: SeatSection[];
}

export default function TrackDetailClient({ circuitName, centerLat, centerLng, sections }: TrackDetailClientProps) {
  const [activeTab, setActiveTab] = useState<"map" | "table">("map");
  const [selectedSection, setSelectedSection] = useState<SeatSection | null>(null);

  const mapImageUrl = getCircuitMapImage(circuitName);

  function handleSectionClick(section: SeatSection) {
    setSelectedSection(section);
  }

  const tabClass = (tab: string) =>
    `px-4 py-2 text-sm font-medium cursor-pointer ${
      activeTab === tab
        ? "border-b-2 border-blue-500 text-blue-400"
        : "text-gray-400 hover:text-white"
    }`;

  return (
    <div>
      {/* Tabs */}
      <div className="flex border-b border-gray-800 px-6">
        <button className={tabClass("map")} onClick={() => setActiveTab("map")}>
          Seat Map
        </button>
        <button className={tabClass("table")} onClick={() => setActiveTab("table")}>
          Table View
        </button>
      </div>

      {/* Content */}
      <div className="px-6 py-4">
        {activeTab === "map" ? (
          <div className="flex gap-4">
            <div className={selectedSection ? "flex-1" : "w-full"}>
              <CircuitMap
                mapImageUrl={mapImageUrl}
                circuitName={circuitName}
                sections={sections}
                selectedSectionId={selectedSection?.id ?? null}
                onSectionClick={handleSectionClick}
              />
            </div>
            <SectionSidebar
              section={selectedSection}
              onClose={() => setSelectedSection(null)}
            />
          </div>
        ) : (
          <div className="flex gap-4">
            <div className={selectedSection ? "flex-1" : "w-full"}>
              <SectionTable sections={sections} onSectionClick={handleSectionClick} />
            </div>
            <SectionSidebar
              section={selectedSection}
              onClose={() => setSelectedSection(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
