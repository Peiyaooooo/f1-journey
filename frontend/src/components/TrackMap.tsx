"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { SeatSection } from "@/lib/api";

interface TrackMapProps {
  centerLat: number;
  centerLng: number;
  sections: SeatSection[];
  onSectionClick: (section: SeatSection) => void;
  selectedSectionId: number | null;
}

const SECTION_COLORS: Record<string, string> = {
  grandstand: "#3b82f6",
  general_admission: "#22c55e",
  hospitality: "#eab308",
  vip: "#eab308",
};

function FitBounds({ sections, centerLat, centerLng }: { sections: SeatSection[]; centerLat: number; centerLng: number }) {
  const map = useMap();
  useEffect(() => {
    if (sections.length === 0) {
      map.setView([centerLat, centerLng], 15);
      return;
    }
    const lats = sections.map((s) => s.latitude);
    const lngs = sections.map((s) => s.longitude);
    const bounds: [[number, number], [number, number]] = [
      [Math.min(...lats) - 0.002, Math.min(...lngs) - 0.004],
      [Math.max(...lats) + 0.002, Math.max(...lngs) + 0.004],
    ];
    map.fitBounds(bounds);
  }, [sections, centerLat, centerLng, map]);
  return null;
}

export default function TrackMap({
  centerLat,
  centerLng,
  sections,
  onSectionClick,
  selectedSectionId,
}: TrackMapProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-[500px] bg-gray-800 rounded-lg flex items-center justify-center">
        <span className="text-gray-500">Loading map...</span>
      </div>
    );
  }

  return (
    <MapContainer
      center={[centerLat, centerLng]}
      zoom={15}
      className="w-full h-[500px] rounded-lg"
      style={{ background: "#1e293b" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitBounds sections={sections} centerLat={centerLat} centerLng={centerLng} />
      {sections.map((section) => (
        <CircleMarker
          key={section.id}
          center={[section.latitude, section.longitude]}
          radius={selectedSectionId === section.id ? 10 : 7}
          pathOptions={{
            color: selectedSectionId === section.id ? "#ffffff" : SECTION_COLORS[section.section_type] || "#3b82f6",
            fillColor: SECTION_COLORS[section.section_type] || "#3b82f6",
            fillOpacity: 0.8,
            weight: selectedSectionId === section.id ? 3 : 1,
          }}
          eventHandlers={{
            click: () => onSectionClick(section),
          }}
        >
          <Popup>
            <div style={{ fontSize: "13px" }}>
              <strong>{section.name}</strong>
              <br />
              {section.section_type.replace("_", " ")}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
