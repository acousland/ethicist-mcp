/**
 * Repugnance inference tool for the Ethicist MCP server.
 *
 * This module is self-contained, performs no network I/O, and embeds a compact
 * lookup catalogue plus a deterministic linear model with lexical fallbacks.
 *
 * Compile:  tsc repugnance-infer.ts --target ES2020 --module commonjs
 * Run CLI:  node repugnance-infer.js "Marriage and Family Therapist"
 * Self-test: MCP_SELFTEST=1 node repugnance-infer.js
 */

// Lightweight MCP tool registration interfaces to avoid external imports.
export interface JsonSchema {
  [key: string]: unknown;
}

export interface McpToolDefinition {
  name: string;
  description: string;
  inputSchema: JsonSchema;
  outputSchema: JsonSchema;
}

export interface McpServerLike {
  registerTool: (
    definition: McpToolDefinition,
    handler: (args: Record<string, unknown>) => Promise<RepugnanceResult>
  ) => void;
}

export type Band = "repugnant" | "ambivalent" | "permissible";
export type Method = "lookup" | "model" | "rules";

export interface NearestOccupation {
  title: string;
  sim: number;
}

export interface RepugnanceResult {
  title_normalised: string;
  score: number;
  band: Band;
  confidence: number;
  method: Method;
  nearest: NearestOccupation[];
  rationale: string;
  model_version: string;
  reference_snapshot: string;
}

const EMBEDDING_DIM = 64;
const MODEL_VERSION = "repugnance-linear-0.1.0";
const REFERENCE_SNAPSHOT = "2024-06-30";

// Canonical lookup scores (placeholders – extend in production as coverage grows).
const GOLD_SCORES: Record<string, number> = {
  "palliative care nurse": 6.2,
  "aged care worker": 5.8,
  "funeral director": 6.1,
  "paramedic": 5.4,
  "nurse practitioner": 5.6,
  "midwife": 6.0,
  "judge": 5.9,
  "priest": 5.7,
  "police officer": 4.8,
  "mortuary technician": 5.2,
  "social worker": 5.4,
  "marriage and family therapist": 5.5,
  "hospital nurse": 5.4,
  "software engineer": 2.2,
  "data scientist": 2.0,
  "accountant": 2.4,
  "call center operator": 2.6,
  "receptionist": 2.8,
  "warehouse operative": 2.5,
  "customer service representative": 2.7,
  "firefighter": 5.0
};

// Lexicon patterns – expand carefully to tune tier C behaviour.
const LEXICONS: Record<string, RegExp[]> = {
  caregiving: [
    /\bnurse\b/,
    /\bcare\b/,
    /\baide\b/,
    /\bmidwif/,
    /\bcarer\b/,
    /\bchild\s*care\b/,
    /\baged\b/,
    /\bpalliative\b/,
    /\bsocial worker\b/,
    /\bparamedic\b/
  ],
  therapy: [
    /\btherap/,
    /\bcounsel/,
    /\bpsycholog/,
    /\bbehavio[u]?r(al)?\b/,
    /\bmental health\b/
  ],
  spiritual: [
    /\bpriest\b/,
    /\bchaplain\b/,
    /\bimam\b/,
    /\bpastor\b/,
    /\bminister\b/,
    /\bfaith\b/,
    /\bspiritual\b/
  ],
  policingJudiciary: [
    /\bpolice\b/,
    /\bofficer\b/,
    /\bjudge\b/,
    /\bmagistr/,
    /\bprobation\b/,
    /\bjustice\b/,
    /\bcorrection/,
    /\bdetective\b/
  ],
  funerary: [
    /\bfuneral\b/,
    /\bmortician\b/,
    /\bmortuary\b/,
    /\bem[bs]alm/,
    /\bundertaker\b/
  ],
  clerical: [
    /\breceptionist\b/,
    /\bclerk\b/,
    /\badministr/,
    /\bassistant\b/,
    /\bdata entry\b/,
    /\bcall centre\b/,
    /\bcustomer service\b/,
    /\bscheduler\b/
  ],
  technicalAnalytical: [
    /\bengineer\b/,
    /\bscientist\b/,
    /\bdeveloper\b/,
    /\bprogrammer\b/,
    /\banalyst\b/,
    /\btechnician\b/,
    /\bit support\b/,
    /\bdesigner\b/,
    /\barchitect\b/
  ],
  manualMaintenance: [
    /\bmechanic\b/,
    /\bplumber\b/,
    /\belectrician\b/,
    /\bjanitor\b/,
    /\bcleaner\b/,
    /\bmaintenance\b/,
    /\bgroundskeeper\b/,
    /\bwarehouse\b/,
    /\bdriver\b/,
    /\bcarpenter\b/,
    /\bgardener\b/
  ],
  artPerformance: [
    /\bartist\b/,
    /\bmusician\b/,
    /\bactor\b/,
    /\bperformer\b/,
    /\bsinger\b/,
    /\bdancer\b/,
    /\bcoach\b/,
    /\bathlete\b/
  ]
};

