// Maps circuit name (from API) to the image filename in /maps/
const CIRCUIT_MAP_IMAGES: Record<string, string> = {
  "Albert Park Circuit": "albert-park.jpg",
  "Shanghai International Circuit": "shanghai.jpg",
  "Suzuka International Racing Course": "suzuka.jpg",
  "Miami International Autodrome": "miami.jpg",
  "Circuit Gilles Villeneuve": "montreal.jpg",
  "Circuit de Monaco": "monaco.png",
  "Circuit de Barcelona-Catalunya": "barcelona.jpg",
  "Red Bull Ring": "austria.jpg",
  "Silverstone Circuit": "silverstone.png",
  "Circuit de Spa-Francorchamps": "spa.jpg",
  "Hungaroring": "hungaroring.jpg",
  "Circuit Zandvoort": "zandvoort.jpg",
  "Autodromo Nazionale di Monza": "monza.png",
  "Madrid Street Circuit": "madrid.jpg",
  "Baku City Circuit": "baku.jpg",
  "Marina Bay Street Circuit": "singapore.jpg",
  "Circuit of the Americas": "austin.jpg",
  "Autodromo Hermanos Rodriguez": "mexico-city.jpg",
  "Interlagos": "interlagos.png",
  "Las Vegas Street Circuit": "las-vegas.jpg",
  "Losail International Circuit": "qatar.jpg",
  "Yas Marina Circuit": "abu-dhabi.jpg",
};

export function getCircuitMapImage(circuitName: string): string | null {
  return CIRCUIT_MAP_IMAGES[circuitName]
    ? `/maps/${CIRCUIT_MAP_IMAGES[circuitName]}`
    : null;
}
