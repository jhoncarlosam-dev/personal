create table if not exists profiles (
  owner_sub text primary key,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

create table if not exists assets (
  id bigserial primary key,
  owner_sub text not null,
  name text not null,
  kind text not null,
  detail text not null default '',
  value_cop bigint,
  value_is_estimate boolean not null default true,
  owned boolean not null default true,
  note text not null default '',
  sort_order int not null default 0
);
create index if not exists assets_owner_idx on assets (owner_sub, sort_order, id);

create table if not exists liabilities (
  id bigserial primary key,
  owner_sub text not null,
  name text not null,
  balance_cop bigint not null default 0,
  monthly_cop bigint,
  confirmed boolean not null default false,
  note text not null default '',
  sort_order int not null default 0
);
create index if not exists liabilities_owner_idx on liabilities (owner_sub, sort_order, id);

create table if not exists costs (
  id bigserial primary key,
  owner_sub text not null,
  name text not null,
  amount_cop bigint not null default 0,
  note text not null default '',
  sort_order int not null default 0
);
create index if not exists costs_owner_idx on costs (owner_sub, sort_order, id);

create table if not exists daily_logs (
  id bigserial primary key,
  owner_sub text not null,
  log_date date not null,
  health smallint,
  energy smallint,
  mood smallint,
  sleep_hours numeric(4,1),
  studied boolean not null default false,
  worked boolean not null default false,
  income_cop bigint not null default 0,
  expense_cop bigint not null default 0,
  note text not null default '',
  unique (owner_sub, log_date)
);

create table if not exists milestones (
  id bigserial primary key,
  owner_sub text not null,
  happened_on date not null,
  title text not null,
  detail text not null default '',
  sort_order int not null default 0
);
create index if not exists milestones_owner_idx on milestones (owner_sub, happened_on, id);

create table if not exists reports (
  id bigserial primary key,
  owner_sub text not null,
  title text not null,
  period_start date,
  period_end date,
  body jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists reports_owner_idx on reports (owner_sub, created_at);

create table if not exists portraits (
  owner_sub text primary key,
  image_b64 text not null,
  content_type text not null,
  updated_at timestamptz not null default now()
);
