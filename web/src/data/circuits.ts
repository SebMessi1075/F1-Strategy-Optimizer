import type { Circuit } from "@/types/api";

/** Static circuit list, generated from models/circuits.json at build time.
 *  Bundled so the selector is usable instantly, with no dependency on the
 *  API being awake. The live API list refreshes this in the background. */
export const CIRCUITS: Circuit[] = [
  { slug: "albert_park", name: "Albert Park", typical_laps: 57, median_pace: 89.6, gp: "Australian Grand Prix" },
  { slug: "americas", name: "Americas", typical_laps: 56, median_pace: 102.6, gp: "United States Grand Prix" },
  { slug: "bahrain", name: "Bahrain", typical_laps: 57, median_pace: 97.8, gp: "Bahrain Grand Prix" },
  { slug: "baku", name: "Baku", typical_laps: 51, median_pace: 108.5, gp: "Azerbaijan Grand Prix" },
  { slug: "catalunya", name: "Catalunya", typical_laps: 65, median_pace: 85.7, gp: "Spanish Grand Prix" },
  { slug: "hockenheimring", name: "Hockenheimring", typical_laps: 66, median_pace: 82.3, gp: "German Grand Prix" },
  { slug: "hungaroring", name: "Hungaroring", typical_laps: 69, median_pace: 84.7, gp: "Hungarian Grand Prix" },
  { slug: "imola", name: "Imola", typical_laps: 63, median_pace: 81.4, gp: "Emilia Romagna Grand Prix" },
  { slug: "interlagos", name: "Interlagos", typical_laps: 71, median_pace: 76.1, gp: "Brazilian Grand Prix" },
  { slug: "istanbul", name: "Istanbul", typical_laps: 58, median_pace: 97.1, gp: "Turkish Grand Prix" },
  { slug: "jeddah", name: "Jeddah", typical_laps: 50, median_pace: 94.8, gp: "Saudi Arabian Grand Prix" },
  { slug: "losail", name: "Losail", typical_laps: 57, median_pace: 88.1, gp: "Qatar Grand Prix" },
  { slug: "marina_bay", name: "Marina Bay", typical_laps: 61, median_pace: 110, gp: "Singapore Grand Prix" },
  { slug: "miami", name: "Miami", typical_laps: 57, median_pace: 93.4, gp: "Miami Grand Prix" },
  { slug: "monaco", name: "Monaco", typical_laps: 77, median_pace: 79.3, gp: "Monaco Grand Prix" },
  { slug: "monza", name: "Monza", typical_laps: 53, median_pace: 86.9, gp: "Italian Grand Prix" },
  { slug: "mugello", name: "Mugello", typical_laps: 59, median_pace: 83.7, gp: "Tuscan Grand Prix" },
  { slug: "nurburgring", name: "Nurburgring", typical_laps: 60, median_pace: 92.9, gp: "Eifel Grand Prix" },
  { slug: "portimao", name: "Portimao", typical_laps: 65, median_pace: 82.9, gp: "Portuguese Grand Prix" },
  { slug: "red_bull_ring", name: "Red Bull Ring", typical_laps: 70, median_pace: 70.7, gp: "Austrian Grand Prix" },
  { slug: "ricard", name: "Ricard", typical_laps: 53, median_pace: 98.9, gp: "French Grand Prix" },
  { slug: "rodriguez", name: "Rodriguez", typical_laps: 70, median_pace: 83.4, gp: "Mexican Grand Prix" },
  { slug: "sepang", name: "Sepang", typical_laps: 55, median_pace: 103.3, gp: "Malaysian Grand Prix" },
  { slug: "shanghai", name: "Shanghai", typical_laps: 56, median_pace: 102.2, gp: "Chinese Grand Prix" },
  { slug: "silverstone", name: "Silverstone", typical_laps: 52, median_pace: 93.7, gp: "British Grand Prix" },
  { slug: "sochi", name: "Sochi", typical_laps: 53, median_pace: 102, gp: "Russian Grand Prix" },
  { slug: "spa", name: "Spa", typical_laps: 44, median_pace: 112.6, gp: "Belgian Grand Prix" },
  { slug: "suzuka", name: "Suzuka", typical_laps: 52, median_pace: 98.4, gp: "Japanese Grand Prix" },
  { slug: "vegas", name: "Vegas", typical_laps: 50, median_pace: 98.6, gp: "Las Vegas Grand Prix" },
  { slug: "villeneuve", name: "Villeneuve", typical_laps: 69, median_pace: 78.6, gp: "Canadian Grand Prix" },
  { slug: "yas_marina", name: "Yas Marina", typical_laps: 55, median_pace: 103.5, gp: "Abu Dhabi Grand Prix" },
  { slug: "zandvoort", name: "Zandvoort", typical_laps: 72, median_pace: 76.6, gp: "Dutch Grand Prix" },
];
