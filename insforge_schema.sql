-- InsForge schema for computer-usage-tracker
create table if not exists users (
   id         uuid primary key,
   email      text null,
   created_at timestamptz not null default now()
);

create table if not exists sessions (
   id           uuid primary key,
   user_id      uuid null,
   started_at   timestamptz not null,
   ended_at     timestamptz null,
   session_name text null,
   device_name  text null,
   os_name      text null,
   sync_enabled boolean not null default false,
   created_at   timestamptz not null default now()
);

create table if not exists events (
   id           uuid primary key,
   session_id   uuid not null
      references sessions ( id ),
   timestamp    timestamptz not null,
   event_type   text not null,
   app_name     text null,
   window_title text null,
   metadata     jsonb not null,
   created_at   timestamptz not null default now()
);

create table if not exists screenshots (
   id           uuid primary key,
   session_id   uuid not null
      references sessions ( id ),
   event_id     uuid null
      references events ( id ),
   storage_path text not null,
   ocr_text     text null,
   captured_at  timestamptz not null,
   created_at   timestamptz not null default now()
);

create table if not exists summaries (
   id          uuid primary key,
   session_id  uuid not null
      references sessions ( id ),
   pseudocode  text not null,
   suggestions jsonb not null,
   created_at  timestamptz not null default now()
);
