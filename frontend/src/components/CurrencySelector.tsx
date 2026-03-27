"use client";

const CURRENCIES = [
  "USD", "EUR", "GBP", "AUD", "CAD", "JPY", "CNY", "BRL",
  "MXN", "SGD", "AED", "CHF", "SEK", "NOK", "DKK", "PLN",
  "HUF", "CZK", "TRY", "INR", "KRW", "THB", "MYR",
];

interface CurrencySelectorProps {
  value: string;
  onChange: (currency: string) => void;
}

export default function CurrencySelector({ value, onChange }: CurrencySelectorProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-2 py-1"
    >
      {CURRENCIES.map((c) => (
        <option key={c} value={c}>{c}</option>
      ))}
    </select>
  );
}
