import { i as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { _ as useNavigate, g as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as useAuth } from "./use-auth-DtWIkJr7.mjs";
import { _ as ArrowRight, h as FileText, l as Lock, o as Plus, r as ShieldCheck } from "../_libs/lucide-react.mjs";
import { n as ThemeToggle, r as cn, s as topics, t as SignOutButton } from "./ThemeToggle-Cjy0GpDb.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-CHXgz5XQ.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function Landing() {
	const [selected, setSelected] = (0, import_react.useState)(null);
	const navigate = useNavigate();
	const topic = topics.find((t) => t.id === selected);
	const { session, loading } = useAuth();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
		className: "flex min-h-screen items-center justify-center bg-background px-4 py-16",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "w-full max-w-[640px]",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-center justify-between gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-mono text-[12px] uppercase tracking-wide text-primary",
						children: "CliniRAG · Evidence-Grounded Clinical Assistant"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ThemeToggle, {}), !loading && (session ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/workspace",
							className: "rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50",
							children: "Open workspace"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SignOutButton, {})] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/auth",
							className: "rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50",
							children: "Sign in"
						}))]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "mt-3 text-[36px] font-semibold leading-tight text-foreground",
					children: "Ask questions grounded in official guidelines."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 text-[16px] text-muted-foreground",
					children: "Every answer is cited to WHO, CDC, NICE, or USPSTF source text. No private data. No unsupported claims."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-8 rounded-xl border border-border bg-card p-5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "font-mono text-[12px] uppercase tracking-wide text-muted-foreground",
							children: "Select clinical scope"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-3 grid gap-3 sm:grid-cols-2",
							children: [topics.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
								type: "button",
								onClick: () => setSelected(t.id),
								className: cn("rounded-xl border border-border p-4 text-left transition-colors duration-150 hover:border-primary/50", selected === t.id && "border-primary bg-secondary"),
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "block text-[16px] font-semibold text-foreground",
									children: t.title
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "mt-1 block text-[14px] text-muted-foreground",
									children: t.blurb
								})]
							}, t.id)), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-2 rounded-xl border border-dashed border-border p-4 text-[14px] text-muted-foreground",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, {
										className: "size-4",
										strokeWidth: 1.5
									}),
									"Add topic",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-mono text-[12px]",
										children: "(roadmap)"
									})
								]
							})]
						}),
						topic && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-4 border-t border-border pt-4",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "font-mono text-[12px] uppercase tracking-wide text-muted-foreground",
								children: "Ingested sources for this scope"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-2 flex flex-wrap gap-2",
								children: topic.sources.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "inline-flex items-center gap-1.5 rounded-md border border-border bg-background px-2 py-1 font-mono text-[12px] text-foreground",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FileText, {
										className: "size-3",
										strokeWidth: 1.5
									}), s]
								}, s))
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
							type: "button",
							disabled: !topic,
							onClick: () => session ? navigate({
								to: "/workspace",
								search: { topic: topic.id }
							}) : navigate({
								to: "/auth",
								search: { redirect: `/workspace?topic=${topic.id}` }
							}),
							className: "mt-5 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-[15px] font-medium text-primary-foreground transition-colors duration-150 hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-40",
							children: [session ? "Start session" : "Sign in to start session", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowRight, {
								className: "size-4",
								strokeWidth: 1.5
							})]
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "mt-5 flex items-center gap-2 text-[12px] text-muted-foreground",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, {
						className: "size-3.5",
						strokeWidth: 1.5
					}), "Fluent answer ≠ safe answer. CliniRAG will visibly refuse out-of-scope or unsupported questions."]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "mt-2 flex items-center gap-2 text-[12px] text-muted-foreground",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, {
						className: "size-3.5",
						strokeWidth: 1.5
					}), "Clinicians cannot upload files. Only administrators curate the guideline corpus."]
				})
			]
		})
	});
}
//#endregion
export { Landing as component };
