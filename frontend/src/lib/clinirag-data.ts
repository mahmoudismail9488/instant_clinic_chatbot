export type Confidence = "high" | "medium" | "low" | "insufficient";

export type Topic = {
  id: string;
  title: string;
  blurb: string;
  sources: string[];
};

/** Only topics backed by the indexed corpus. */
export const topics: Topic[] = [
  {
    id: "diabetes",
    title: "Diabetes Screening & Adult Type 2 Care",
    blurb:
      "Screening, diagnosis cut-points, and adult type 2 recommendations from the indexed guidelines.",
    sources: [
      "Diabetes-Canada-2024-CPG-Quick-Reference-Guide.pdf",
      "NICE-NG28-Type2-Diabetes-Adults-Recommendations.pdf",
    ],
  },
];

export type EvidenceChunk = {
  id: string;
  doc: string;
  page: number;
  section: string;
  url: string;
  score: number;
  excerpt: string;
  used: boolean;
};

export type Citation = { doc: string; page: number; section: string; chunkId: string };

export type AnswerTurn = {
  kind: "answer";
  id: string;
  question: string;
  caution?: string;
  recommendation: string;
  evidence: { text: string; citation: Citation }[];
  confidence: Confidence;
  /** Evidence-quality index in [0, 1] — not a clinical probability. */
  confidenceScore?: number;
  chunks: EvidenceChunk[];
  status?: string;
  nextAction?: string;
};

export type RefusalTurn = {
  kind: "refusal";
  id: string;
  question: string;
  reason:
    | "Out of scope"
    | "Emergency — seek immediate care"
    | "Insufficient retrieval confidence"
    | "Patient-specific — seek clinical care"
    | "Medication request — consult a clinician";
  detail: string;
  emergencyLine?: string;
  chunks: EvidenceChunk[];
  status?: string;
  nextAction?: string;
  confidence?: Confidence;
  confidenceScore?: number;
};

export type Turn = AnswerTurn | RefusalTurn;

/** Soft retrieval bias chips — maps to API `section_focus`. */
export const sectionFocusOptions = [
  { id: "any", label: "Any section" },
  { id: "screening", label: "Screening" },
  { id: "diagnosis", label: "Diagnosis" },
  { id: "monitoring", label: "Monitoring" },
  { id: "targets", label: "Targets" },
  { id: "education", label: "Education" },
] as const;

export type SectionFocusId = (typeof sectionFocusOptions)[number]["id"];

export const pipelineStages = [
  { name: "Ingestion", metric: "2 PDFs · Diabetes Canada + NICE NG28" },
  { name: "Chunking", metric: "Config B · 1024 tokens · overlap 100 · section titles" },
  { name: "Embeddings", metric: "BAAI/bge-small-en-v1.5 · cosine" },
  { name: "Retrieval", metric: "Hybrid dense + BM25 RRF · optional section bias" },
  { name: "Guardrails", metric: "Risk classification + medication/safety gates" },
  { name: "Grounded LLM", metric: "Groq chat · citation-constrained" },
  { name: "Claim support", metric: "Coverage + unsupported-claim heuristic" },
  { name: "Evidence Panel", metric: "Chunks with page + section_title" },
];

/** Real Day-2 / Day-4 numbers for the judge view (not demo placeholders). */
export const liveMetrics = [
  {
    label: "Retrieval Precision@5",
    value: "0.433",
    sub: "cfgB bake-off · eval/outputs/LAB_REPORT.md",
  },
  {
    label: "Day 4 behavior pass",
    value: "96%",
    sub: "23/24 benchmark · docs/day4/EVALUATION_RESULTS.md",
  },
  {
    label: "Safety pass rate",
    value: "100%",
    sub: "Refuse / clarify / emergency cases",
  },
  {
    label: "Citation coverage",
    value: "100%",
    sub: "Answered questions · claim↔citation",
  },
  {
    label: "Claim faithfulness",
    value: "100%",
    sub: "Answered questions · unsupported rate 0%",
  },
];
