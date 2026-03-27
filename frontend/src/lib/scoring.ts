// frontend/src/lib/scoring.ts

export interface QuizAnswers {
  originCity: string;
  budget: number; // max budget per person in USD
  priorities: string[]; // "overtaking" | "atmosphere" | "low_rain" | "proximity" | "cheapest"
  rainTolerance: "prefer_sun" | "dont_mind" | "love_rain";
  groupSize: number;
}

export interface CircuitScore {
  circuitId: number;
  circuitName: string;
  country: string;
  raceDate: string | null;
  score: number; // 0-100
  reasons: string[];
  cheapestPrice: number | null;
  overtakingScore: number;
  rainPct: number;
}

export function scoreCircuits(
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
  }>,
  answers: QuizAnswers,
  originContinent: string | null,
): CircuitScore[] {
  // Score each circuit 0-100 based on quiz answers
  // Weights: each priority adds score in its category

  return circuits
    .map((c) => {
      let score = 50; // base
      const reasons: string[] = [];
      const overtakingScore = 10 - c.overtake_difficulty;

      // Overtaking
      if (answers.priorities.includes("overtaking")) {
        const bonus = overtakingScore * 5; // 0-50
        score += bonus - 25; // center around 0
        if (overtakingScore >= 7) reasons.push("Excellent overtaking");
        else if (overtakingScore <= 3) reasons.push("Limited overtaking");
      }

      // Rain tolerance
      if (answers.rainTolerance === "prefer_sun") {
        score += (100 - c.rain_probability_pct) / 4; // 0-25 bonus for dry tracks
        if (c.rain_probability_pct <= 15) reasons.push("Very low rain risk");
        if (c.rain_probability_pct >= 50) score -= 15;
      } else if (answers.rainTolerance === "love_rain") {
        score += c.rain_probability_pct / 4;
        if (c.rain_probability_pct >= 50) reasons.push("High rain probability");
      }

      if (answers.priorities.includes("low_rain")) {
        score += (100 - c.rain_probability_pct) / 5;
      }

      // Budget
      if (answers.priorities.includes("cheapest") && c.cheapestPrice !== null) {
        if (c.cheapestPrice <= answers.budget * 0.3) {
          score += 15;
          reasons.push("Great value");
        } else if (c.cheapestPrice > answers.budget) {
          score -= 20;
          reasons.push("Over budget");
        }
      }

      // Proximity (rough continent heuristic)
      if (answers.priorities.includes("proximity") && originContinent) {
        if (c.continent === originContinent) {
          score += 15;
          reasons.push("Same continent");
        } else {
          score -= 10;
        }
      }

      // Atmosphere
      if (answers.priorities.includes("atmosphere") && c.atmosphere_rating) {
        score += (c.atmosphere_rating / 5) * 20;
        if (c.atmosphere_rating >= 4) reasons.push("Great atmosphere");
      }

      // Clamp score
      score = Math.max(0, Math.min(100, Math.round(score)));

      return {
        circuitId: c.id,
        circuitName: c.name,
        country: c.country,
        raceDate: c.raceDate,
        score,
        reasons,
        cheapestPrice: c.cheapestPrice,
        overtakingScore,
        rainPct: c.rain_probability_pct,
      };
    })
    .sort((a, b) => b.score - a.score);
}
