const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface CircuitListItem {
  id: number;
  name: string;
  country: string;
  continent: string;
  track_type: string;
  overtake_difficulty: number;
  avg_overtakes_per_race: number;
  rain_probability_pct: number;
}

export interface Circuit extends CircuitListItem {
  city: string;
  latitude: number;
  longitude: number;
  track_length_km: number;
  number_of_turns: number;
  drs_zones_count: number;
  nearest_airport: string;
  local_transport_notes: string | null;
  atmosphere_rating: number | null;
  fan_reviews_summary: string | null;
  elevation_change: number | null;
}

export interface RaceEvent {
  id: number;
  circuit_id: number;
  season_year: number;
  race_name: string;
  race_date: string;
  sprint_weekend: boolean;
  status: string;
  total_overtakes: number | null;
  weather_actual: string | null;
}

export interface RaceEventWithCircuit extends RaceEvent {
  circuit_name: string;
  circuit_country: string;
  continent: string;
}

export async function fetchCircuits(params?: {
  continent?: string;
  track_type?: string;
}): Promise<CircuitListItem[]> {
  const url = new URL(`${API_URL}/api/circuits`);
  if (params?.continent) url.searchParams.set("continent", params.continent);
  if (params?.track_type) url.searchParams.set("track_type", params.track_type);
  const res = await fetch(url.toString(), { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch circuits");
  return res.json();
}

export async function fetchCircuit(id: number): Promise<Circuit> {
  const res = await fetch(`${API_URL}/api/circuits/${id}`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch circuit");
  return res.json();
}

export async function fetchRaceEvents(params?: {
  season?: number;
  status?: string;
}): Promise<RaceEvent[]> {
  const url = new URL(`${API_URL}/api/race-events`);
  if (params?.season) url.searchParams.set("season", String(params.season));
  if (params?.status) url.searchParams.set("status", params.status);
  const res = await fetch(url.toString(), { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch race events");
  return res.json();
}

export async function fetchRaceEvent(id: number): Promise<RaceEventWithCircuit> {
  const res = await fetch(`${API_URL}/api/race-events/${id}`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch race event");
  return res.json();
}

export interface SeatSection {
  id: number;
  circuit_id: number;
  name: string;
  section_type: string;
  location_on_track: string | null;
  has_roof: boolean;
  has_screen: boolean;
  pit_view: boolean;
  podium_view: boolean;
  capacity: number | null;
  view_description: string | null;
  latitude: number;
  longitude: number;
  view_photos: string[] | null;
}

export async function fetchSections(
  circuitId: number,
  params?: { section_type?: string; has_roof?: boolean }
): Promise<SeatSection[]> {
  const url = new URL(`${API_URL}/api/circuits/${circuitId}/sections`);
  if (params?.section_type) url.searchParams.set("section_type", params.section_type);
  if (params?.has_roof !== undefined) url.searchParams.set("has_roof", String(params.has_roof));
  const res = await fetch(url.toString(), { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch sections");
  return res.json();
}

export async function fetchSection(id: number): Promise<SeatSection> {
  const res = await fetch(`${API_URL}/api/sections/${id}`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch section");
  return res.json();
}

export interface TicketListing {
  id: number;
  circuit_id: number;
  race_event_id: number;
  seat_section_id: number | null;
  source_site: string;
  source_url: string;
  source_section_name: string;
  ticket_type: string;
  price: number;
  currency: string;
  available_quantity: number | null;
  includes: string[] | null;
  last_scraped_at: string;
  is_available: boolean;
}

export async function fetchCircuitTickets(
  circuitId: number,
  params?: { source_site?: string; ticket_type?: string; min_price?: number; max_price?: number; sort?: string }
): Promise<TicketListing[]> {
  const url = new URL(`${API_URL}/api/circuits/${circuitId}/tickets`);
  if (params?.source_site) url.searchParams.set("source_site", params.source_site);
  if (params?.ticket_type) url.searchParams.set("ticket_type", params.ticket_type);
  if (params?.min_price !== undefined) url.searchParams.set("min_price", String(params.min_price));
  if (params?.max_price !== undefined) url.searchParams.set("max_price", String(params.max_price));
  if (params?.sort) url.searchParams.set("sort", params.sort);
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("Failed to fetch tickets");
  return res.json();
}

export async function fetchSectionTickets(sectionId: number): Promise<TicketListing[]> {
  const res = await fetch(`${API_URL}/api/sections/${sectionId}/tickets`, { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("Failed to fetch section tickets");
  return res.json();
}

export async function fetchUnmatchedTickets(circuitId: number): Promise<TicketListing[]> {
  const res = await fetch(`${API_URL}/api/circuits/${circuitId}/tickets/unmatched`, { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("Failed to fetch unmatched tickets");
  return res.json();
}