interface OccupationRecord {
  title: string;
  normalised: string;
  description: string;
  vector: number[];
}

interface FeatureFlags {
  isCaregiving: boolean;
  isTherapy: boolean;
  isSpiritual: boolean;
  isPolicingJudiciary: boolean;
  isFunerary: boolean;
  isClerical: boolean;
  isTechnicalAnalytical: boolean;
  isManualMaintenance: boolean;
  isArtPerformance: boolean;
}

interface ModelWeights {
  bias: number;
  embedding: number[];
  isCaregiving: number;
  isTherapy: number;
  isSpiritual: number;
  isPolicingJudiciary: number;
  isFunerary: number;
  isClerical: number;
  isTechnicalAnalytical: number;
  isManualMaintenance: number;
  isArtPerformance: number;
}

const MODEL_WEIGHTS: ModelWeights = {
  bias: 3.7,
  // Embedding interaction weights (deterministic, bounded within ±0.15).
  embedding: [
    0.08, -0.05, 0.04, -0.02, 0.06, -0.01, 0.03, -0.04,
    0.02, 0.01, -0.06, 0.05, -0.08, 0.07, -0.03, 0.04,
    0.06, -0.07, 0.05, -0.02, 0.01, 0.05, -0.06, 0.04,
    0.07, -0.08, 0.03, -0.04, 0.02, 0.01, -0.05, 0.06,
    -0.07, 0.03, 0.05, -0.02, 0.04, -0.01, 0.02, 0.05,
    -0.06, 0.04, 0.07, -0.05, 0.03, -0.04, 0.02, 0.01,
    -0.03, 0.05, -0.06, 0.04, 0.06, -0.07, 0.05, -0.03,
    0.02, 0.01, -0.04, 0.05, -0.06, 0.04, 0.02, -0.05
  ],
  // Category coefficients (bounded within ±0.4 as per design guidance).
  isCaregiving: 0.38,
  isTherapy: 0.34,
  isSpiritual: 0.36,
  isPolicingJudiciary: 0.32,
  isFunerary: 0.33,
  isClerical: -0.32,
  isTechnicalAnalytical: -0.37,
  isManualMaintenance: -0.28,
  isArtPerformance: 0.12
};

