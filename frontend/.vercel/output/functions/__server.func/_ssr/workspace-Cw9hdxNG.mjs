import { i as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { g as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as Route } from "./router-cVTBtxXh.mjs";
import { a as SendHorizontal, d as Link2, f as LayoutDashboard, g as ChevronDown, h as FileText, i as ShieldAlert, p as Hash, r as ShieldCheck, t as TriangleAlert, u as LoaderCircle } from "../_libs/lucide-react.mjs";
import { n as ThemeToggle, o as pipelineStages, r as cn, s as topics, t as SignOutButton } from "./ThemeToggle-Cjy0GpDb.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/workspace-Cw9hdxNG.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var confidenceMap = {
	high: {
		label: "High",
		color: "text-confidence-high border-confidence-high/30 bg-confidence-high/8",
		hint: "Mean retrieval similarity 0.85 · 3/3 claims cited"
	},
	medium: {
		label: "Medium",
		color: "text-confidence-medium border-confidence-medium/30 bg-confidence-medium/8",
		hint: "Mean retrieval similarity 0.74 · 2/2 claims cited"
	},
	low: {
		label: "Low",
		color: "text-confidence-low border-confidence-low/30 bg-confidence-low/8",
		hint: "Mean retrieval similarity below 0.60"
	},
	insufficient: {
		label: "Insufficient Evidence",
		color: "text-confidence-insufficient border-confidence-insufficient/30 bg-confidence-insufficient/8",
		hint: "No chunk cleared the grounding threshold — refusal is the correct output"
	}
};
function ConfidenceBadge({ level }) {
	const c = confidenceMap[level];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
		title: c.hint,
		className: cn("inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[12px] leading-5", c.color),
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-1.5 rounded-full bg-current" }), c.label]
	});
}
function CitationChip({ citation, onSelect, active }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
		type: "button",
		onClick: () => onSelect?.(citation.chunkId),
		className: cn("ml-1 inline-flex items-center gap-1 rounded-md border border-evidence/35 bg-evidence-soft px-1.5 py-0.5 font-mono text-[12px] text-evidence transition-colors duration-150 hover:border-evidence hover:bg-evidence/12", active && "ring-2 ring-evidence/40"),
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link2, {
				className: "size-3",
				strokeWidth: 1.5
			}),
			citation.doc,
			" · p.",
			citation.page,
			" · ",
			citation.section
		]
	});
}
function SourceLine({ doc, page }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex items-center gap-1.5 text-[14px] font-semibold text-foreground",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FileText, {
				className: "size-4 text-muted-foreground",
				strokeWidth: 1.5
			}),
			doc,
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: "font-mono text-[12px] font-normal text-muted-foreground",
				children: ["p.", page]
			})
		]
	});
}
function MetaRow({ chunkId, section, url }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[12px] text-muted-foreground",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: "inline-flex items-center gap-1",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Hash, {
					className: "size-3",
					strokeWidth: 1.5
				}), chunkId]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "·" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: section }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "·" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "truncate",
				children: url
			})
		]
	});
}
function GuardrailIndicator() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
		className: "inline-flex items-center gap-1.5 rounded-md border border-confidence-high/30 bg-confidence-high/8 px-2 py-1 font-mono text-[12px] text-confidence-high",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, {
			className: "size-3.5",
			strokeWidth: 1.5
		}), "Guardrail: Active"]
	});
}
function Card({ className, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: cn("rounded-xl border border-border bg-card transition-shadow duration-150 hover:shadow-sm", className),
		children
	});
}
function UserMessage({ text }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex justify-end",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "max-w-[80%] rounded-xl bg-secondary px-3.5 py-2 text-[15px] text-foreground",
			children: text
		})
	});
}
function AnswerCard({ turn, onCitation, activeChunk }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
		className: turn.caution ? "border-t-2 border-t-safety-caution" : void 0,
		children: [
			turn.caution && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-start gap-2 rounded-t-xl bg-safety-caution-bg px-4 py-2.5 text-[13px] text-safety-caution",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, {
					className: "mt-0.5 size-4 shrink-0",
					strokeWidth: 1.5
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: turn.caution })]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center justify-between gap-3 px-4 pt-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
						className: "font-mono text-[12px] uppercase tracking-wide text-muted-foreground",
						children: "Recommendation"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "font-mono text-[11px] text-muted-foreground",
						children: [
							"Status: ",
							turn.status ?? "answered",
							" · Evidence quality: ",
							turn.confidence
						]
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ConfidenceBadge, { level: turn.confidence })]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "whitespace-pre-wrap px-4 pt-2 text-[15px] leading-[1.6] text-foreground",
				children: turn.recommendation
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
				className: "px-4 pt-5 font-mono text-[12px] uppercase tracking-wide text-muted-foreground",
				children: "Supporting evidence"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "space-y-2.5 px-4 pt-2",
				children: turn.evidence.map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "text-[15px] leading-[1.6] text-foreground",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "mr-2 text-muted-foreground",
							children: "—"
						}),
						e.text,
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CitationChip, {
							citation: e.citation,
							onSelect: onCitation,
							active: activeChunk === e.citation.chunkId
						})
					]
				}, e.citation.chunkId))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-5 space-y-1 rounded-b-xl border-t border-border px-4 py-2.5 text-[12px] text-muted-foreground",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "This supports — not replaces — clinical judgment." }), turn.nextAction && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "text-foreground/80",
					children: ["Suggested next action: ", turn.nextAction]
				})]
			})
		]
	});
}
function RefusalCard({ turn }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
		className: "bg-safety-refuse-bg",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-start gap-3 p-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldAlert, {
				className: "mt-0.5 size-6 shrink-0 text-confidence-insufficient",
				strokeWidth: 1.5
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "space-y-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
						className: "text-[16px] font-semibold text-foreground",
						children: "I can't answer this safely within scope."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-wrap gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "inline-block rounded-md border border-border bg-card px-2 py-0.5 font-mono text-[12px] text-confidence-insufficient",
							children: turn.reason
						}), turn.status && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "inline-block rounded-md border border-border bg-card px-2 py-0.5 font-mono text-[12px] text-muted-foreground",
							children: ["status: ", turn.status]
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-[14px] text-muted-foreground",
						children: turn.detail
					}),
					turn.emergencyLine && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-[15px] font-semibold text-foreground",
						children: turn.emergencyLine
					}),
					turn.nextAction && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "text-[13px] text-foreground/80",
						children: ["Suggested next action: ", turn.nextAction]
					})
				]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "border-t border-border px-4 py-2.5 text-[12px] text-muted-foreground",
			children: "This supports — not replaces — clinical judgment."
		})]
	});
}
function ChunkCard({ chunk, active }) {
	const [open, setOpen] = (0, import_react.useState)(false);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		id: `chunk-${chunk.id}`,
		className: cn("rounded-xl border border-l-4 border-border bg-card p-3.5 transition-shadow duration-150", chunk.used ? "border-l-evidence" : "border-l-border", active && "shadow-sm ring-2 ring-evidence/40"),
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SourceLine, {
				doc: chunk.doc,
				page: chunk.page
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-2 flex items-center gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "h-1.5 flex-1 overflow-hidden rounded-full bg-muted",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: cn("h-full rounded-full", chunk.used ? "bg-evidence" : "bg-muted-foreground/50"),
						style: { width: `${chunk.score * 100}%` }
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "font-mono text-[12px] text-muted-foreground",
					children: chunk.score.toFixed(2)
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: cn("mt-2 text-[14px] leading-[1.6] text-foreground", !open && "line-clamp-3"),
				children: chunk.excerpt
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: () => setOpen((v) => !v),
				className: "mt-1 font-mono text-[12px] text-primary hover:text-primary-hover",
				children: open ? "collapse chunk" : "show full chunk"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-2 border-t border-border pt-2",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetaRow, {
					chunkId: chunk.id,
					section: chunk.section,
					url: chunk.url
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 font-mono text-[12px] text-muted-foreground",
				children: chunk.used ? "cited in answer" : "retrieved · not cited"
			})
		]
	});
}
function EvidencePanel({ chunks, activeChunk, judgeMode }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex h-full flex-col",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "border-b border-border px-4 py-3",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h2", {
					className: "text-[14px] font-semibold text-foreground",
					children: [
						"Evidence used for this answer",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-[12px] font-normal text-muted-foreground",
							children: "(Top-K = 5)"
						})
					]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex-1 space-y-3 overflow-y-auto p-4",
				children: chunks.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "rounded-xl border border-dashed border-border p-4 text-[14px] text-muted-foreground",
					children: "No retrieval performed — query fell outside guideline scope."
				}) : chunks.map((c) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChunkCard, {
					chunk: c,
					active: activeChunk === c.id
				}, c.id))
			}),
			judgeMode && chunks.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "border-t border-border px-4 py-2.5 font-mono text-[12px] text-muted-foreground",
				children: ["Precision@5 for this query: ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-confidence-high",
					children: "0.80"
				})]
			})
		]
	});
}
var DEFAULT_API = "http://localhost:8000";
function apiBaseUrl() {
	return {
		"BASE_URL": "/",
		"DEV": false,
		"MODE": "production",
		"PROD": true,
		"SSR": true,
		"TSS_DEV_SERVER": "false",
		"TSS_DEV_SSR_STYLES_BASEPATH": "/",
		"TSS_DEV_SSR_STYLES_ENABLED": "true",
		"TSS_DISABLE_CSRF_MIDDLEWARE_WARNING": "false",
		"TSS_INLINE_CSS_ENABLED": "false",
		"TSS_ROUTER_BASEPATH": "",
		"TSS_SERVER_FN_BASE": "/_serverFn/",
		"VITE_API_URL": "http://localhost:8000",
		"VITE_SUPABASE_PROJECT_ID": "bbwycwrnmzmyakhbzqtd",
		"VITE_SUPABASE_PUBLISHABLE_KEY": "sb_publishable_EdzwjL-1y0AgfoDnM4Gk1Q_zZjDba42",
		"VITE_SUPABASE_URL": "https://bbwycwrnmzmyakhbzqtd.supabase.co"
	}["VITE_API_URL"]?.replace(/\/$/, "") || DEFAULT_API;
}
function mapChunks(chunks) {
	return (chunks ?? []).map((c) => ({
		id: c.id,
		doc: c.doc,
		page: c.page ?? 0,
		section: c.section || c.section_title || c.section_number || "—",
		url: "",
		score: c.score,
		excerpt: c.excerpt,
		used: c.used ?? true
	}));
}
function mapConfidence(value) {
	const v = (value || "").toLowerCase();
	if (v === "high") return "high";
	if (v === "medium") return "medium";
	if (v === "low") return "low";
	if (v.includes("insufficient")) return "insufficient";
	return "medium";
}
function mapRefusalReason(reason) {
	if (reason === "Emergency — seek immediate care") return reason;
	if (reason === "Insufficient retrieval confidence") return reason;
	if (reason === "Patient-specific — seek clinical care") return reason;
	if (reason === "Medication request — consult a clinician") return reason;
	const lower = (reason || "").toLowerCase();
	if (lower.includes("patient")) return "Patient-specific — seek clinical care";
	if (lower.includes("medication") || lower.includes("prescrib") || lower.includes("dosage")) return "Medication request — consult a clinician";
	return "Out of scope";
}
function mapApiToTurn(data) {
	const chunks = mapChunks(data.chunks);
	if (data.kind === "refusal" || data.blocked) {
		const detailParts = [data.detail || data.recommendation || "Request could not be answered from guidelines."];
		if (data.missing_information?.length) detailParts.push(data.missing_information.map((g) => `• ${g}`).join("\n"));
		if (data.safety_note) detailParts.push(data.safety_note);
		return {
			kind: "refusal",
			id: data.id,
			question: data.question,
			reason: mapRefusalReason(data.reason),
			detail: detailParts.join("\n\n"),
			emergencyLine: data.reason === "Emergency — seek immediate care" ? "Call emergency services immediately (112 / 911 / local equivalent)." : void 0,
			chunks,
			status: data.status,
			nextAction: data.next_action ?? void 0
		};
	}
	return {
		kind: "answer",
		id: data.id,
		question: data.question,
		caution: data.caution ?? data.safety_note ?? void 0,
		recommendation: data.recommendation || "",
		evidence: (data.evidence ?? []).map((e) => ({
			text: e.text,
			citation: {
				doc: e.citation.doc,
				page: e.citation.page,
				section: e.citation.section,
				chunkId: e.citation.chunkId
			}
		})),
		confidence: mapConfidence(data.confidence),
		chunks,
		status: data.status,
		nextAction: data.next_action ?? "Consult a clinician to apply this to an individual patient."
	};
}
async function queryGuidelines(query, opts) {
	const res = await fetch(`${apiBaseUrl()}/query`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json"
		},
		body: JSON.stringify({
			query,
			topic: opts?.topic,
			top_k: opts?.topK
		}),
		signal: opts?.signal
	});
	if (!res.ok) {
		let detail = res.statusText;
		try {
			const err = await res.json();
			if (err.detail) detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
		} catch {}
		throw new Error(detail || `API error ${res.status}`);
	}
	return mapApiToTurn(await res.json());
}
function Workspace() {
	const { topic } = Route.useSearch();
	const scope = topics.find((t) => t.id === topic) ?? topics.find((t) => t.id === "diabetes") ?? topics[0];
	const [turns, setTurns] = (0, import_react.useState)([]);
	const [activeChunk, setActiveChunk] = (0, import_react.useState)(null);
	const [pipelineOpen, setPipelineOpen] = (0, import_react.useState)(true);
	const [draft, setDraft] = (0, import_react.useState)("");
	const [mobileTab, setMobileTab] = (0, import_react.useState)("chat");
	const [loading, setLoading] = (0, import_react.useState)(false);
	const [error, setError] = (0, import_react.useState)(null);
	const abortRef = (0, import_react.useRef)(null);
	const listRef = (0, import_react.useRef)(null);
	const current = turns[turns.length - 1];
	(0, import_react.useEffect)(() => {
		listRef.current?.scrollTo({
			top: listRef.current.scrollHeight,
			behavior: "smooth"
		});
	}, [turns, loading]);
	function onCitation(chunkId) {
		setActiveChunk(chunkId);
		setMobileTab("evidence");
		requestAnimationFrame(() => {
			document.getElementById(`chunk-${chunkId}`)?.scrollIntoView({
				behavior: "smooth",
				block: "center"
			});
		});
	}
	async function send() {
		const question = draft.trim();
		if (!question || loading) return;
		setDraft("");
		setError(null);
		setActiveChunk(null);
		setLoading(true);
		abortRef.current?.abort();
		const ac = new AbortController();
		abortRef.current = ac;
		try {
			const turn = await queryGuidelines(question, {
				topic: scope.id,
				signal: ac.signal
			});
			setTurns((prev) => [...prev, turn]);
			if (turn.chunks[0]) setActiveChunk(turn.chunks[0].id);
		} catch (err) {
			if (err.name === "AbortError") return;
			const message = err instanceof Error ? err.message : "Request failed";
			setError(message.includes("Failed to fetch") ? `Cannot reach API at ${apiBaseUrl()}. Start it with: uv run clinic-api` : message);
		} finally {
			setLoading(false);
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex h-screen flex-col bg-background",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "flex flex-wrap items-center justify-between gap-3 border-b border-border bg-card px-4 py-2.5",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center gap-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-[12px] uppercase tracking-wide text-primary",
							children: "CliniRAG"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "rounded-md border border-border bg-secondary px-2 py-0.5 text-[13px] text-foreground",
							children: scope.title
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/",
							className: "text-[13px] text-primary hover:text-primary-hover",
							children: "change topic"
						})
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center gap-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
							to: "/dashboard",
							className: "inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LayoutDashboard, {
								className: "size-3.5",
								strokeWidth: 1.5
							}), "Judge view"]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ThemeToggle, {}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SignOutButton, {})
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "border-b border-border bg-card px-4 pb-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
					type: "button",
					onClick: () => setPipelineOpen((v) => !v),
					className: "flex items-center gap-1 font-mono text-[12px] text-muted-foreground",
					children: ["Pipeline status", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: cn("size-3.5 transition-transform", !pipelineOpen && "-rotate-90") })]
				}), pipelineOpen && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap gap-x-3 gap-y-1 pt-1 font-mono text-[12px] text-muted-foreground",
					children: [pipelineStages.slice(0, 4).map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [
						s.name,
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-confidence-high",
							children: "✓"
						})
					] }, s.name)), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "text-muted-foreground/80",
						children: ["API ", apiBaseUrl()]
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex border-b border-border bg-card md:hidden",
				children: ["chat", "evidence"].map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: () => setMobileTab(t),
					className: cn("flex-1 py-2 text-[13px] capitalize", mobileTab === t ? "border-b-2 border-primary text-primary" : "text-muted-foreground"),
					children: t
				}, t))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex min-h-0 flex-1",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: cn("min-h-0 flex-1 flex-col md:flex md:basis-[65%]", mobileTab === "chat" ? "flex" : "hidden"),
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						ref: listRef,
						className: "flex-1 space-y-5 overflow-y-auto p-4",
						children: [
							turns.length === 0 && !loading && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "rounded-lg border border-dashed border-border bg-card px-4 py-6 text-center text-[14px] text-muted-foreground",
								children: "Ask a guideline question grounded in the indexed corpus (Diabetes Canada CPG + NICE NG28). Example: “Who should be screened for type 2 diabetes?” — medication or “do I have…” questions are refused."
							}),
							turns.map((turn) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "space-y-3",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UserMessage, { text: turn.question }), turn.kind === "answer" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnswerCard, {
									turn,
									onCitation,
									activeChunk
								}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefusalCard, { turn })]
							}, turn.id)),
							loading && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-2 text-[14px] text-muted-foreground",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "size-4 animate-spin" }), "Retrieving guidelines and generating a grounded answer…"]
							}),
							error && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "rounded-lg border border-destructive/40 bg-destructive/5 px-3 py-2 text-[13px] text-destructive",
								children: error
							})
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "border-t border-border bg-card p-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								value: draft,
								onChange: (e) => setDraft(e.target.value),
								onKeyDown: (e) => e.key === "Enter" && void send(),
								placeholder: "Ask a guideline question…",
								disabled: loading,
								className: "h-10 flex-1 rounded-lg border border-border bg-background px-3 text-[15px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary disabled:opacity-60"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
								type: "button",
								onClick: () => void send(),
								disabled: loading || !draft.trim(),
								className: "inline-flex h-10 items-center gap-1.5 rounded-lg bg-primary px-3.5 text-[14px] font-medium text-primary-foreground transition-colors duration-150 hover:bg-primary-hover disabled:opacity-40",
								children: [loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, {
									className: "size-4 animate-spin",
									strokeWidth: 1.5
								}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SendHorizontal, {
									className: "size-4",
									strokeWidth: 1.5
								}), "Send"]
							})]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-2 flex items-center justify-between",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GuardrailIndicator, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "font-mono text-[12px] text-muted-foreground",
								children: ["Live RAG · ", scope.title]
							})]
						})]
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("aside", {
					className: cn("min-h-0 border-l border-border bg-background md:block md:basis-[35%]", mobileTab === "evidence" ? "block flex-1" : "hidden"),
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EvidencePanel, {
						chunks: current?.chunks ?? [],
						activeChunk,
						judgeMode: true
					})
				})]
			})
		]
	});
}
//#endregion
export { Workspace as component };
