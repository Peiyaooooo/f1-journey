"use client";

import { useState } from "react";
import QuizFlow from "@/components/QuizFlow";
import QuizResults from "@/components/QuizResults";
import { scoreCircuits } from "@/lib/scoring";
import type { QuizAnswers, CircuitScore } from "@/lib/scoring";

// Simple city-to-continent mapping for proximity scoring
const CITY_CONTINENT_MAP: Record<string, string> = {
  // Europe
  London: "Europe",
  Paris: "Europe",
  Berlin: "Europe",
  Madrid: "Europe",
  Rome: "Europe",
  Amsterdam: "Europe",
  Vienna: "Europe",
  Brussels: "Europe",
  Zurich: "Europe",
  Munich: "Europe",
  Milan: "Europe",
  Barcelona: "Europe",
  Manchester: "Europe",
  Stockholm: "Europe",
  Oslo: "Europe",
  Helsinki: "Europe",
  Copenhagen: "Europe",
  Dublin: "Europe",
  Lisbon: "Europe",
  Warsaw: "Europe",
  Prague: "Europe",
  Budapest: "Europe",
  // North America
  "New York": "North America",
  "Los Angeles": "North America",
  Chicago: "North America",
  Houston: "North America",
  Miami: "North America",
  Toronto: "North America",
  Vancouver: "North America",
  Montreal: "North America",
  "Mexico City": "North America",
  Dallas: "North America",
  "San Francisco": "North America",
  Boston: "North America",
  Washington: "North America",
  Atlanta: "North America",
  // South America
  "Sao Paulo": "South America",
  "Buenos Aires": "South America",
  "Rio de Janeiro": "South America",
  Bogota: "South America",
  Lima: "South America",
  Santiago: "South America",
  // Asia
  Tokyo: "Asia",
  Shanghai: "Asia",
  Beijing: "Asia",
  Singapore: "Asia",
  "Hong Kong": "Asia",
  Seoul: "Asia",
  Mumbai: "Asia",
  Delhi: "Asia",
  Bangkok: "Asia",
  "Kuala Lumpur": "Asia",
  Jakarta: "Asia",
  Taipei: "Asia",
  // Middle East
  Dubai: "Middle East",
  "Abu Dhabi": "Middle East",
  Doha: "Middle East",
  Riyadh: "Middle East",
  Jeddah: "Middle East",
  Bahrain: "Middle East",
  // Oceania
  Sydney: "Oceania",
  Melbourne: "Oceania",
  Brisbane: "Oceania",
  Perth: "Oceania",
  Auckland: "Oceania",
  // Africa
  Johannesburg: "Africa",
  "Cape Town": "Africa",
  Cairo: "Africa",
  Nairobi: "Africa",
  Lagos: "Africa",
};

function guessContinent(city: string): string | null {
  // Try exact match first
  if (CITY_CONTINENT_MAP[city]) return CITY_CONTINENT_MAP[city];

  // Try case-insensitive partial match
  const lower = city.toLowerCase();
  for (const [key, continent] of Object.entries(CITY_CONTINENT_MAP)) {
    if (key.toLowerCase() === lower) return continent;
    if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) {
      return continent;
    }
  }

  return null;
}

interface QuizPageClientProps {
  circuits: Array<{
    id: number;
    name: string;
    country: string;
    continent: string;
    overtake_difficulty: number;
    rain_probability_pct: number;
    atmosphere_rating: number | null;
    raceDate: string | null;
    cheapestPrice: number | null;
  }>;
  cities: string[];
}

export default function QuizPageClient({
  circuits,
  cities,
}: QuizPageClientProps) {
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState<CircuitScore[] | null>(null);

  const handleComplete = (answers: QuizAnswers) => {
    const originContinent = guessContinent(answers.originCity);
    const scored = scoreCircuits(circuits, answers, originContinent);
    setResults(scored);
    setShowResults(true);
  };

  const handleRetake = () => {
    setShowResults(false);
    setResults(null);
  };

  if (showResults && results) {
    return <QuizResults results={results} onRetake={handleRetake} />;
  }

  return <QuizFlow cities={cities} onComplete={handleComplete} />;
}
