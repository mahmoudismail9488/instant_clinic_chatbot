/** Client for the GlucoRAG FastAPI backend (Day 3 grounded pipeline). */

import type {
  AnswerTurn,
  Confidence,
  EvidenceChunk,
  RefusalTurn,
  Turn,
} from "@/lib/clinirag-data";

const DEFAULT_API = "http://localhost:8000";

export function apiBaseUrl(): string {
  return (import.meta.env["VITE_API_URL"] as string | undefined)?.replace(/\/$/, "") || DEFAULT_API;
}

type ApiChunk = {
  id: string;
  doc: string;
  page?: number | null;
  section?: string;
  section_number?: string | null;
  section_title?: string | null;
  score: number;
  excerpt: string;
  used?: boolean;
};

type ApiResponse = {
  kind: "answer" | "refusal" | string;
  id: string;
  question: string;
  recommendation?: string;
  detail?: string;
  reason?: string | null;
  caution?: string | null;
  confidence?: string;
  confidence_score?: number | null;
  evidence?: {
    text: string;
    citation: { doc: string; page: number; section: string; chunkId: string };
  }[];
  chunks?: ApiChunk[];
  blocked?: boolean;
  status?: string;
  safety_note?: string | null;
  missing_information?: string[];
  guardrail?: { allowed?: boolean; passed?: boolean; reason?: string | null } | null;
  next_action?: string | null;
  risk?: { category?: string; level?: string; action?: string; reason?: string } | null;
};

function mapChunks(chunks: ApiChunk[] | undefined): EvidenceChunk[] {
  return (chunks ?? []).map((c) => ({
    id: c.id,
    doc: c.doc,
    page: c.page ?? 0,
    section: c.section || c.section_title || c.section_number || "—",
    url: "",
    score: c.score,
    excerpt: c.excerpt,
    used: c.used ?? true,
  }));
}

function mapConfidence(value: string | undefined): Confidence {
  const v = (value || "").toLowerCase();
  if (v === "high") return "high";
  if (v === "medium") return "medium";
  if (v === "low") return "low";
  if (v.includes("insufficient")) return "insufficient";
  return "medium";
}

function mapRefusalReason(reason: string | null | undefined): RefusalTurn["reason"] {
  if (reason === "Emergency — seek immediate care") return reason;
  if (reason === "Insufficient retrieval confidence") return reason;
  if (reason === "Patient-specific — seek clinical care") return reason;
  if (reason === "Medication request — consult a clinician") return reason;
  const lower = (reason || "").toLowerCase();
  if (lower.includes("patient")) return "Patient-specific — seek clinical care";
  if (lower.includes("medication") || lower.includes("prescrib") || lower.includes("dosage")) {
    return "Medication request — consult a clinician";
  }
  return "Out of scope";
}

export function mapApiToTurn(data: ApiResponse): Turn {
  const chunks = mapChunks(data.chunks);
  if (data.kind === "refusal" || data.blocked) {
    const detailParts = [
      data.detail || data.recommendation || "Request could not be answered from guidelines.",
    ];
    if (data.missing_information?.length) {
      detailParts.push(data.missing_information.map((g) => `• ${g}`).join("\n"));
    }
    if (data.safety_note) detailParts.push(data.safety_note);

    const refusal: RefusalTurn = {
      kind: "refusal",
      id: data.id,
      question: data.question,
      reason: mapRefusalReason(data.reason),
      detail: detailParts.join("\n\n"),
      chunks,
      confidence: mapConfidence(data.confidence),
      confidenceScore:
        typeof data.confidence_score === "number" ? data.confidence_score : 0,
    };
    if (data.reason === "Emergency — seek immediate care") {
      refusal.emergencyLine =
        "Call emergency services immediately (112 / 911 / local equivalent).";
    }
    if (data.status) refusal.status = data.status;
    if (data.next_action) refusal.nextAction = data.next_action;
    return refusal;
  }

  const answer: AnswerTurn = {
    kind: "answer",
    id: data.id,
    question: data.question,
    recommendation: data.recommendation || "",
    evidence: (data.evidence ?? []).map((e) => ({
      text: e.text,
      citation: {
        doc: e.citation.doc,
        page: e.citation.page,
        section: e.citation.section,
        chunkId: e.citation.chunkId,
      },
    })),
    confidence: mapConfidence(data.confidence),
    chunks,
    nextAction: data.next_action ?? "Consult a clinician to apply this to an individual patient.",
  };
  const caution = data.caution ?? data.safety_note;
  if (caution) answer.caution = caution;
  if (typeof data.confidence_score === "number") {
    answer.confidenceScore = data.confidence_score;
  }
  if (data.status) answer.status = data.status;
  return answer;
}

export async function queryGuidelines(
  query: string,
  opts?: {
    topic?: string;
    topK?: number;
    sectionFocus?: string;
    signal?: AbortSignal;
  },
): Promise<Turn> {
  const init: RequestInit = {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      query,
      topic: opts?.topic,
      top_k: opts?.topK,
      section_focus: opts?.sectionFocus && opts.sectionFocus !== "any" ? opts.sectionFocus : undefined,
    }),
  };
  if (opts?.signal) init.signal = opts.signal;

  const res = await fetch(`${apiBaseUrl()}/query`, init);

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = (await res.json()) as { detail?: string };
      if (err.detail) detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail || `API error ${res.status}`);
  }

  const data = (await res.json()) as ApiResponse;
  return mapApiToTurn(data);
}

export async function checkApiHealth(): Promise<{
  status: string;
  index_size: number;
  pipeline?: string;
}> {
  const res = await fetch(`${apiBaseUrl()}/health`);
  if (!res.ok) throw new Error(`Health check failed (${res.status})`);
  return res.json() as Promise<{ status: string; index_size: number; pipeline?: string }>;
}
