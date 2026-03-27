"use client";

import { useState, useEffect, useCallback } from "react";
import type { QuizAnswers } from "@/lib/scoring";

interface QuizFlowProps {
  cities: string[];
  onComplete: (answers: QuizAnswers) => void;
}

const BUDGET_OPTIONS = [200, 500, 1000, 2000, 5000];

const PRIORITY_OPTIONS = [
  { value: "overtaking", label: "Lots of overtaking" },
  { value: "atmosphere", label: "Great atmosphere" },
  { value: "low_rain", label: "Low rain risk" },
  { value: "proximity", label: "Close to home" },
  { value: "cheapest", label: "Cheapest overall" },
] as const;

const RAIN_OPTIONS = [
  { value: "prefer_sun" as const, label: "Prefer sunshine" },
  { value: "dont_mind" as const, label: "Don't mind rain" },
  { value: "love_rain" as const, label: "Love rain drama" },
];

export default function QuizFlow({ cities, onComplete }: QuizFlowProps) {
  const [step, setStep] = useState(1);
  const [answers, setAnswers] = useState<QuizAnswers>({
    originCity: "",
    budget: 0,
    priorities: [],
    rainTolerance: "dont_mind",
    groupSize: 2,
  });

  // City autocomplete state
  const [cityQuery, setCityQuery] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredCities, setFilteredCities] = useState<string[]>([]);

  useEffect(() => {
    if (cityQuery.length >= 2) {
      const lower = cityQuery.toLowerCase();
      setFilteredCities(
        cities.filter((c) => c.toLowerCase().includes(lower)).slice(0, 8),
      );
      setShowSuggestions(true);
    } else {
      setFilteredCities([]);
      setShowSuggestions(false);
    }
  }, [cityQuery, cities]);

  const selectCity = useCallback(
    (city: string) => {
      setCityQuery(city);
      setAnswers((prev) => ({ ...prev, originCity: city }));
      setShowSuggestions(false);
    },
    [],
  );

  const canProceed = (): boolean => {
    switch (step) {
      case 1:
        return answers.originCity.length > 0;
      case 2:
        return answers.budget > 0;
      case 3:
        return answers.priorities.length > 0;
      case 4:
        return true; // always has a default
      case 5:
        return answers.groupSize >= 1;
      default:
        return false;
    }
  };

  const togglePriority = (value: string) => {
    setAnswers((prev) => ({
      ...prev,
      priorities: prev.priorities.includes(value)
        ? prev.priorities.filter((p) => p !== value)
        : [...prev.priorities, value],
    }));
  };

  const handleNext = () => {
    if (step < 5) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = () => {
    onComplete(answers);
  };

  return (
    <div className="max-w-lg mx-auto">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-xs text-gray-400 mb-2">
          <span>
            Step {step} of 5
          </span>
          <span>{Math.round((step / 5) * 100)}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(step / 5) * 100}%` }}
          />
        </div>
      </div>

      {/* Step content */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 mb-6">
        {step === 1 && (
          <div>
            <h2 className="text-lg font-bold mb-4">Where are you based?</h2>
            <p className="text-sm text-gray-400 mb-4">
              We&apos;ll use this to estimate travel distances.
            </p>
            <div className="relative">
              <input
                type="text"
                value={cityQuery}
                onChange={(e) => {
                  setCityQuery(e.target.value);
                  if (e.target.value !== answers.originCity) {
                    setAnswers((prev) => ({ ...prev, originCity: "" }));
                  }
                }}
                placeholder="Start typing a city..."
                className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-sm text-gray-100 focus:outline-none focus:border-green-500"
              />
              {showSuggestions && filteredCities.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-gray-900 border border-gray-600 rounded-lg overflow-hidden shadow-lg">
                  {filteredCities.map((city) => (
                    <button
                      key={city}
                      onClick={() => selectCity(city)}
                      className="w-full text-left px-4 py-2 text-sm text-gray-200 hover:bg-gray-700 transition-colors"
                    >
                      {city}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {answers.originCity && (
              <p className="text-xs text-green-400 mt-2">
                Selected: {answers.originCity}
              </p>
            )}
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-lg font-bold mb-4">Budget per person?</h2>
            <p className="text-sm text-gray-400 mb-4">
              Total budget including tickets, travel, and accommodation.
            </p>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {BUDGET_OPTIONS.map((amount) => (
                <button
                  key={amount}
                  onClick={() =>
                    setAnswers((prev) => ({ ...prev, budget: amount }))
                  }
                  className={`px-4 py-3 rounded-lg border text-sm font-medium transition-colors ${
                    answers.budget === amount
                      ? "border-green-500 bg-green-500/10 text-green-400"
                      : "border-gray-600 bg-gray-900 text-gray-300 hover:border-gray-500"
                  }`}
                >
                  {amount >= 5000 ? "$5,000+" : `$${amount.toLocaleString()}`}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="text-lg font-bold mb-4">What matters most?</h2>
            <p className="text-sm text-gray-400 mb-4">
              Select all that apply.
            </p>
            <div className="space-y-3">
              {PRIORITY_OPTIONS.map(({ value, label }) => (
                <label
                  key={value}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors ${
                    answers.priorities.includes(value)
                      ? "border-green-500 bg-green-500/10"
                      : "border-gray-600 bg-gray-900 hover:border-gray-500"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={answers.priorities.includes(value)}
                    onChange={() => togglePriority(value)}
                    className="accent-green-500"
                  />
                  <span className="text-sm text-gray-200">{label}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div>
            <h2 className="text-lg font-bold mb-4">Rain tolerance?</h2>
            <p className="text-sm text-gray-400 mb-4">
              Some of the best races happen in the rain.
            </p>
            <div className="space-y-3">
              {RAIN_OPTIONS.map(({ value, label }) => (
                <label
                  key={value}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors ${
                    answers.rainTolerance === value
                      ? "border-green-500 bg-green-500/10"
                      : "border-gray-600 bg-gray-900 hover:border-gray-500"
                  }`}
                >
                  <input
                    type="radio"
                    name="rainTolerance"
                    checked={answers.rainTolerance === value}
                    onChange={() =>
                      setAnswers((prev) => ({
                        ...prev,
                        rainTolerance: value,
                      }))
                    }
                    className="accent-green-500"
                  />
                  <span className="text-sm text-gray-200">{label}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {step === 5 && (
          <div>
            <h2 className="text-lg font-bold mb-4">Group size?</h2>
            <p className="text-sm text-gray-400 mb-4">
              How many people are going?
            </p>
            <div className="flex items-center gap-4">
              <button
                onClick={() =>
                  setAnswers((prev) => ({
                    ...prev,
                    groupSize: Math.max(1, prev.groupSize - 1),
                  }))
                }
                className="w-10 h-10 rounded-lg border border-gray-600 bg-gray-900 text-gray-200 hover:border-gray-500 transition-colors text-lg font-bold"
              >
                -
              </button>
              <span className="text-2xl font-bold text-gray-100 w-12 text-center">
                {answers.groupSize}
              </span>
              <button
                onClick={() =>
                  setAnswers((prev) => ({
                    ...prev,
                    groupSize: Math.min(10, prev.groupSize + 1),
                  }))
                }
                className="w-10 h-10 rounded-lg border border-gray-600 bg-gray-900 text-gray-200 hover:border-gray-500 transition-colors text-lg font-bold"
              >
                +
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">1 to 10 people</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        {step > 1 ? (
          <button
            onClick={handleBack}
            className="px-5 py-2.5 rounded-lg border border-gray-600 text-sm text-gray-300 hover:border-gray-500 transition-colors"
          >
            Back
          </button>
        ) : (
          <div />
        )}

        {step < 5 ? (
          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="px-5 py-2.5 rounded-lg bg-green-600 text-sm font-medium text-white hover:bg-green-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!canProceed()}
            className="px-5 py-2.5 rounded-lg bg-green-600 text-sm font-medium text-white hover:bg-green-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            See Results
          </button>
        )}
      </div>
    </div>
  );
}
