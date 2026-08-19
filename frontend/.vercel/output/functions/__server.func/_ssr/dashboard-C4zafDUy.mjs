import { i as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { g as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as supabase } from "./client-DeHMspjV.mjs";
import { n as useIsAdmin, t as useAuth } from "./use-auth-DtWIkJr7.mjs";
import { l as Lock, m as FileUp, u as LoaderCircle, v as ArrowLeft } from "../_libs/lucide-react.mjs";
import { a as guardrailLog, i as evalRows, n as ThemeToggle, o as pipelineStages, r as cn, t as SignOutButton } from "./ThemeToggle-Cjy0GpDb.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/dashboard-C4zafDUy.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function AdminDocuments({ userId }) {
	const { isAdmin, checking } = useIsAdmin(userId);
	const [docs, setDocs] = (0, import_react.useState)([]);
	const [title, setTitle] = (0, import_react.useState)("");
	const [org, setOrg] = (0, import_react.useState)("");
	const [file, setFile] = (0, import_react.useState)(null);
	const [busy, setBusy] = (0, import_react.useState)(false);
	const [error, setError] = (0, import_react.useState)(null);
	const load = (0, import_react.useCallback)(async () => {
		const { data } = await supabase.from("guideline_documents").select("id, title, source_org, topic, created_at").order("created_at", { ascending: false });
		setDocs(data ?? []);
	}, []);
	(0, import_react.useEffect)(() => {
		load();
	}, [load]);
	async function upload(e) {
		e.preventDefault();
		if (!file || !userId) return;
		setBusy(true);
		setError(null);
		const path = `${userId}/${Date.now()}-${file.name}`;
		const { error: storageError } = await supabase.storage.from("guidelines").upload(path, file);
		if (storageError) {
			setError(storageError.message);
			setBusy(false);
			return;
		}
		const { error: rowError } = await supabase.from("guideline_documents").insert({
			title,
			source_org: org,
			storage_path: path,
			uploaded_by: userId
		});
		if (rowError) setError(rowError.message);
		else {
			setTitle("");
			setOrg("");
			setFile(null);
			await load();
		}
		setBusy(false);
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "rounded-xl border border-border bg-card",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
			className: "border-b border-border px-4 py-3 text-[14px] font-semibold text-foreground",
			children: "Guideline corpus · source documents"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "p-4",
			children: [
				checking ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "font-mono text-[12px] text-muted-foreground",
					children: "Checking permissions…"
				}) : isAdmin ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
					onSubmit: upload,
					className: "grid gap-3 sm:grid-cols-[1fr_1fr_auto]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							required: true,
							value: title,
							onChange: (e) => setTitle(e.target.value),
							placeholder: "Document title",
							className: "h-10 rounded-lg border border-border bg-background px-3 text-[14px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							required: true,
							value: org,
							onChange: (e) => setOrg(e.target.value),
							placeholder: "Source org (WHO, CDC, NICE…)",
							className: "h-10 rounded-lg border border-border bg-background px-3 text-[14px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								required: true,
								type: "file",
								accept: ".pdf,.txt,.md",
								onChange: (e) => setFile(e.target.files?.[0] ?? null),
								className: "max-w-[220px] text-[13px] text-muted-foreground"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
								type: "submit",
								disabled: busy,
								className: "inline-flex h-10 items-center gap-1.5 rounded-lg bg-primary px-3.5 text-[14px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50",
								children: [busy ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, {
									className: "size-4 animate-spin",
									strokeWidth: 1.5
								}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(FileUp, {
									className: "size-4",
									strokeWidth: 1.5
								}), "Upload"]
							})]
						})
					]
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2 text-[13px] text-muted-foreground",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, {
						className: "size-3.5",
						strokeWidth: 1.5
					}), "Uploading guideline documents is restricted to administrators."]
				}),
				error && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 rounded-lg border border-confidence-insufficient/30 bg-safety-refuse-bg px-3 py-2 text-[13px] text-confidence-insufficient",
					children: error
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ul", {
					className: "mt-4 space-y-2",
					children: [docs.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
						className: "font-mono text-[12px] text-muted-foreground",
						children: "No documents ingested yet."
					}), docs.map((d) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
						className: "flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-[13px]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-foreground",
							children: d.title
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-[12px] text-muted-foreground",
							children: d.source_org
						})]
					}, d.id))]
				})
			]
		})]
	});
}
var stats = [
	{
		label: "Retrieval Precision@5",
		value: "0.82",
		sub: "+0.06 vs baseline",
		spark: [
			58,
			62,
			66,
			71,
			74,
			79,
			82
		]
	},
	{
		label: "Citation Accuracy",
		value: "94%",
		sub: "47 of 50 citations verified",
		spark: [
			80,
			84,
			86,
			88,
			90,
			92,
			94
		]
	},
	{
		label: "Unsupported Claim Rate",
		value: "3.1%",
		sub: "lower is better",
		spark: [
			12,
			10,
			9,
			7,
			6,
			4,
			3
		]
	}
];
function Sparkline({ points }) {
	const max = Math.max(...points);
	const d = points.map((p, i) => `${i / (points.length - 1) * 100},${30 - p / max * 28}`).join(" ");
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("svg", {
		viewBox: "0 0 100 30",
		preserveAspectRatio: "none",
		className: "mt-3 h-8 w-full",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("polyline", {
			points: d,
			fill: "none",
			stroke: "var(--color-primary)",
			strokeWidth: "1.5",
			vectorEffect: "non-scaling-stroke"
		})
	});
}
function Dashboard() {
	const [stage, setStage] = (0, import_react.useState)(0);
	const { user } = useAuth();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "min-h-screen bg-background",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "flex items-center justify-between border-b border-border bg-card px-4 py-2.5",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "font-mono text-[12px] uppercase tracking-wide text-primary",
					children: "CliniRAG"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-[14px] font-semibold text-foreground",
					children: "Judge view"
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
						to: "/workspace",
						className: "inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, {
							className: "size-3.5",
							strokeWidth: 1.5
						}), "Back to workspace"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ThemeToggle, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SignOutButton, {})
				]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mx-auto max-w-6xl space-y-6 p-4 md:p-6",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AdminDocuments, { userId: user?.id }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
					className: "grid gap-4 md:grid-cols-3",
					children: stats.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "rounded-xl border border-border bg-card p-4",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "font-mono text-[12px] uppercase tracking-wide text-muted-foreground",
								children: s.label
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1 font-mono text-[36px] leading-tight text-foreground",
								children: s.value
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-[13px] text-muted-foreground",
								children: s.sub
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkline, { points: s.spark })
						]
					}, s.label))
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "rounded-xl border border-border bg-card p-4",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "text-[14px] font-semibold text-foreground",
							children: "Pipeline architecture"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-3 flex flex-wrap items-center gap-2",
							children: pipelineStages.map((s, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
									type: "button",
									onClick: () => setStage(i),
									className: cn("rounded-lg border border-border px-2.5 py-1.5 text-[13px] transition-colors duration-150", stage === i ? "border-primary bg-secondary text-primary" : "text-foreground hover:border-primary/50"),
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "mr-1.5 font-mono text-[12px] text-muted-foreground",
										children: i + 1
									}), s.name]
								}), i < pipelineStages.length - 1 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-muted-foreground",
									children: "→"
								})]
							}, s.name))
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-3 rounded-lg bg-secondary px-3 py-2 font-mono text-[12px] text-foreground",
							children: [
								pipelineStages[stage].name,
								": ",
								pipelineStages[stage].metric
							]
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "rounded-xl border border-border bg-card",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "border-b border-border px-4 py-3 text-[14px] font-semibold text-foreground",
						children: "Evaluation set · 10 of 20 labeled questions"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "overflow-x-auto",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
							className: "w-full text-left text-[13px]",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
								className: "font-mono text-[12px] uppercase text-muted-foreground",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
									className: "border-b border-border",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
											className: "px-4 py-2 font-normal",
											children: "Question"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
											className: "px-4 py-2 font-normal",
											children: "Expected chunk"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
											className: "px-4 py-2 font-normal",
											children: "Retrieved@5"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
											className: "px-4 py-2 font-normal",
											children: "Match"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
											className: "px-4 py-2 font-normal",
											children: "Citation"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
											className: "px-4 py-2 font-normal",
											children: "Notes"
										})
									]
								})
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: evalRows.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
								className: "border-b border-border last:border-0",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: "px-4 py-2 text-foreground",
										children: r.q
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: "px-4 py-2 font-mono text-[12px] text-muted-foreground",
										children: r.expected
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: "px-4 py-2 font-mono text-[12px] text-muted-foreground",
										children: r.retrieved
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: cn("px-4 py-2 font-mono", r.match ? "text-confidence-high" : "text-confidence-low"),
										children: r.match ? "✓" : "✗"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: cn("px-4 py-2 font-mono", r.citation ? "text-confidence-high" : "text-confidence-low"),
										children: r.citation ? "✓" : "✗"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
										className: "px-4 py-2 text-muted-foreground",
										children: r.notes
									})
								]
							}, r.q)) })]
						})
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "rounded-xl border border-border bg-card",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "border-b border-border px-4 py-3 text-[14px] font-semibold text-foreground",
						children: "Guardrail log · last 6 queries"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("table", {
						className: "w-full text-left text-[13px]",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: guardrailLog.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
							className: "border-b border-border last:border-0",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-4 py-2 font-mono text-[12px] text-muted-foreground",
									children: g.time
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-4 py-2 text-foreground",
									children: g.query
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "px-4 py-2 text-right",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: cn("rounded-md border px-2 py-0.5 font-mono text-[12px]", g.classification === "Allowed" && "border-confidence-high/30 bg-confidence-high/8 text-confidence-high", g.classification === "Needs Caution" && "border-safety-caution/30 bg-safety-caution-bg text-safety-caution", g.classification === "Refuse" && "border-confidence-insufficient/30 bg-safety-refuse-bg text-confidence-insufficient"),
										children: g.classification
									})
								})
							]
						}, g.time)) })
					})]
				})
			]
		})]
	});
}
//#endregion
export { Dashboard as component };