const OCCUPATIONS_SOURCE: Array<{ title: string; description: string }> = [
  { title: "Palliative Care Nurse", description: "Provides end-of-life nursing, pain management, and family support in hospice settings." },
  { title: "Aged Care Worker", description: "Supports older Australians with daily living, personal care, and companionship needs." },
  { title: "Funeral Director", description: "Oversees funeral arrangements, family liaison, and bereavement support." },
  { title: "Paramedic", description: "Delivers emergency medical care and transport in critical situations." },
  { title: "Nurse Practitioner", description: "Advanced practice nurse delivering diagnosis, treatment, and patient counselling." },
  { title: "Midwife", description: "Guides prenatal care, labour support, and postnatal wellbeing for parents and infants." },
  { title: "Judge", description: "Adjudicates legal cases, interprets law, and delivers binding decisions affecting rights." },
  { title: "Priest", description: "Provides spiritual leadership, pastoral care, and community rites." },
  { title: "Police Officer", description: "Enforces law, responds to emergencies, and protects community safety." },
  { title: "Mortuary Technician", description: "Prepares deceased individuals, supports pathologists, and assists families." },
  { title: "Social Worker", description: "Assists individuals and families with welfare, safeguarding, and complex psychosocial needs." },
  { title: "Marriage and Family Therapist", description: "Delivers therapeutic counselling for couples and families navigating conflict." },
  { title: "Childcare Worker", description: "Provides care, development activities, and safeguarding for young children." },
  { title: "Primary School Teacher", description: "Teaches foundational curriculum, pastoral care, and learning support for primary students." },
  { title: "Secondary School Teacher", description: "Delivers subject teaching, wellbeing support, and assessment for adolescents." },
  { title: "University Lecturer", description: "Facilitates tertiary education, research supervision, and student mentorship." },
  { title: "Psychologist", description: "Offers psychological assessment, therapy, and mental health interventions." },
  { title: "Counsellor", description: "Provides counselling services for personal, social, or vocational challenges." },
  { title: "Chaplain", description: "Delivers spiritual care within institutions, guiding individuals and families." },
  { title: "Police Detective", description: "Investigates serious crimes, interviews witnesses, and prepares prosecution briefs." },
  { title: "Probation Officer", description: "Supports offender rehabilitation, supervises compliance, and advises courts." },
  { title: "Funeral Celebrant", description: "Leads funeral ceremonies, coordinates rituals, and supports grieving families." },
  { title: "Software Engineer", description: "Designs, builds, and maintains software systems and digital products." },
  { title: "Data Scientist", description: "Develops analytical models, interprets data insights, and supports decision making." },
  { title: "Civil Engineer", description: "Plans and oversees infrastructure projects, ensuring safety and compliance." },
  { title: "Electrical Engineer", description: "Designs and maintains electrical systems for industry and consumers." },
  { title: "Mechanical Engineer", description: "Builds and maintains machines, equipment, and mechanical processes." },
  { title: "Accountant", description: "Manages financial records, compliance, and reporting for organisations." },
  { title: "Bookkeeper", description: "Performs routine financial recording, reconciliations, and invoice processing." },
  { title: "Call Centre Operator", description: "Handles high-volume customer enquiries, scripts, and issue triage." },
  { title: "Receptionist", description: "Manages front-of-house duties, appointment scheduling, and customer queries." },
  { title: "Customer Service Representative", description: "Provides customer support, issue resolution, and product guidance." },
  { title: "Warehouse Operative", description: "Executes picking, packing, and inventory tasks in logistics facilities." },
  { title: "Truck Driver", description: "Transports goods long-distance, adhering to safety and delivery schedules." },
  { title: "Delivery Driver", description: "Performs local deliveries, parcel handling, and customer interactions." },
  { title: "Janitor", description: "Maintains facility cleanliness, waste handling, and basic repairs." },
  { title: "Cleaner", description: "Provides cleaning services for homes, offices, and public facilities." },
  { title: "Plumber", description: "Installs and repairs water, drainage, and heating systems." },
  { title: "Electrician", description: "Installs and services electrical wiring, systems, and equipment." },
  { title: "Carpenter", description: "Constructs and repairs timber structures, fixtures, and fittings." },
  { title: "Mechanic", description: "Diagnoses and repairs mechanical and automotive systems." },
  { title: "Groundskeeper", description: "Maintains outdoor grounds, landscaping, and basic horticulture." },
  { title: "Gardener", description: "Provides horticultural care, planting, and garden maintenance." },
  { title: "Graphic Designer", description: "Creates visual designs for branding, marketing, and digital media." },
  { title: "UX Designer", description: "Designs user experiences, conducts research, and prototypes digital products." },
  { title: "Product Manager", description: "Defines product strategy, prioritises features, and coordinates delivery teams." },
  { title: "Business Analyst", description: "Documents requirements, analyses processes, and supports solution design." },
  { title: "Human Resources Manager", description: "Oversees workforce planning, employee relations, and compliance." },
  { title: "Recruiter", description: "Sources, screens, and places candidates into roles." },
  { title: "Firefighter", description: "Responds to fires, rescues, and emergency incidents protecting life and property." },
  { title: "Emergency Dispatcher", description: "Coordinates emergency calls, dispatches services, and provides guidance." },
  { title: "Pharmacist", description: "Dispenses medication, counsel patients, and ensures safe pharmaceutical practice." },
  { title: "Phlebotomist", description: "Collects blood samples, maintains sterile technique, and comforts patients." },
  { title: "Dental Hygienist", description: "Provides preventative dental care, scaling, and oral health education." },
  { title: "General Practitioner", description: "Delivers primary medical care, diagnosis, and patient management." },
  { title: "Surgeon", description: "Performs surgical procedures, manages operative risks, and leads clinical teams." },
  { title: "Physiotherapist", description: "Delivers physical rehabilitation, mobility support, and pain management." },
  { title: "Occupational Therapist", description: "Supports functional independence through therapy and adaptive strategies." },
  { title: "Speech Pathologist", description: "Treats speech, language, and swallowing disorders across age groups." },
  { title: "Dietitian", description: "Develops nutrition plans, clinical dietary advice, and health promotion." },
  { title: "Art Therapist", description: "Uses creative practice to support mental health and emotional wellbeing." },
  { title: "Music Therapist", description: "Employs music-based interventions for therapeutic outcomes." },
  { title: "Museum Curator", description: "Manages collections, exhibitions, and cultural programming." },
  { title: "Archivist", description: "Preserves records, manages archives, and provides access to historical materials." },
  { title: "Librarian", description: "Curates information resources, supports literacy, and community programs." },
  { title: "Sports Coach", description: "Develops athletic performance, mentorship, and team strategy." },
  { title: "Professional Athlete", description: "Competes at elite level sporting events, training rigorously." },
  { title: "Chef", description: "Designs menus, leads kitchen operations, and ensures food quality." },
  { title: "Barista", description: "Prepares coffee beverages, customer service, and cafe operations." },
  { title: "Waiter", description: "Provides table service, customer care, and order coordination." },
  { title: "Security Guard", description: "Monitors premises, enforces rules, and responds to incidents." },
  { title: "Immigration Officer", description: "Assesses entry applications, border compliance, and traveller support." },
  { title: "Prison Chaplain", description: "Provides faith-based counselling, rehabilitation support, and rituals in correctional settings." },
  { title: "Community Liaison Officer", description: "Engages communities, mediates concerns, and supports social cohesion." },
  { title: "Event Planner", description: "Organises events, vendor coordination, and attendee experience." },
  { title: "Marketing Manager", description: "Develops marketing strategies, campaigns, and stakeholder engagement." },
  { title: "Research Scientist", description: "Conducts scientific experiments, publishes findings, and advances knowledge." },
  { title: "Environmental Scientist", description: "Monitors ecosystems, assesses environmental impacts, and advises policy." }
];

