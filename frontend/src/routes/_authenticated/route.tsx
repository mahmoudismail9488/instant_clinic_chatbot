import { useEffect } from "react";
import { Outlet, createFileRoute, useNavigate, useRouterState } from "@tanstack/react-router";
import { useAuth } from "@/hooks/use-auth";

export const Route = createFileRoute("/_authenticated")({
  ssr: false,
  component: AuthenticatedLayout,
});

function AuthenticatedLayout() {
  const { session, loading } = useAuth();
  const navigate = useNavigate();
  const href = useRouterState({ select: (s) => s.location.href });

  useEffect(() => {
    if (!loading && !session && !href.startsWith("/auth")) {
      navigate({ to: "/auth", search: { redirect: href }, replace: true });
    }
  }, [loading, session, navigate, href]);

  if (loading || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <p className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">
          Verifying session…
        </p>
      </div>
    );
  }

  return <Outlet />;
}