"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import type { SeatSection } from "@/lib/api";
import SectionSidebar from "@/components/SectionSidebar";
import SectionTable from "@/components/SectionTable";

const TrackMap = dynamic(() => import("@/components/TrackMap"), { ssr: false });

interface TrackDetailClientProps {
  centerLat: number;
  centerLng: number;
  sections: SeatSection[];
}

export default function TrackDetailClient({ centerLat, centerLng, sections }: TrackDetailClientProps) {
  const [activeTab, setActiveTab] = useState<"map" | "table">("map");
  const [selectedSection, setSelectedSection] = useState<SeatSection | null>(null);

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
      <div className="flex border-b border-gray-800 px-6">
        <button className={tabClass("map")} onClick={() => setActiveTab("map")}>
          Seat Map
        </button>
        <button className={tabClass("table")} onClick={() => setActiveTab("table")}>
          Table View
        </button>
      </div>

      <div className="px-6 pt-3 flex gap-4 text-xs text-gray-400">
        <span><span className="inline-block w-3 h-3 rounded-full bg-blue-500 mr-1"></span> Grandstand</span>
        <span><span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-1"></span> General Admission</span>
        <span><span className="inline-block w-3 h-3 rounded-full bg-yellow-500 mr-1"></span> Hospitality / VIP</span>
      </div>

      <div className="px-6 py-4">
        {activeTab === "map" ? (
          <div className="flex gap-0">
            <div className={selectedSection ? "flex-1" : "w-full"}>
              <TrackMap
                centerLat={centerLat}
                centerLng={centerLng}
                sections={sections}
                onSectionClick={handleSectionClick}
                selectedSectionId={selectedSection?.id ?? null}
              />
            </div>
            <SectionSidebar
              section={selectedSection}
              onClose={() => setSelectedSection(null)}
            />
          </div>
        ) : (
          <div className="flex gap-0">
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
