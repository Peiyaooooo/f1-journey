"use client";

import type { SeatSection, TicketListing } from "@/lib/api";

interface SectionSidebarProps {
  section: SeatSection | null;
  onClose: () => void;
  tickets: TicketListing[];
}

const TYPE_LABELS: Record<string, string> = {
  grandstand: "Grandstand",
  general_admission: "General Admission",
  hospitality: "Hospitality",
  vip: "VIP",
};

export default function SectionSidebar({ section, onClose, tickets }: SectionSidebarProps) {
  if (!section) return null;

  const badges = [
    section.has_roof && { label: "Has Roof", color: "bg-green-500/10 text-green-400" },
    section.has_screen && { label: "Screen", color: "bg-blue-500/10 text-blue-400" },
    section.pit_view && { label: "Pit View", color: "bg-yellow-500/10 text-yellow-400" },
    section.podium_view && { label: "Podium View", color: "bg-purple-500/10 text-purple-400" },
  ].filter(Boolean) as { label: string; color: string }[];

  return (
    <div className="bg-gray-900 border-l border-gray-700 p-4 w-80 overflow-y-auto">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-bold text-lg">{section.name}</h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-white text-xl leading-none"
        >
          &times;
        </button>
      </div>

      <div className="text-sm text-gray-400 mb-3">
        {TYPE_LABELS[section.section_type] || section.section_type}
        {section.location_on_track && <> &bull; {section.location_on_track}</>}
      </div>

      {badges.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {badges.map((badge) => (
            <span
              key={badge.label}
              className={`text-xs px-2 py-1 rounded ${badge.color}`}
            >
              {badge.label}
            </span>
          ))}
        </div>
      )}

      {section.view_description && (
        <div className="bg-gray-800 rounded-lg p-3 mb-4 text-sm text-gray-300">
          <div className="text-xs text-gray-500 mb-1 uppercase">View Description</div>
          {section.view_description}
        </div>
      )}

      {section.capacity && (
        <div className="text-sm text-gray-400 mb-4">
          Capacity: {section.capacity.toLocaleString()}
        </div>
      )}

      {section.view_photos && section.view_photos.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-gray-500 mb-2 uppercase">View Photos</div>
          <div className="flex flex-col gap-2">
            {section.view_photos.map((url, i) => (
              <img
                key={i}
                src={url}
                alt={`${section.name} view ${i + 1}`}
                className="rounded-lg w-full object-cover h-40"
              />
            ))}
          </div>
        </div>
      )}

      {tickets.length > 0 ? (
        <div>
          <div className="text-xs text-gray-500 mb-2 uppercase">Tickets Available</div>
          <div className="flex flex-col gap-2">
            {tickets.map((t) => (
              <a
                key={t.id}
                href={t.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gray-800 rounded-lg p-3 flex justify-between items-center hover:bg-gray-700 transition-colors"
              >
                <div>
                  <div className="font-medium text-sm capitalize">{t.source_site.replace(/_/g, " ")}</div>
                  <div className="text-xs text-gray-400 capitalize">{t.ticket_type.replace(/_/g, " ")}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-green-400">{t.currency} {t.price.toFixed(0)}</div>
                  {t.available_quantity && (
                    <div className="text-xs text-gray-500">{t.available_quantity} left</div>
                  )}
                </div>
              </a>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-600 text-xs mt-4">
          No tickets found for this section
        </div>
      )}
    </div>
  );
}
