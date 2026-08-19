import { i as __toESM } from "../_runtime.mjs";
import { i as require_react } from "../_libs/react+tanstack__react-query.mjs";
import { t as supabase } from "./client-DeHMspjV.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/use-auth-DtWIkJr7.js
var import_react = /* @__PURE__ */ __toESM(require_react());
function useAuth() {
	const [session, setSession] = (0, import_react.useState)(null);
	const [loading, setLoading] = (0, import_react.useState)(true);
	(0, import_react.useEffect)(() => {
		const { data } = supabase.auth.onAuthStateChange((_event, next) => {
			setSession(next);
			setLoading(false);
		});
		supabase.auth.getSession().then(({ data: { session: current } }) => {
			setSession(current);
			setLoading(false);
		});
		return () => data.subscription.unsubscribe();
	}, []);
	return {
		session,
		user: session?.user ?? null,
		loading
	};
}
function useIsAdmin(userId) {
	const [isAdmin, setIsAdmin] = (0, import_react.useState)(false);
	const [checking, setChecking] = (0, import_react.useState)(true);
	(0, import_react.useEffect)(() => {
		let active = true;
		if (!userId) {
			setIsAdmin(false);
			setChecking(false);
			return;
		}
		setChecking(true);
		supabase.from("user_roles").select("role").eq("user_id", userId).eq("role", "admin").maybeSingle().then(({ data }) => {
			if (!active) return;
			setIsAdmin(Boolean(data));
			setChecking(false);
		});
		return () => {
			active = false;
		};
	}, [userId]);
	return {
		isAdmin,
		checking
	};
}
//#endregion
export { useIsAdmin as n, useAuth as t };
