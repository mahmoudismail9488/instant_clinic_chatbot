-- Per-account saved chats (run in Supabase SQL editor)
create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  title text not null,
  topic text,
  turns jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists chat_sessions_user_updated_idx
  on public.chat_sessions (user_id, updated_at desc);

alter table public.chat_sessions enable row level security;

create policy "Users read own chats"
  on public.chat_sessions for select
  using (auth.uid() = user_id);

create policy "Users insert own chats"
  on public.chat_sessions for insert
  with check (auth.uid() = user_id);

create policy "Users update own chats"
  on public.chat_sessions for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "Users delete own chats"
  on public.chat_sessions for delete
  using (auth.uid() = user_id);
