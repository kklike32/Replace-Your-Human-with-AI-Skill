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

create table if not exists workflow_templates (
  id uuid primary key,
  session_id uuid references sessions(id),
  title text not null,
  description text nullable,
  category text nullable,
  tags jsonb default '[]'::jsonb,
  pseudocode jsonb not null,
  plain_text text not null,
  created_from text default 'session_summary',
  created_at timestamptz default now()
);

create table if not exists workflow_insights (
  id uuid primary key,
  session_id uuid references sessions(id),
  summary text not null,
  main_apps jsonb default '[]'::jsonb,
  detected_task_type text nullable,
  tags jsonb default '[]'::jsonb,
  automation_score integer not null,
  automation_reason text nullable,
  recommended_next_action text nullable,
  created_at timestamptz default now()
);

create table if not exists agent_handoff_queue (
  id uuid primary key,
  session_id uuid references sessions(id),
  template_id uuid nullable references workflow_templates(id),
  status text default 'draft',
  proposed_action text not null,
  action_plan jsonb not null,
  requires_user_approval boolean default true,
  approved_at timestamptz nullable,
  executed_at timestamptz nullable,
  created_at timestamptz default now()
);

create table if not exists workflow_search_index (
  id uuid primary key,
  session_id uuid references sessions(id),
  template_id uuid nullable references workflow_templates(id),
  searchable_text text not null,
  tags jsonb default '[]'::jsonb,
  created_at timestamptz default now()
);
