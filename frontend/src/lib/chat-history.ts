/** Per-account chat history — Supabase when available, localStorage fallback. */

import { supabase } from "@/integrations/supabase/client";
import type { Json } from "@/integrations/supabase/types";
import type { Turn } from "@/lib/clinirag-data";

export type ChatSession = {
  id: string;
  title: string;
  topic: string | null;
  turns: Turn[];
  updatedAt: string;
  createdAt: string;
};

const LS_PREFIX = "glucorag-chats:";

function lsKey(userId: string): string {
  return `${LS_PREFIX}${userId}`;
}

function readLocal(userId: string): ChatSession[] {
  try {
    const raw = localStorage.getItem(lsKey(userId));
    if (!raw) return [];
    const parsed = JSON.parse(raw) as ChatSession[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeLocal(userId: string, sessions: ChatSession[]): void {
  localStorage.setItem(lsKey(userId), JSON.stringify(sessions));
}

function titleFromTurns(turns: Turn[]): string {
  const first = turns[0]?.question?.trim();
  if (!first) return "New chat";
  return first.length > 64 ? `${first.slice(0, 61)}…` : first;
}

function mapRow(row: {
  id: string;
  title: string;
  topic: string | null;
  turns: Json;
  created_at: string;
  updated_at: string;
}): ChatSession {
  return {
    id: row.id,
    title: row.title,
    topic: row.topic,
    turns: (Array.isArray(row.turns) ? row.turns : []) as Turn[],
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

function persistLocal(userId: string, session: ChatSession): ChatSession {
  const existing = readLocal(userId);
  const idx = existing.findIndex((s) => s.id === session.id);
  if (idx >= 0) {
    session.createdAt = existing[idx]!.createdAt;
    existing[idx] = session;
  } else {
    existing.unshift(session);
  }
  writeLocal(userId, existing.slice(0, 40));
  return session;
}

export async function listChatSessions(userId: string): Promise<ChatSession[]> {
  try {
    const { data, error } = await supabase
      .from("chat_sessions")
      .select("id, title, topic, turns, created_at, updated_at")
      .eq("user_id", userId)
      .order("updated_at", { ascending: false });

    // PGRST205 = table missing from schema cache — fall back quietly.
    if (!error && data) {
      return data.map(mapRow);
    }
  } catch {
    /* network / client errors → local */
  }
  return readLocal(userId).sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

export async function saveChatSession(
  userId: string,
  input: {
    id?: string | null;
    topic?: string | null;
    turns: Turn[];
  },
): Promise<ChatSession> {
  const now = new Date().toISOString();
  const title = titleFromTurns(input.turns);
  const id = input.id || crypto.randomUUID();
  const payloadTurns = input.turns as unknown as Json;

  if (input.id) {
    const { data, error } = await supabase
      .from("chat_sessions")
      .update({
        title,
        topic: input.topic ?? null,
        turns: payloadTurns,
        updated_at: now,
      })
      .eq("id", input.id)
      .eq("user_id", userId)
      .select("id, title, topic, turns, created_at, updated_at")
      .maybeSingle();
    if (!error && data) return mapRow(data);
  }

  const { data, error } = await supabase
    .from("chat_sessions")
    .upsert(
      {
        id,
        user_id: userId,
        title,
        topic: input.topic ?? null,
        turns: payloadTurns,
        updated_at: now,
      },
      { onConflict: "id" },
    )
    .select("id, title, topic, turns, created_at, updated_at")
    .maybeSingle();

  if (!error && data) return mapRow(data);

  return persistLocal(userId, {
    id,
    title,
    topic: input.topic ?? null,
    turns: input.turns,
    createdAt: now,
    updatedAt: now,
  });
}

export async function deleteChatSession(userId: string, sessionId: string): Promise<void> {
  await supabase.from("chat_sessions").delete().eq("id", sessionId).eq("user_id", userId);
  writeLocal(
    userId,
    readLocal(userId).filter((s) => s.id !== sessionId),
  );
}
