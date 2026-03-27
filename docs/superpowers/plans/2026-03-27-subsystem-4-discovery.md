# Subsystem 4: Discovery + Recommendations — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Explore page with filters, recommendation quiz, comparison mode, and weather intelligence — all frontend.

**Architecture:** Three new pages (`/explore`, `/quiz`, `/compare`) consuming existing backend APIs. Client-side filtering, scoring, and comparison. Weather warnings integrated into existing track detail page.

**Tech Stack:** Next.js 16 (App Router), TypeScript, Tailwind CSS. No new backend work.

---

## File Structure

```
frontend/src/
├── app/
│   ├── explore/
│   │   └── page.tsx              # Create: Explore page (server component fetches data)
│   ├── quiz/
│   │   └── page.tsx              # Create: Quiz page
│   └── compare/
│       └── page.tsx              # Create: Comparison page
├── components/
│   ├── Navbar.tsx                # Modify: add Explore, Quiz, Compare links
│   ├── CircuitCard.tsx           # Create: card for explore grid
│   ├── ExploreClient.tsx         # Create: client component with filters + sort
│   ├── QuizFlow.tsx              # Create: multi-step quiz
│   ├── QuizResults.tsx           # Create: ranked results
│   ├── ComparisonView.tsx        # Create: side-by-side stats
│   ├── RainWarning.tsx           # Create: rain warning banner
│   ├── TrackDetailClient.tsx     # Modify: add rain warning
│   └── CircuitMap.tsx            # Modify: highlight covered sections
└── lib/
    └── scoring.ts                # Create: quiz scoring algorithm
```

---

## Task 1: CircuitCard Component

**Files:**
- Create: `frontend/src/components/CircuitCard.tsx`

- [ ] **Step 1: Create CircuitCard component**

A reusable card showing circuit name, country, track type badge, overtaking score, rain %, race date, and cheapest ticket price. Accepts all data as props. Links to `/tracks/{id}`.

Props: `id`, `name`, `country`, `continent`, `trackType`, `overtakeDifficulty`, `rainProbabilityPct`, `raceDate` (string | null), `sprintWeekend` (boolean), `cheapestTicketPrice` (number | null).

