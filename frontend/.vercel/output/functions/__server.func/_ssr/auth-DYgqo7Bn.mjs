import { i as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { _ as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Route$2 } from "./router-cVTBtxXh.mjs";
import { t as supabase } from "./client-DeHMspjV.mjs";
import { t as useAuth } from "./use-auth-DtWIkJr7.mjs";
import { r as ShieldCheck, u as LoaderCircle } from "../_libs/lucide-react.mjs";
import { t as createLovableAuth } from "../_libs/lovable.dev__cloud-auth-js.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/auth-DYgqo7Bn.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var lovableAuth = createLovableAuth();
var lovable = { auth: { signInWithOAuth: async (provider, opts) => {
	const result = await lovableAuth.signInWithOAuth(provider, {
		...opts,
		extraParams: { ...opts?.extraParams }
	});
	if (result.redirected) return result;
	if (result.error) return result;
	try {
		await supabase.auth.setSession(result.tokens);
	} catch (e) {
		return { error: e instanceof Error ? e : new Error(String(e)) };
	}
	return result;
} } };
function safePath(value) {
	if (!value || !value.startsWith("/") || value.startsWith("//")) return "/workspace";
	if (value.startsWith("/auth")) return "/workspace";
	return value;
}
function AuthPage() {
	const { redirect } = Route$2.useSearch();
	const { session, loading } = useAuth();
	const navigate = useNavigate();
	const [mode, setMode] = (0, import_react.useState)("signin");
	const [email, setEmail] = (0, import_react.useState)("");
	const [password, setPassword] = (0, import_react.useState)("");
	const [busy, setBusy] = (0, import_react.useState)(false);
	const [message, setMessage] = (0, import_react.useState)(null);
	const [error, setError] = (0, import_react.useState)(null);
	const target = safePath(redirect);
	(0, import_react.useEffect)(() => {
		if (!loading && session) navigate({
			to: target,
			replace: true
		});
	}, [
		loading,
		session,
		navigate,
		target
	]);
	async function submit(e) {
		e.preventDefault();
		setBusy(true);
		setError(null);
		setMessage(null);
		if (mode === "signup") {
			const { data, error: err } = await supabase.auth.signUp({
				email,
				password,
				options: { emailRedirectTo: window.location.origin }
			});
			if (err) setError(err.message);
			else if (!data.session) setMessage("Check your email to confirm your account, then sign in.");
		} else {
			const { error: err } = await supabase.auth.signInWithPassword({
				email,
				password
			});
			if (err) setError(err.message);
		}
		setBusy(false);
	}
	async function google() {
		setError(null);
		setBusy(true);
		const result = await lovable.auth.signInWithOAuth("google", { redirect_uri: window.location.origin });
		if (result.error) {
			setError("Google sign-in failed. Please try again.");
			setBusy(false);
			return;
		}
		if (result.redirected) return;
		navigate({
			to: target,
			replace: true
		});
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
		className: "flex min-h-screen items-center justify-center bg-background px-4 py-16",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "w-full max-w-[420px]",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "font-mono text-[12px] uppercase tracking-wide text-primary",
					children: "CliniRAG · Access"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "mt-3 text-[28px] font-semibold leading-tight text-foreground",
					children: mode === "signin" ? "Sign in to your workspace" : "Create your clinician account"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-[14px] text-muted-foreground",
					children: "Guideline documents are curated by administrators. Clinicians query — they never upload."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-6 rounded-xl border border-border bg-card p-5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: google,
							disabled: busy,
							className: "flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-background px-4 py-2.5 text-[15px] font-medium text-foreground transition-colors hover:border-primary/50 disabled:opacity-50",
							children: "Continue with Google"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "my-4 flex items-center gap-3",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "h-px flex-1 bg-border" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-[12px] uppercase text-muted-foreground",
									children: "or email"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "h-px flex-1 bg-border" })
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
							onSubmit: submit,
							className: "space-y-3",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
									type: "email",
									required: true,
									value: email,
									onChange: (e) => setEmail(e.target.value),
									placeholder: "clinician@hospital.org",
									className: "h-10 w-full rounded-lg border border-border bg-background px-3 text-[15px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
									type: "password",
									required: true,
									minLength: 6,
									value: password,
									onChange: (e) => setPassword(e.target.value),
									placeholder: "Password",
									className: "h-10 w-full rounded-lg border border-border bg-background px-3 text-[15px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
									type: "submit",
									disabled: busy,
									className: "inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 text-[15px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50",
									children: [busy && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, {
										className: "size-4 animate-spin",
										strokeWidth: 1.5
									}), mode === "signin" ? "Sign in" : "Create account"]
								})
							]
						}),
						error && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-3 rounded-lg border border-confidence-insufficient/30 bg-safety-refuse-bg px-3 py-2 text-[13px] text-confidence-insufficient",
							children: error
						}),
						message && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-3 rounded-lg border border-border bg-secondary px-3 py-2 text-[13px] text-foreground",
							children: message
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => {
								setMode(mode === "signin" ? "signup" : "signin");
								setError(null);
								setMessage(null);
							},
							className: "mt-4 text-[13px] text-primary hover:text-primary-hover",
							children: mode === "signin" ? "No account? Create one" : "Already registered? Sign in"
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "mt-5 flex items-center gap-2 text-[12px] text-muted-foreground",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, {
						className: "size-3.5",
						strokeWidth: 1.5
					}), "File uploads are restricted to administrators. No patient data is stored."]
				})
			]
		})
	});
}
//#endregion
export { AuthPage as component };
