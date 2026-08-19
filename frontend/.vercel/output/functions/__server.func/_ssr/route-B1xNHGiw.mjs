import { i as __toESM } from "../_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "../_libs/react+tanstack__react-query.mjs";
import { _ as useNavigate, f as Outlet, l as useRouterState } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as useAuth } from "./use-auth-DtWIkJr7.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/route-B1xNHGiw.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function AuthenticatedLayout() {
	const { session, loading } = useAuth();
	const navigate = useNavigate();
	const href = useRouterState({ select: (s) => s.location.href });
	(0, import_react.useEffect)(() => {
		if (!loading && !session && !href.startsWith("/auth")) navigate({
			to: "/auth",
			search: { redirect: href },
			replace: true
		});
	}, [
		loading,
		session,
		navigate,
		href
	]);
	if (loading || !session) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex min-h-screen items-center justify-center bg-background",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "font-mono text-[12px] uppercase tracking-wide text-muted-foreground",
			children: "Verifying session…"
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {});
}
//#endregion
export { AuthenticatedLayout as component };