Display:
- Circuit name (bold), country below
- Track type badge (street=yellow, permanent=green)
- Overtaking: `{10 - overtakeDifficulty}/10` with color coding (<=3 green, <=6 yellow, >6 red)
- Rain: `{rainProbabilityPct}%` with color
- Race date formatted
- Sprint badge if sprint weekend
- Cheapest ticket: `From $XXX` or "No tickets" if null
- Entire card is a Link to `/tracks/{id}`

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/CircuitCard.tsx
git commit -m "feat: add CircuitCard component for explore grid"
```

---

## Task 2: Explore Page with Filters

**Files:**
- Create: `frontend/src/components/ExploreClient.tsx`
- Create: `frontend/src/app/explore/page.tsx`

- [ ] **Step 1: Create ExploreClient (client component)**

This is the main interactive component. It receives all circuit data, race events, and ticket data as props (fetched server-side).

State:
- `continentFilter`: string (default "")
- `trackTypeFilter`: string (default "")
- `minOvertaking`: number (default 0)
- `maxRain`: number (default 100)
- `sortBy`: "name" | "overtaking" | "rain" | "date" (default "date")

Filtering logic (all client-side):
- Filter circuits by continent if selected
- Filter by track type if selected
- Filter by overtaking score >= minOvertaking (using `10 - overtake_difficulty`)
- Filter by rain_probability_pct <= maxRain
- Sort by selected field

Layout:
- Filter controls at top (dropdowns for continent/track type, sliders or selects for overtaking/rain, sort dropdown)
- Grid of CircuitCard components below (responsive: 1 col mobile, 2 col tablet, 3 col desktop)
- Show count: "Showing X of 22 circuits"

- [ ] **Step 2: Create Explore page (server component)**

Server component that fetches circuits, race events (2026, upcoming), and tickets for each circuit. Builds a merged data structure and passes to ExploreClient.

```tsx
// Fetch circuits, events, and cheapest ticket per circuit
const circuits = await fetchCircuits();
const events = await fetchRaceEvents({ season: 2026, status: "upcoming" });
// For cheapest ticket, we can use the circuits/tickets endpoint
// Build enriched data: circuit + race date + cheapest price
```

Pass enriched data to `<ExploreClient circuits={enrichedCircuits} />`.

- [ ] **Step 3: Verify build**

```bash
cd frontend && npx next build
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ExploreClient.tsx frontend/src/app/explore/
git commit -m "feat: add Explore page with continent, type, overtaking, and rain filters"
```

---

## Task 3: Quiz Scoring Algorithm

**Files:**
- Create: `frontend/src/lib/scoring.ts`

- [ ] **Step 1: Create scoring module**

```typescript
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

  return circuits.map(c => {
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
  }).sort((a, b) => b.score - a.score);
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/lib/scoring.ts
git commit -m "feat: add quiz scoring algorithm for circuit recommendations"
```

---

## Task 4: Quiz Flow + Results

**Files:**
- Create: `frontend/src/components/QuizFlow.tsx`
- Create: `frontend/src/components/QuizResults.tsx`
- Create: `frontend/src/app/quiz/page.tsx`

- [ ] **Step 1: Create QuizFlow component**

Client component with 5 steps. Each step has a "Next" button. Final step has "See Results".

State: `step` (1-5), `answers: QuizAnswers`.

Step 1: City input with autocomplete (fetch from `/api/travel/cities`).
Step 2: Budget slider/buttons ($200, $500, $1000, $2000, $5000+).
Step 3: Priority multi-select checkboxes (overtaking, atmosphere, low rain, proximity, cheapest).
Step 4: Rain tolerance radio buttons (prefer sun, don't mind, love rain drama).
Step 5: Group size selector (1-10).

On submit, calls `onComplete(answers)`.

- [ ] **Step 2: Create QuizResults component**

Receives `results: CircuitScore[]`. Shows top 10 ranked:
- Rank number + score bar (visual width proportional to score)
- Circuit name, country, race date
- Reason badges (green pills)
- Overtaking score + rain % stats
- Cheapest price if available
- "View details" link to `/tracks/{id}`

- [ ] **Step 3: Create Quiz page**

Server component that fetches circuits, events, and cheapest tickets. Passes to a client wrapper that manages the quiz state (showing QuizFlow or QuizResults).

Also fetches city suggestions for the autocomplete.

The client wrapper:
- Shows QuizFlow initially
- On completion, runs `scoreCircuits()` with the answers
- Switches to QuizResults view
- Has a "Retake quiz" button to go back

- [ ] **Step 4: Verify build**

```bash
cd frontend && npx next build
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/QuizFlow.tsx frontend/src/components/QuizResults.tsx frontend/src/app/quiz/
git commit -m "feat: add recommendation quiz with scoring and results"
```

---

## Task 5: Comparison View

**Files:**
- Create: `frontend/src/components/ComparisonView.tsx`
- Create: `frontend/src/app/compare/page.tsx`

- [ ] **Step 1: Create ComparisonView component**

Client component. Two dropdowns at the top to select circuit A and circuit B from a list.

Once both selected, show side-by-side comparison:
- Track stats row: overtaking score (with green highlight on better), rain %, track length, turns, DRS zones, track type
- Ticket row: cheapest GA price, cheapest grandstand price
- Race info row: date, sprint weekend (yes/no)
- For each stat, green background on the "better" side

Props: `circuits` (full list), `circuitTickets` (map of circuitId → cheapest prices), `raceEvents` (for dates).

- [ ] **Step 2: Create Compare page**

Server component that fetches all circuits, race events, and ticket data. Passes to ComparisonView.

- [ ] **Step 3: Verify build**

```bash
cd frontend && npx next build
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ComparisonView.tsx frontend/src/app/compare/
git commit -m "feat: add side-by-side circuit comparison page"
```

---

## Task 6: Weather Intelligence

**Files:**
- Create: `frontend/src/components/RainWarning.tsx`
- Modify: `frontend/src/app/tracks/[id]/TrackDetailClient.tsx`
- Modify: `frontend/src/components/CircuitMap.tsx`

- [ ] **Step 1: Create RainWarning component**

Simple banner component:
```tsx
interface RainWarningProps {
  rainProbabilityPct: number;
}
```

If `rainProbabilityPct > 40`: show a yellow/amber warning banner:
"This circuit has {X}% chance of rain during race weekend — consider a covered grandstand"

With a rain icon (unicode or emoji-free text: "Rain Risk").

If <= 40: render nothing.

- [ ] **Step 2: Update TrackDetailClient**

Add `rainProbabilityPct` to props. Show `<RainWarning>` above the tabs.

Pass `rainProbabilityPct` to `CircuitMap` as well.

- [ ] **Step 3: Update CircuitMap**

Add `rainRisk` prop (number). When `rainRisk > 40`, add a small visual indicator on section chips that have `has_roof=true` — append a "Covered" text or add a distinct border color to make covered sections stand out.

- [ ] **Step 4: Update page.tsx to pass rainProbabilityPct**

Pass `circuit.rain_probability_pct` to TrackDetailClient.

- [ ] **Step 5: Verify build**

```bash
cd frontend && npx next build
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/RainWarning.tsx frontend/src/components/CircuitMap.tsx frontend/src/app/tracks/
git commit -m "feat: add rain warning banner and covered section highlighting"
```

---

## Task 7: Navbar Updates

**Files:**
- Modify: `frontend/src/components/Navbar.tsx`

- [ ] **Step 1: Update Navbar with new links**

Change the current "Explore" link to point to `/explore`. Add links for Quiz and Compare:

```tsx
<Link href="/explore" className="text-sm text-gray-400 hover:text-white">Explore</Link>
<Link href="/quiz" className="text-sm text-gray-400 hover:text-white">Quiz</Link>
<Link href="/compare" className="text-sm text-gray-400 hover:text-white">Compare</Link>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/Navbar.tsx
git commit -m "feat: add Explore, Quiz, Compare links to navbar"
```

---

## Task 8: End-to-End Verification

- [ ] **Step 1: Verify build**

```bash
cd frontend && npx next build
```
All routes should compile: `/`, `/explore`, `/quiz`, `/compare`, `/tracks/[id]`, `/tracks/[id]/tickets`.

- [ ] **Step 2: Start servers and verify**

Backend: `cd backend && .venv/bin/uvicorn app.main:app --port 8000`
Frontend: `cd frontend && npm run dev -- -p 3001`

Verify:
- `/explore` — grid of 22 circuit cards, filters work (continent, track type, overtaking, rain)
- `/quiz` — 5-step flow works, results show ranked circuits with scores
- `/compare` — select two circuits, side-by-side stats display
- `/tracks/9` (Silverstone, 55% rain) — shows rain warning banner, covered sections highlighted
- `/tracks/6` (Monaco, 15% rain) — no rain warning
- Navbar links all work

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete subsystem 4 — discovery, quiz, comparison, weather intelligence"
```
