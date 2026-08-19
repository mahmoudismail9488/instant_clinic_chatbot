import { i as __toESM } from "../_runtime.mjs";
import { i as require_react, n as useQueryClient, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { _ as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as supabase } from "./client-DeHMspjV.mjs";
import { c as LogOut, n as Sun, s as Moon } from "../_libs/lucide-react.mjs";
import { t as clsx } from "../_libs/clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/ThemeToggle-Cjy0GpDb.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
var topics = [
	{
		id: "diabetes",
		title: "Diabetes Screening",
		blurb: "Screening age, risk factors, A1C and FPG cut-points (Diabetes Canada + NICE NG28).",
		sources: ["Diabetes-Canada-2024-CPG-Quick-Reference-Guide.pdf", "NICE-NG28-Type2-Diabetes-Adults-Recommendations.pdf"]
	},
	{
		id: "hypertension",
		title: "Adult Hypertension",
		blurb: "Diagnosis thresholds, first-line therapy, monitoring intervals.",
		sources: [
			"WHO HTN Guideline 2021",
			"CDC Hypertension Facts",
			"NICE NG136"
		]
	},
	{
		id: "asthma",
		title: "Asthma Guidance",
		blurb: "Stepwise control, inhaled corticosteroid initiation, exacerbations.",
		sources: [
			"NICE NG80",
			"WHO Asthma Fact Sheet 2023",
			"CDC Asthma Data 2024"
		]
	}
];
var pipelineStages = [
	{
		name: "Ingestion",
		metric: "2 PDFs · Diabetes Canada + NICE NG28"
	},
	{
		name: "Chunking",
		metric: "Config B · 1024 tokens · overlap 100"
	},
	{
		name: "Embeddings",
		metric: "BAAI/bge-small-en-v1.5 · cosine"
	},
	{
		name: "Retrieval",
		metric: "Dense top-k=5 · numpy index"
	},
	{
		name: "Guardrails",
		metric: "Query + answer safety checks"
	},
	{
		name: "Grounded LLM",
		metric: "Groq chat · citation-constrained"
	},
	{
		name: "Evidence Panel",
		metric: "Chunks with page + section_title"
	}
];
var evalRows = [
	{
		q: "Stage 1 hypertension threshold?",
		expected: "who-htn-0142",
		retrieved: "who-htn-0142",
		match: true,
		citation: true,
		notes: "Rank 1"
	},
	{
		q: "When to confirm with ABPM?",
		expected: "nice-ng136-0031",
		retrieved: "nice-ng136-0031",
		match: true,
		citation: true,
		notes: "Rank 1"
	},
	{
		q: "First-line drug classes?",
		expected: "who-htn-0201",
		retrieved: "who-htn-0201",
		match: true,
		citation: true,
		notes: "Rank 2"
	},
	{
		q: "Step 2 add-on therapy?",
		expected: "nice-ng136-0088",
		retrieved: "nice-ng136-0088",
		match: true,
		citation: true,
		notes: "Rank 1"
	},
	{
		q: "Diabetes screening start age?",
		expected: "uspstf-dm-0012",
		retrieved: "uspstf-dm-0012",
		match: true,
		citation: true,
		notes: "Rank 1"
	},
	{
		q: "A1C diagnostic cut-point?",
		expected: "nice-ng28-0044",
		retrieved: "cdc-dm-0071",
		match: false,
		citation: false,
		notes: "Near-duplicate chunk"
	},
	{
		q: "Asthma ICS initiation step?",
		expected: "nice-ng80-0033",
		retrieved: "nice-ng80-0033",
		match: true,
		citation: true,
		notes: "Rank 1"
	},
	{
		q: "Pediatric asthma dosing?",
		expected: "—",
		retrieved: "—",
		match: true,
		citation: true,
		notes: "Correctly refused (out of scope)"
	},
	{
		q: "BP target in CKD?",
		expected: "who-htn-0233",
		retrieved: "who-htn-0219",
		match: false,
		citation: false,
		notes: "Adjacent section retrieved"
	},
	{
		q: "Home monitoring frequency?",
		expected: "cdc-htn-0009",
		retrieved: "cdc-htn-0009",
		match: true,
		citation: true,
		notes: "Rank 2"
	}
];
var guardrailLog = [
	{
		time: "11:04:22",
		query: "Stage 1 hypertension threshold?",
		classification: "Allowed"
	},
	{
		time: "11:05:10",
		query: "My 62-year-old on ramipril reads 152/94",
		classification: "Needs Caution"
	},
	{
		time: "11:06:41",
		query: "Crushing chest pain right now — dose?",
		classification: "Refuse"
	},
	{
		time: "11:08:03",
		query: "Best antibiotic for my dog's ear infection",
		classification: "Refuse"
	},
	{
		time: "11:09:55",
		query: "USPSTF diabetes screening age",
		classification: "Allowed"
	},
	{
		time: "11:11:17",
		query: "What medicine should I take for diabetes?",
		classification: "Refuse"
	},
	{
		time: "11:12:04",
		query: "Should I stop my own medication?",
		classification: "Needs Caution"
	}
];
function SignOutButton() {
	const navigate = useNavigate();
	const queryClient = useQueryClient();
	async function signOut() {
		await queryClient.cancelQueries();
		queryClient.clear();
		await supabase.auth.signOut();
		navigate({
			to: "/auth",
			replace: true
		});
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
		type: "button",
		onClick: signOut,
		className: "inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogOut, {
			className: "size-3.5",
			strokeWidth: 1.5
		}), "Sign out"]
	});
}
var THEME_STORAGE_KEY = "clinirag-theme";
function resolveInitialTheme() {
	if (typeof window === "undefined") return "light";
	const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
	if (stored === "light" || stored === "dark") return stored;
	return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
function applyTheme(theme) {
	const root = document.documentElement;
	root.classList.toggle("dark", theme === "dark");
	root.style.colorScheme = theme;
}
function useTheme() {
	const [theme, setThemeState] = (0, import_react.useState)("light");
	const [mounted, setMounted] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		const initial = resolveInitialTheme();
		setThemeState(initial);
		applyTheme(initial);
		setMounted(true);
	}, []);
	return {
		theme,
		setTheme: (0, import_react.useCallback)((next) => {
			setThemeState(next);
			applyTheme(next);
			window.localStorage.setItem(THEME_STORAGE_KEY, next);
		}, []),
		toggleTheme: (0, import_react.useCallback)(() => {
			setThemeState((current) => {
				const next = current === "dark" ? "light" : "dark";
				applyTheme(next);
				window.localStorage.setItem(THEME_STORAGE_KEY, next);
				return next;
			});
		}, []),
		mounted
	};
}
function ThemeToggle() {
	const { theme, toggleTheme, mounted } = useTheme();
	const isDark = mounted && theme === "dark";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		onClick: toggleTheme,
		"aria-label": isDark ? "Switch to light mode" : "Switch to dark mode",
		title: isDark ? "Light mode" : "Dark mode",
		className: "inline-flex size-8 items-center justify-center rounded-md border border-border text-foreground transition-colors hover:border-primary/50 hover:bg-accent",
		children: isDark ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sun, {
			className: "size-4",
			strokeWidth: 1.5
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Moon, {
			className: "size-4",
			strokeWidth: 1.5
		})
	});
}
//#endregion
export { guardrailLog as a, evalRows as i, ThemeToggle as n, pipelineStages as o, cn as r, topics as s, SignOutButton as t };
