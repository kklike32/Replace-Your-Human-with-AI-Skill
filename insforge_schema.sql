create table if not exists sessions (
  id uuid primary key,
  user_id uuid nullable,
  started_at timestamptz not null,
  ended_at timestamptz nullable,
  session_name text nullable,
  device_name text nullable,
  os_name text nullable,
  created_at timestamptz default now()
);

create table if not exists chunk_summaries (
  id uuid primary key,
  session_id uuid references sessions(id),
  chunk_index integer not null,
  started_at timestamptz not null,
  ended_at timestamptz not null,
  summary text not null,
  observed_apps jsonb nullable,
  confidence text nullable,
  created_at timestamptz default now()
);

create table if not exists final_pseudocode (
  id uuid primary key,
  session_id uuid references sessions(id),
  pseudocode jsonb not null,
  plain_text text not null,
  suggestions jsonb nullable,
  created_at timestamptz default now()
);
