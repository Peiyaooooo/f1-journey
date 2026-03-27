export function detectUserCurrency(): string {
  if (typeof navigator === "undefined") return "USD";
  const locale = navigator.language || "en-US";
  const regionCurrencies: Record<string, string> = {
    "en-US": "USD", "en-GB": "GBP", "en-AU": "AUD", "en-CA": "CAD",
    "de": "EUR", "fr": "EUR", "es": "EUR", "it": "EUR", "nl": "EUR",
    "pt-BR": "BRL", "ja": "JPY", "zh": "CNY", "ko": "KRW",
    "ar": "AED", "hi": "INR", "ru": "RUB", "tr": "TRY",
  };
  const lang = locale.split("-").slice(0, 2).join("-");
  return regionCurrencies[lang] || regionCurrencies[locale.split("-")[0]] || "USD";
}

export function convertCurrency(
  amountUsd: number,
  rates: Record<string, number>,
  targetCurrency: string
): number {
  const rate = rates[targetCurrency] || 1;
  return amountUsd * rate;
}

export function formatCurrency(amount: number, currency: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}
