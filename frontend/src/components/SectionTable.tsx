"use client";

import { useState } from "react";
import type { SeatSection } from "@/lib/api";

interface SectionTableProps {
  sections: SeatSection[];
  onSectionClick: (section: SeatSection) => void;
}

type SortKey = "name" | "section_type" | "location_on_track" | "has_roof" | "has_screen";

export default function SectionTable({ sections, onSectionClick }: SectionTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [sortAsc, setSortAsc] = useState(true);

  const sorted = [...sections].sort((a, b) => {
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    if (aVal === null || aVal === undefined) return 1;
    if (bVal === null || bVal === undefined) return -1;
    if (typeof aVal === "boolean") return (aVal === bVal ? 0 : aVal ? -1 : 1) * (sortAsc ? 1 : -1);
    if (typeof aVal === "string") return aVal.localeCompare(String(bVal)) * (sortAsc ? 1 : -1);
    return 0;
  });

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  }

  const thClass = "pb-2 pr-4 cursor-pointer hover:text-gray-200";

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-400 text-left">
            <th className={thClass} onClick={() => handleSort("name")}>Name {sortKey === "name" ? (sortAsc ? "\u2191" : "\u2193") : ""}</th>
            <th className={thClass} onClick={() => handleSort("section_type")}>Type {sortKey === "section_type" ? (sortAsc ? "\u2191" : "\u2193") : ""}</th>
            <th className={thClass} onClick={() => handleSort("location_on_track")}>Location {sortKey === "location_on_track" ? (sortAsc ? "\u2191" : "\u2193") : ""}</th>
            <th className={thClass} onClick={() => handleSort("has_roof")}>Roof {sortKey === "has_roof" ? (sortAsc ? "\u2191" : "\u2193") : ""}</th>
            <th className={thClass} onClick={() => handleSort("has_screen")}>Screen {sortKey === "has_screen" ? (sortAsc ? "\u2191" : "\u2193") : ""}</th>
            <th className="pb-2 pr-4">Pit View</th>
            <th className="pb-2 pr-4">Podium View</th>
            <th className="pb-2">Capacity</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((section) => (
            <tr
              key={section.id}
              className="border-b border-gray-800/50 hover:bg-gray-900 cursor-pointer"
              onClick={() => onSectionClick(section)}
            >
              <td className="py-2 pr-4 text-blue-400">{section.name}</td>
              <td className="py-2 pr-4 text-gray-400 capitalize">{section.section_type.replace("_", " ")}</td>
              <td className="py-2 pr-4 text-gray-400">{section.location_on_track || "\u2014"}</td>
              <td className="py-2 pr-4">{section.has_roof ? "\u2713" : "\u2014"}</td>
              <td className="py-2 pr-4">{section.has_screen ? "\u2713" : "\u2014"}</td>
              <td className="py-2 pr-4">{section.pit_view ? "\u2713" : "\u2014"}</td>
              <td className="py-2 pr-4">{section.podium_view ? "\u2713" : "\u2014"}</td>
              <td className="py-2">{section.capacity ? section.capacity.toLocaleString() : "\u2014"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
