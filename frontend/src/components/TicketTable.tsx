"use client";

import { useState } from "react";
import type { TicketListing } from "@/lib/api";

interface TicketTableProps {
  tickets: TicketListing[];
}

const SOURCE_LABELS: Record<string, string> = {
  f1_official: "F1.com",
  stubhub: "StubHub",
  viagogo: "Viagogo",
  seatgeek: "SeatGeek",
  vivid_seats: "Vivid Seats",
  ticketmaster: "Ticketmaster",
  gp_portal: "GP Portal",
};

export default function TicketTable({ tickets }: TicketTableProps) {
  const [sourceFilter, setSourceFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState<"price_asc" | "price_desc">("price_asc");

  const sources = [...new Set(tickets.map((t) => t.source_site))];
  const types = [...new Set(tickets.map((t) => t.ticket_type))];

  let filtered = tickets;
  if (sourceFilter) filtered = filtered.filter((t) => t.source_site === sourceFilter);
  if (typeFilter) filtered = filtered.filter((t) => t.ticket_type === typeFilter);
  filtered = [...filtered].sort((a, b) =>
    sortBy === "price_asc" ? a.price - b.price : b.price - a.price
  );

  return (
    <div>
      <div className="flex gap-3 mb-4 flex-wrap">
        <select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-1.5">
          <option value="">All Sources</option>
          {sources.map((s) => <option key={s} value={s}>{SOURCE_LABELS[s] || s}</option>)}
        </select>
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-1.5">
          <option value="">All Types</option>
          {types.map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
        </select>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value as "price_asc" | "price_desc")}
          className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-1.5">
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-gray-400 text-left">
              <th className="pb-2 pr-4">Source</th>
              <th className="pb-2 pr-4">Section</th>
              <th className="pb-2 pr-4">Type</th>
              <th className="pb-2 pr-4">Price</th>
              <th className="pb-2 pr-4">Available</th>
              <th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((t) => (
              <tr key={t.id} className="border-b border-gray-800/50 hover:bg-gray-900">
                <td className="py-2 pr-4">{SOURCE_LABELS[t.source_site] || t.source_site}</td>
                <td className="py-2 pr-4 text-gray-400">{t.source_section_name}</td>
                <td className="py-2 pr-4 text-gray-400 capitalize">{t.ticket_type.replace(/_/g, " ")}</td>
                <td className="py-2 pr-4 font-bold text-green-400">{t.currency} {t.price.toFixed(0)}</td>
                <td className="py-2 pr-4 text-gray-400">{t.available_quantity ?? "—"}</td>
                <td className="py-2">
                  <a href={t.source_url} target="_blank" rel="noopener noreferrer"
                    className="text-xs bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded">
                    Buy
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center text-gray-500 py-8">No tickets found</div>
        )}
      </div>
    </div>
  );
}
