-- =====================================================================
-- Memoria de la Junta Directiva Agéntica IAM™
-- Ejecutar una sola vez en el SQL Editor de Supabase.
-- =====================================================================

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------
-- Sesiones de junta
-- ---------------------------------------------------------------------
create table if not exists junta_sesiones (
    id              uuid primary key default gen_random_uuid(),
    sdk_session_id  text unique,                 -- id de sesión del Claude Agent SDK
    titulo          text not null,
    tema            text,
    estado          text not null default 'abierta'
                    check (estado in ('abierta', 'cerrada')),
    creada_en       timestamptz not null default now(),
    cerrada_en      timestamptz,
    metadata        jsonb not null default '{}'::jsonb
);

create index if not exists idx_sesiones_creada  on junta_sesiones (creada_en desc);
create index if not exists idx_sesiones_sdk     on junta_sesiones (sdk_session_id);

-- ---------------------------------------------------------------------
-- Transcripción de cada sesión
-- ---------------------------------------------------------------------
create table if not exists junta_mensajes (
    id          bigserial primary key,
    sesion_id   uuid not null references junta_sesiones(id) on delete cascade,
    orden       integer not null,
    rol         text not null
                check (rol in ('usuario', 'presidencia', 'consejero', 'sistema')),
    consejero   text,                            -- nombre del subagente, si aplica
    contenido   text not null,
    creado_en   timestamptz not null default now()
);

create index if not exists idx_mensajes_sesion on junta_mensajes (sesion_id, orden);

-- ---------------------------------------------------------------------
-- Decisiones formales
-- ---------------------------------------------------------------------
create table if not exists junta_decisiones (
    id                     uuid primary key default gen_random_uuid(),
    sesion_id              uuid references junta_sesiones(id) on delete set null,
    asunto                 text not null,
    decision               text not null,
    fundamento             text,
    consejeros_convocados  text[] not null default '{}',
    desacuerdos            text,
    creada_en              timestamptz not null default now()
);

create index if not exists idx_decisiones_creada on junta_decisiones (creada_en desc);
create index if not exists idx_decisiones_asunto
    on junta_decisiones using gin (to_tsvector('spanish', asunto || ' ' || decision));

-- ---------------------------------------------------------------------
-- Acuerdos accionables
-- ---------------------------------------------------------------------
create table if not exists junta_acuerdos (
    id             uuid primary key default gen_random_uuid(),
    sesion_id      uuid references junta_sesiones(id) on delete set null,
    decision_id    uuid references junta_decisiones(id) on delete set null,
    acuerdo        text not null,
    responsable    text not null,
    fecha_limite   date,
    metrica        text,                          -- cómo se verifica que se cumplió
    estado         text not null default 'abierto'
                   check (estado in ('abierto', 'en_progreso', 'cumplido', 'cancelado')),
    creado_en      timestamptz not null default now(),
    actualizado_en timestamptz not null default now()
);

create index if not exists idx_acuerdos_estado on junta_acuerdos (estado, fecha_limite);

-- ---------------------------------------------------------------------
-- KPIs del negocio en el tiempo
-- ---------------------------------------------------------------------
create table if not exists junta_kpis (
    id         bigserial primary key,
    periodo    date not null,                     -- normalmente el primer día del mes
    nombre     text not null,
    valor      numeric not null,
    unidad     text,                              -- COP, %, días, unidades...
    fuente     text,                              -- Airtable, cálculo CFO, manual...
    nota       text,
    creado_en  timestamptz not null default now(),
    unique (periodo, nombre)
);

create index if not exists idx_kpis_nombre on junta_kpis (nombre, periodo desc);

-- ---------------------------------------------------------------------
-- Datos que faltaron para decidir bien
-- ---------------------------------------------------------------------
create table if not exists junta_datos_faltantes (
    id         uuid primary key default gen_random_uuid(),
    sesion_id  uuid references junta_sesiones(id) on delete set null,
    dato       text not null,
    para_que   text,
    resuelto   boolean not null default false,
    creado_en  timestamptz not null default now()
);

create index if not exists idx_faltantes_resuelto on junta_datos_faltantes (resuelto);

-- ---------------------------------------------------------------------
-- Mantener actualizado_en
-- ---------------------------------------------------------------------
create or replace function junta_touch_actualizado_en()
returns trigger
language plpgsql
as $$
begin
    new.actualizado_en = now();
    return new;
end;
$$;

drop trigger if exists trg_acuerdos_touch on junta_acuerdos;
create trigger trg_acuerdos_touch
    before update on junta_acuerdos
    for each row execute function junta_touch_actualizado_en();

-- ---------------------------------------------------------------------
-- Seguridad
-- ---------------------------------------------------------------------
-- Estas tablas guardan información estratégica del negocio. Se activa RLS y NO se
-- crea ninguna política permisiva: así, la clave `anon` no puede leer nada.
-- La junta se conecta con la SERVICE ROLE KEY, que omite RLS por diseño.
--
-- ⚠️ La service role key NUNCA debe llegar al navegador ni a un repositorio.
--    Vive solo en el .env del servidor donde corre la junta.
alter table junta_sesiones        enable row level security;
alter table junta_mensajes        enable row level security;
alter table junta_decisiones      enable row level security;
alter table junta_acuerdos        enable row level security;
alter table junta_kpis            enable row level security;
alter table junta_datos_faltantes enable row level security;
