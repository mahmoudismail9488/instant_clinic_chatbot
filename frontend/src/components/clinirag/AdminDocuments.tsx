import { useCallback, useEffect, useState } from "react";
import { FileUp, Loader2, Lock } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useIsAdmin } from "@/hooks/use-auth";

type Doc = {
  id: string;
  title: string;
  source_org: string;
  topic: string | null;
  created_at: string;
};

export function AdminDocuments({ userId }: { userId: string | undefined }) {
  const { isAdmin, checking } = useIsAdmin(userId);
  const [docs, setDocs] = useState<Doc[]>([]);
  const [title, setTitle] = useState("");
  const [org, setOrg] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    const { data } = await supabase
      .from("guideline_documents")
      .select("id, title, source_org, topic, created_at")
      .order("created_at", { ascending: false });
    setDocs((data ?? []) as Doc[]);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function upload(e: React.FormEvent) {
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
      uploaded_by: userId,
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

  return (
    <section className="rounded-xl border border-border bg-card">
      <h2 className="border-b border-border px-4 py-3 text-[14px] font-semibold text-foreground">
        Guideline corpus · source documents
      </h2>

      <div className="p-4">
        {checking ? (
          <p className="font-mono text-[12px] text-muted-foreground">Checking permissions…</p>
        ) : isAdmin ? (
          <form onSubmit={upload} className="grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
            <input
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Document title"
              className="h-10 rounded-lg border border-border bg-background px-3 text-[14px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
            />
            <input
              required
              value={org}
              onChange={(e) => setOrg(e.target.value)}
              placeholder="Source org (WHO, CDC, NICE…)"
              className="h-10 rounded-lg border border-border bg-background px-3 text-[14px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
            />
            <div className="flex items-center gap-2">
              <input
                required
                type="file"
                accept=".pdf,.txt,.md"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="max-w-[220px] text-[13px] text-muted-foreground"
              />
              <button
                type="submit"
                disabled={busy}
                className="inline-flex h-10 items-center gap-1.5 rounded-lg bg-primary px-3.5 text-[14px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50"
              >
                {busy ? (
                  <Loader2 className="size-4 animate-spin" strokeWidth={1.5} />
                ) : (
                  <FileUp className="size-4" strokeWidth={1.5} />
                )}
                Upload
              </button>
            </div>
          </form>
        ) : (
          <p className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2 text-[13px] text-muted-foreground">
            <Lock className="size-3.5" strokeWidth={1.5} />
            Uploading guideline documents is restricted to administrators.
          </p>
        )}

        {error && (
          <p className="mt-3 rounded-lg border border-confidence-insufficient/30 bg-safety-refuse-bg px-3 py-2 text-[13px] text-confidence-insufficient">
            {error}
          </p>
        )}

        <ul className="mt-4 space-y-2">
          {docs.length === 0 && (
            <li className="font-mono text-[12px] text-muted-foreground">No documents ingested yet.</li>
          )}
          {docs.map((d) => (
            <li
              key={d.id}
              className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-[13px]"
            >
              <span className="text-foreground">{d.title}</span>
              <span className="font-mono text-[12px] text-muted-foreground">{d.source_org}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}