const OCCS: OccupationRecord[] = OCCUPATIONS_SOURCE.map((entry) => {
  const normalised = normaliseTitle(entry.title);
  const vector = createEmbedding(`${entry.title} ${entry.description}`);
  return {
    title: entry.title,
    normalised,
    description: entry.description,
    vector
  };
});

const HARMONISE_MAP: Array<[RegExp, string]> = [
  [/counsellor/g, "counselor"],
  [/behaviour/g, "behavior"],
  [/labour/g, "labor"],
  [/organis(e|ation)/g, "organiz$1"],
  [/specialis(e|ation)/g, "specializ$1"],
  [/favour/g, "favor"],
  [/harbour/g, "harbor"],
  [/centre/g, "center"],
  [/defence/g, "defense"],
  [/licen[cs]e/g, "license"],
  [/judgement/g, "judgment"]
];

function normaliseTitle(input: string): string {
  let value = (input || "").toLowerCase();
  value = value.normalize("NFKD");
  value = value.replace(/[\u0300-\u036f]/g, "");
  for (const [pattern, replacement] of HARMONISE_MAP) {
    value = value.replace(pattern, replacement);
  }
  value = value.replace(/[^a-z0-9\s]/g, " ");
  value = value.replace(/\s+/g, " ").trim();
  return value;
}

