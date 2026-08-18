export type Confidence = "high" | "medium" | "low" | "insufficient";

export type Topic = {
  id: string;
  title: string;
  blurb: string;
  sources: string[];
};

export const topics: Topic[] = [
  {
    id: "diabetes",
    title: "Diabetes Screening",
    blurb: "Screening age, risk factors, A1C and FPG cut-points (Diabetes Canada + NICE NG28).",
    sources: [
      "Diabetes-Canada-2024-CPG-Quick-Reference-Guide.pdf",
      "NICE-NG28-Type2-Diabetes-Adults-Recommendations.pdf",
    ],
  },
  {
    id: "hypertension",
    title: "Adult Hypertension",
    blurb: "Diagnosis thresholds, first-line therapy, monitoring intervals.",
    sources: ["WHO HTN Guideline 2021", "CDC Hypertension Facts", "NICE NG136"],
  },
  {
    id: "asthma",
    title: "Asthma Guidance",
    blurb: "Stepwise control, inhaled corticosteroid initiation, exacerbations.",
    sources: ["NICE NG80", "WHO Asthma Fact Sheet 2023", "CDC Asthma Data 2024"],
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
  chunks: EvidenceChunk[];
};

export type RefusalTurn = {
  kind: "refusal";
  id: string;
  question: string;
  reason:
    | "Out of scope"
    | "Emergency — seek immediate care"
    | "Insufficient retrieval confidence"
    | "Patient-specific — seek clinical care";
  detail: string;
  emergencyLine?: string;
  chunks: EvidenceChunk[];
};

export type Turn = AnswerTurn | RefusalTurn;

export const demoTurns: Turn[] = [
  {
    kind: "answer",
    id: "t1",
    question: "What blood pressure threshold defines stage 1 hypertension in adults?",
    recommendation:
      "Stage 1 hypertension in adults is defined as an office systolic BP of 140–159 mmHg or diastolic 90–99 mmHg, confirmed on repeated measurement. Confirm with ambulatory or home monitoring before starting pharmacological therapy in low-risk patients.",
    evidence: [
      {
        text: "WHO defines hypertension as systolic ≥140 mmHg and/or diastolic ≥90 mmHg on two separate days.",
        citation: { doc: "WHO HTN Guideline 2021", page: 12, section: "§3.2", chunkId: "who-htn-0142" },
      },
      {
        text: "NICE recommends ambulatory BP monitoring to confirm a clinic reading of 140/90 mmHg or higher.",
        citation: { doc: "NICE NG136", page: 8, section: "§1.2", chunkId: "nice-ng136-0031" },
      },
      {
        text: "Repeat measurement on a separate visit reduces white-coat misclassification.",
        citation: { doc: "CDC Hypertension Facts", page: 3, section: "§2.1", chunkId: "cdc-htn-0009" },
      },
    ],
    confidence: "high",
    chunks: [
      {
        id: "who-htn-0142",
        doc: "WHO HTN Guideline 2021",
        page: 12,
        section: "Diagnosis thresholds",
        url: "who.int/publications/hypertension-2021",
        score: 0.91,
        excerpt:
          "Hypertension is diagnosed when systolic blood pressure is ≥140 mmHg and/or diastolic blood pressure is ≥90 mmHg, measured on two different days.",
        used: true,
      },
      {
        id: "nice-ng136-0031",
        doc: "NICE NG136",
        page: 8,
        section: "Confirming diagnosis",
        url: "nice.org.uk/guidance/ng136",
        score: 0.87,
        excerpt:
          "If clinic blood pressure is 140/90 mmHg or higher, offer ambulatory blood pressure monitoring (ABPM) to confirm the diagnosis of hypertension.",
        used: true,
      },
      {
        id: "cdc-htn-0009",
        doc: "CDC Hypertension Facts",
        page: 3,
        section: "Measurement practice",
        url: "cdc.gov/bloodpressure/facts",
        score: 0.78,
        excerpt:
          "Blood pressure should be confirmed with repeat measurement at a separate visit before a diagnosis is recorded.",
        used: true,
      },
      {
        id: "who-htn-0201",
        doc: "WHO HTN Guideline 2021",
        page: 19,
        section: "Pharmacological treatment",
        url: "who.int/publications/hypertension-2021",
        score: 0.64,
        excerpt:
          "For adults with hypertension requiring pharmacological treatment, WHO recommends thiazide, ACE inhibitor, or long-acting CCB as first-line.",
        used: false,
      },
      {
        id: "cdc-htn-0044",
        doc: "CDC Hypertension Facts",
        page: 6,
        section: "Population burden",
        url: "cdc.gov/bloodpressure/facts",
        score: 0.51,
        excerpt:
          "Nearly half of adults in the United States have hypertension, defined as elevated blood pressure or taking medication for it.",
        used: false,
      },
    ],
  },
  {
    kind: "answer",
    id: "t2",
    question: "My 62-year-old patient on ramipril still reads 152/94 — what next?",
    caution:
      "This question involves patient-specific context. General guideline info below — confirm with a clinician for individual care.",
    recommendation:
      "Guidelines suggest that when a single first-line agent does not achieve target, add a second agent from a different class rather than maximising monotherapy. Adherence, measurement technique, and secondary causes should be reviewed first.",
    evidence: [
      {
        text: "WHO recommends combination therapy when BP remains above target on a single agent.",
        citation: { doc: "WHO HTN Guideline 2021", page: 22, section: "§4.3", chunkId: "who-htn-0219" },
      },
      {
        text: "NICE step 2 adds a CCB or thiazide-like diuretic to an ACE inhibitor.",
        citation: { doc: "NICE NG136", page: 21, section: "§1.4", chunkId: "nice-ng136-0088" },
      },
    ],
    confidence: "medium",
    chunks: [
      {
        id: "who-htn-0219",
        doc: "WHO HTN Guideline 2021",
        page: 22,
        section: "Combination therapy",
        url: "who.int/publications/hypertension-2021",
        score: 0.83,
        excerpt:
          "WHO suggests combination therapy, preferably as a single-pill combination, for adults whose blood pressure is not controlled on monotherapy.",
        used: true,
      },
      {
        id: "nice-ng136-0088",
        doc: "NICE NG136",
        page: 21,
        section: "Step 2 treatment",
        url: "nice.org.uk/guidance/ng136",
        score: 0.8,
        excerpt:
          "If hypertension is not controlled by an ACE inhibitor or ARB, offer the addition of a calcium-channel blocker or a thiazide-like diuretic.",
        used: true,
      },
      {
        id: "nice-ng136-0121",
        doc: "NICE NG136",
        page: 27,
        section: "Adherence review",
        url: "nice.org.uk/guidance/ng136",
        score: 0.61,
        excerpt:
          "Before escalating therapy, review adherence, measurement technique, and possible secondary causes of hypertension.",
        used: false,
      },
    ],
  },
  {
    kind: "refusal",
    id: "t3",
    question: "Patient has crushing chest pain radiating to the left arm right now — what dose do I give?",
    reason: "Emergency — seek immediate care",
    detail:
      "This describes a potential acute emergency. CliniRAG does not provide acute treatment dosing and no retrieval was performed.",
    emergencyLine: "Call emergency services immediately (112 / 911 / local equivalent).",
    chunks: [],
  },
];

export const pipelineStages = [
  { name: "Ingestion", metric: "2 PDFs · Diabetes Canada + NICE NG28" },
  { name: "Chunking", metric: "Config B · 1024 tokens · overlap 100" },
  { name: "Embeddings", metric: "BAAI/bge-small-en-v1.5 · cosine" },
  { name: "Retrieval", metric: "Dense top-k=5 · numpy index" },
  { name: "Guardrails", metric: "Query + answer safety checks" },
  { name: "Grounded LLM", metric: "Groq chat · citation-constrained" },
  { name: "Evidence Panel", metric: "Chunks with page + section_title" },
];

export const evalRows = [
  { q: "Stage 1 hypertension threshold?", expected: "who-htn-0142", retrieved: "who-htn-0142", match: true, citation: true, notes: "Rank 1" },
  { q: "When to confirm with ABPM?", expected: "nice-ng136-0031", retrieved: "nice-ng136-0031", match: true, citation: true, notes: "Rank 1" },
  { q: "First-line drug classes?", expected: "who-htn-0201", retrieved: "who-htn-0201", match: true, citation: true, notes: "Rank 2" },
  { q: "Step 2 add-on therapy?", expected: "nice-ng136-0088", retrieved: "nice-ng136-0088", match: true, citation: true, notes: "Rank 1" },
  { q: "Diabetes screening start age?", expected: "uspstf-dm-0012", retrieved: "uspstf-dm-0012", match: true, citation: true, notes: "Rank 1" },
  { q: "A1C diagnostic cut-point?", expected: "nice-ng28-0044", retrieved: "cdc-dm-0071", match: false, citation: false, notes: "Near-duplicate chunk" },
  { q: "Asthma ICS initiation step?", expected: "nice-ng80-0033", retrieved: "nice-ng80-0033", match: true, citation: true, notes: "Rank 1" },
  { q: "Pediatric asthma dosing?", expected: "—", retrieved: "—", match: true, citation: true, notes: "Correctly refused (out of scope)" },
  { q: "BP target in CKD?", expected: "who-htn-0233", retrieved: "who-htn-0219", match: false, citation: false, notes: "Adjacent section retrieved" },
  { q: "Home monitoring frequency?", expected: "cdc-htn-0009", retrieved: "cdc-htn-0009", match: true, citation: true, notes: "Rank 2" },
];

export const guardrailLog = [
  { time: "11:04:22", query: "Stage 1 hypertension threshold?", classification: "Allowed" as const },
  { time: "11:05:10", query: "My 62-year-old on ramipril reads 152/94", classification: "Needs Caution" as const },
  { time: "11:06:41", query: "Crushing chest pain right now — dose?", classification: "Refuse" as const },
  { time: "11:08:03", query: "Best antibiotic for my dog's ear infection", classification: "Refuse" as const },
  { time: "11:09:55", query: "USPSTF diabetes screening age", classification: "Allowed" as const },
  { time: "11:11:17", query: "Should I stop my own medication?", classification: "Needs Caution" as const },
];