function hashNgram(text: string): number {
  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash | 0;
}

function createEmbedding(text: string): number[] {
  const cleaned = normaliseTitle(text);
  if (!cleaned) {
    return new Array(EMBEDDING_DIM).fill(0);
  }
  const tokens = cleaned.split(" ");
  const vector = new Array(EMBEDDING_DIM).fill(0);
  for (const token of tokens) {
    const padded = `_${token}_`;
    for (let n = 2; n <= 3; n += 1) {
      for (let i = 0; i <= padded.length - n; i += 1) {
        const ngram = padded.slice(i, i + n);
        const idx = Math.abs(hashNgram(ngram)) % EMBEDDING_DIM;
        vector[idx] += 1;
      }
    }
  }
  const denom = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
  if (denom > 0) {
    for (let i = 0; i < vector.length; i += 1) {
      vector[i] = vector[i] / denom;
    }
  }
  return vector;
}

function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < Math.min(a.length, b.length); i += 1) {
    const av = a[i];
    const bv = b[i];
    dot += av * bv;
    normA += av * av;
    normB += bv * bv;
  }
  if (normA === 0 || normB === 0) {
    return 0;
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function deriveFlags(text: string): FeatureFlags {
  const source = normaliseTitle(text);
  const flags: FeatureFlags = {
    isCaregiving: matchesAny(LEXICONS.caregiving, source),
    isTherapy: matchesAny(LEXICONS.therapy, source),
    isSpiritual: matchesAny(LEXICONS.spiritual, source),
    isPolicingJudiciary: matchesAny(LEXICONS.policingJudiciary, source),
    isFunerary: matchesAny(LEXICONS.funerary, source),
    isClerical: matchesAny(LEXICONS.clerical, source),
    isTechnicalAnalytical: matchesAny(LEXICONS.technicalAnalytical, source),
    isManualMaintenance: matchesAny(LEXICONS.manualMaintenance, source),
    isArtPerformance: matchesAny(LEXICONS.artPerformance, source)
  };
  return flags;
}

function matchesAny(patterns: RegExp[], text: string): boolean {
  return patterns.some((pattern) => pattern.test(text));
}

function linearModelScore(vector: number[], flags: FeatureFlags): number {
  let score = MODEL_WEIGHTS.bias;
  const embedWeights = MODEL_WEIGHTS.embedding;
  const length = Math.min(vector.length, embedWeights.length);
  for (let i = 0; i < length; i += 1) {
    score += vector[i] * embedWeights[i];
  }
  score += flags.isCaregiving ? MODEL_WEIGHTS.isCaregiving : 0;
  score += flags.isTherapy ? MODEL_WEIGHTS.isTherapy : 0;
  score += flags.isSpiritual ? MODEL_WEIGHTS.isSpiritual : 0;
  score += flags.isPolicingJudiciary ? MODEL_WEIGHTS.isPolicingJudiciary : 0;
  score += flags.isFunerary ? MODEL_WEIGHTS.isFunerary : 0;
  score += flags.isClerical ? MODEL_WEIGHTS.isClerical : 0;
  score += flags.isTechnicalAnalytical ? MODEL_WEIGHTS.isTechnicalAnalytical : 0;
  score += flags.isManualMaintenance ? MODEL_WEIGHTS.isManualMaintenance : 0;
  score += flags.isArtPerformance ? MODEL_WEIGHTS.isArtPerformance : 0;
  return clamp(score, 1, 7);
}

function scoreToBand(score: number, intervalWidth: number): Band {
  const lower = clamp(score - intervalWidth, 1, 7);
  const upper = clamp(score + intervalWidth, 1, 7);
  if (lower > 4.0) {
    return "repugnant";
  }
  if (upper < 4.0) {
    return "permissible";
  }
  return "ambivalent";
}

function formatRationale(parts: string[]): string {
  if (parts.length === 0) {
    return "Applied default heuristics, considered ethical salience, and returned a conservative midpoint.";
  }
  if (parts.length === 1) {
    return parts[0];
  }
  if (parts.length === 2) {
    return `${parts[0]} and ${parts[1]}`;
  }
  const head = parts.slice(0, -1).join(", ");
  const tail = parts[parts.length - 1];
  return `${head}, and ${tail}`;
}

function describeFlags(flags: FeatureFlags): string[] {
  const parts: string[] = [];
  if (flags.isCaregiving) {
    parts.push("highlighted caregiving responsibilities");
  }
  if (flags.isTherapy) {
    parts.push("noted therapeutic or counselling duties");
  }
  if (flags.isSpiritual) {
    parts.push("considered spiritual guidance");
  }
  if (flags.isPolicingJudiciary) {
    parts.push("accounted for coercive authority");
  }
  if (flags.isFunerary) {
    parts.push("identified funerary rituals");
  }
  if (flags.isClerical) {
    parts.push("observed clerical routine cues");
  }
  if (flags.isTechnicalAnalytical) {
    parts.push("recognised technical or analytical focus");
  }
  if (flags.isManualMaintenance) {
    parts.push("saw manual or maintenance workload");
  }
  if (flags.isArtPerformance) {
    parts.push("acknowledged artistic or performance elements");
  }
  return parts;
}

interface InferenceContext {
  titleInput: string;
  normalisedTitle: string;
  embedding: number[];
  neighbours: NearestOccupation[];
  bestNeighbour?: OccupationRecord;
  bestSimilarity: number;
}

function buildInferenceContext(jobTitle: string): InferenceContext {
  const normalisedTitle = normaliseTitle(jobTitle);
  const embedding = createEmbedding(jobTitle);
  const neighbourScores = OCCS.map((occ) => ({
    occ,
    sim: cosineSimilarity(embedding, occ.vector)
  }));
  neighbourScores.sort((a, b) => b.sim - a.sim);
  const nearest = neighbourScores.slice(0, 5).map((entry) => ({
    title: entry.occ.title,
    sim: Number(entry.sim.toFixed(3))
  }));
  const best = neighbourScores.length > 0 ? neighbourScores[0] : undefined;
  return {
    titleInput: jobTitle,
    normalisedTitle,
    embedding,
    neighbours: nearest,
    bestNeighbour: best?.occ,
    bestSimilarity: best?.sim ?? 0
  };
}

function hasEmbeddingSignal(vector: number[]): boolean {
  return vector.some((value) => Math.abs(value) > 0);
}

function tierLookup(context: InferenceContext): RepugnanceResult | null {
  const directScore = GOLD_SCORES[context.normalisedTitle];
  if (typeof directScore === "number") {
    const rationale = formatRationale([
      `Matched directly to "${context.normalisedTitle}" in the gold reference`,
      "applied high-confidence lookup",
      "returned stored repugnance score"
    ]);
    return {
      title_normalised: context.normalisedTitle,
      score: Number(directScore.toFixed(2)),
      band: scoreToBand(directScore, 0.25),
      confidence: 0.95,
      method: "lookup",
      nearest: context.neighbours,
      rationale,
      model_version: MODEL_VERSION,
      reference_snapshot: REFERENCE_SNAPSHOT
    };
  }

  const best = context.bestNeighbour;
  if (!best) {
    return null;
  }
  const bestGold = GOLD_SCORES[best.normalised];
  if (typeof bestGold !== "number" || context.bestSimilarity < 0.85) {
    return null;
  }
  const similarityPenalty = (1 - context.bestSimilarity) * 0.6;
  const adjusted = clamp(bestGold - similarityPenalty, 1, 7);
  const rationale = formatRationale([
    `Mapped to "${best.title}" based on high semantic similarity`,
    "reused gold reference score with a similarity adjustment",
    "documented inference for transparency"
  ]);
  const confidence = Number((0.8 + context.bestSimilarity * 0.12).toFixed(2));
  return {
    title_normalised: context.normalisedTitle,
    score: Number(adjusted.toFixed(2)),
    band: scoreToBand(adjusted, 0.35),
    confidence,
    method: "lookup",
    nearest: context.neighbours,
    rationale,
    model_version: MODEL_VERSION,
    reference_snapshot: REFERENCE_SNAPSHOT
  };
}

function tierModel(context: InferenceContext): RepugnanceResult | null {
  if (!hasEmbeddingSignal(context.embedding)) {
    return null;
  }
  if (context.bestSimilarity < 0.6) {
    return null;
  }
  const neighbour = context.bestNeighbour;
  const compositeText = neighbour
    ? `${context.titleInput} ${neighbour.title} ${neighbour.description}`
    : context.titleInput;
  const flags = deriveFlags(compositeText);
  const rawScore = linearModelScore(context.embedding, flags);
  const intervalWidth = context.bestSimilarity >= 0.9 ? 0.35 : 0.5;
  const band = scoreToBand(rawScore, intervalWidth);
  const flagInsights = describeFlags(flags);
  const parts = [
    neighbour
      ? `Referenced "${neighbour.title}" as the closest occupation`
      : "Used best-available semantic neighbour",
    flagInsights.length > 0
      ? formatRationale(flagInsights)
      : "Observed limited categorical cues",
    "Applied embedded linear model to synthesise the score"
  ];
  const confidenceBase = 0.55 + 0.25 * context.bestSimilarity;
  const confidence = Number(clamp(confidenceBase - intervalWidth * 0.1, 0.45, 0.9).toFixed(2));
  return {
    title_normalised: context.normalisedTitle,
    score: Number(rawScore.toFixed(2)),
    band,
    confidence,
    method: "model",
    nearest: context.neighbours,
    rationale: formatRationale(parts),
    model_version: MODEL_VERSION,
    reference_snapshot: REFERENCE_SNAPSHOT
  };
}

function tierRules(context: InferenceContext): RepugnanceResult {
  const title = context.normalisedTitle;
  let score = 3.8;
  const reasons: string[] = [];

  if (!title) {
    score = 3.8;
    reasons.push("Received empty title");
  }

  const caregiving = matchesAny(LEXICONS.caregiving, title);
  const therapy = matchesAny(LEXICONS.therapy, title);
  const spiritual = matchesAny(LEXICONS.spiritual, title);
  const judiciary = matchesAny(LEXICONS.policingJudiciary, title);
  const funerary = matchesAny(LEXICONS.funerary, title);
  const clerical = matchesAny(LEXICONS.clerical, title);
  const technical = matchesAny(LEXICONS.technicalAnalytical, title);

  if (caregiving || therapy || spiritual || judiciary || funerary) {
    score = 5.4;
    reasons.push("Detected highly sensitive caregiving, justice, or rites");
  } else if (clerical || technical) {
    score = 2.4;
    reasons.push("Detected routine clerical or technical patterns");
  } else {
    score = 3.8;
    reasons.push("Defaulted to neutral baseline");
  }

  if (caregiving && therapy) {
    score += 0.3;
    reasons.push("Elevated for blended care and therapy cues");
  }
  if (spiritual) {
    score += 0.2;
    reasons.push("Elevated for spiritual references");
  }
  if (technical && !caregiving && !therapy) {
    score -= 0.3;
    reasons.push("Tempered due to strongly technical orientation");
  }

  score = clamp(score, 1, 7);
  const intervalWidth = 0.6;
  return {
    title_normalised: title,
    score: Number(score.toFixed(2)),
    band: scoreToBand(score, intervalWidth),
    confidence: 0.35,
    method: "rules",
    nearest: context.neighbours,
    rationale: formatRationale([
      "Applied lexical rules given low similarity coverage",
      ...reasons
    ]),
    model_version: MODEL_VERSION,
    reference_snapshot: REFERENCE_SNAPSHOT
  };
}

export function inferRepugnance(jobTitle: string): RepugnanceResult {
  const context = buildInferenceContext(jobTitle);
  let result = tierLookup(context);
  if (result) {
    return result;
  }
  result = tierModel(context);
  if (result) {
    return result;
  }
  return tierRules(context);
}

export function registerRepugnanceInferTool(server: McpServerLike): void {
  const definition: McpToolDefinition = {
    name: "repugnance-infer",
    description: "Infer a repugnance-to-automate score for a given job title using embedded ethical heuristics.",
    inputSchema: {
      type: "object",
      properties: {
        job_title: { type: "string" }
      },
      required: ["job_title"]
    },
    outputSchema: {
      type: "object",
      properties: {
        title_normalised: { type: "string" },
        score: { type: "number" },
        band: { type: "string", enum: ["repugnant", "ambivalent", "permissible"] },
        confidence: { type: "number" },
        method: { type: "string", enum: ["lookup", "model", "rules"] },
        nearest: {
          type: "array",
          items: {
            type: "object",
            properties: {
              title: { type: "string" },
              sim: { type: "number" }
            },
            required: ["title", "sim"]
          }
        },
        rationale: { type: "string" },
        model_version: { type: "string" },
        reference_snapshot: { type: "string" }
      },
      required: [
        "title_normalised",
        "score",
        "band",
        "confidence",
        "method",
        "nearest",
        "rationale",
        "model_version",
        "reference_snapshot"
      ]
    }
  };

  server.registerTool(definition, async (args) => {
    const jobTitle = typeof args.job_title === "string" ? args.job_title : "";
    return inferRepugnance(jobTitle);
  });
}

function runCli(): void {
  const [, , ...rest] = process.argv;
  if (rest.length === 0) {
    console.error("Usage: node repugnance-infer.js \"Job Title\"");
    process.exitCode = 1;
    return;
  }
  const title = rest.join(" ");
  const result = inferRepugnance(title);
  console.log(JSON.stringify(result, null, 2));
}

interface SelfTestCase {
  title: string;
  expectedBand: Band;
}

function runSelfTests(): void {
  const cases: SelfTestCase[] = [
    { title: "Hospital Nurse", expectedBand: "repugnant" },
    { title: "Software Engineer", expectedBand: "permissible" },
    { title: "Museum Curator", expectedBand: "ambivalent" },
    { title: "Funeral Director", expectedBand: "repugnant" },
    { title: "Call Centre Operator", expectedBand: "permissible" }
  ];
  const failures: string[] = [];

  for (const testCase of cases) {
    const outcome = inferRepugnance(testCase.title);
    if (outcome.band !== testCase.expectedBand) {
      failures.push(
        `${testCase.title} => expected ${testCase.expectedBand} but received ${outcome.band} (score ${outcome.score})`
      );
    }
  }

  if (failures.length > 0) {
    console.error("Self-test failures:");
    for (const failure of failures) {
      console.error(` - ${failure}`);
    }
    process.exitCode = 1;
  } else {
    console.log("Self-test passed.");
  }
}

if (require.main === module) {
  if (process.env.MCP_SELFTEST === "1") {
    runSelfTests();
  } else {
    runCli();
  }
}
