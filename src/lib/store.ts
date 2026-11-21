import "server-only";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { sql } from "./db";
import { bogotaToday, buildReport, formatLongDate, isIsoDate, monthStart } from "./life";
import { seedAssets, seedCosts, seedLiabilities, seedMilestones, seedProfile } from "./seed";
import type {
  Asset,
  AssetKind,
  Cost,
  DailyLog,
  Liability,
  LifeState,
  Milestone,
  Profile,
  ReportBody,
  ReportSummary,
} from "./types";
import {
  positiveId,
  sanitizeAsset,
  sanitizeCost,
  sanitizeLiability,
  sanitizeLog,
  sanitizeMilestone,
  sanitizeProfile,
} from "./validate";

type Row = Record<string, unknown>;

function asDate(value: unknown): string {
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  return String(value).slice(0, 10);
}

function asIso(value: unknown): string {
  if (value instanceof Date) return value.toISOString();
  const date = new Date(String(value));
  return Number.isNaN(date.getTime()) ? new Date(0).toISOString() : date.toISOString();
}

function asNumber(value: unknown): number {
  return Number(value);
}

function asNumberOrNull(value: unknown): number | null {
  if (value == null) return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function asBool(value: unknown): boolean {
  return value === true || value === "t" || value === "true" || value === 1;
}

function mapAsset(row: Row): Asset {
  return {
    id: asNumber(row.id),
    name: String(row.name),
    kind: row.kind as AssetKind,
    detail: String(row.detail ?? ""),
    valueCop: asNumberOrNull(row.value_cop),
    valueIsEstimate: asBool(row.value_is_estimate),
    owned: asBool(row.owned),
    note: String(row.note ?? ""),
  };
}

function mapLiability(row: Row): Liability {
  return {
    id: asNumber(row.id),
    name: String(row.name),
    balanceCop: asNumber(row.balance_cop),
    monthlyCop: asNumberOrNull(row.monthly_cop),
    confirmed: asBool(row.confirmed),
    note: String(row.note ?? ""),
  };
}

function mapCost(row: Row): Cost {
  return {
    id: asNumber(row.id),
    name: String(row.name),
    amountCop: asNumber(row.amount_cop),
    note: String(row.note ?? ""),
  };
}

function mapLog(row: Row): DailyLog {
  return {
    id: asNumber(row.id),
    logDate: asDate(row.log_date),
    health: asNumberOrNull(row.health),
    energy: asNumberOrNull(row.energy),
    mood: asNumberOrNull(row.mood),
    sleepHours: asNumberOrNull(row.sleep_hours),
    studied: asBool(row.studied),
    worked: asBool(row.worked),
    incomeCop: asNumber(row.income_cop),
    expenseCop: asNumber(row.expense_cop),
    note: String(row.note ?? ""),
  };
}

function mapMilestone(row: Row): Milestone {
  return {
    id: asNumber(row.id),
    happenedOn: asDate(row.happened_on),
    title: String(row.title),
    detail: String(row.detail ?? ""),
  };
}

function mapReport(row: Row): ReportSummary {
  return {
    id: asNumber(row.id),
    title: String(row.title),
    periodStart: row.period_start == null ? null : asDate(row.period_start),
    periodEnd: row.period_end == null ? null : asDate(row.period_end),
    createdAt: asIso(row.created_at),
  };
}

async function countOf(
  table: "assets" | "liabilities" | "costs" | "daily_logs" | "milestones" | "reports",
  owner: string,
): Promise<number> {
  const queries = {
    assets: "select count(*) as n from assets where owner_sub = $1",
    liabilities: "select count(*) as n from liabilities where owner_sub = $1",
    costs: "select count(*) as n from costs where owner_sub = $1",
    daily_logs: "select count(*) as n from daily_logs where owner_sub = $1",
    milestones: "select count(*) as n from milestones where owner_sub = $1",
    reports: "select count(*) as n from reports where owner_sub = $1",
  } as const;
  const rows = await sql<{ n: unknown }>(queries[table], [owner]);
  return Number(rows[0]?.n ?? 0);
}

export async function ensureOwner(owner: string): Promise<void> {
  const existing = await sql<{ owner_sub: string }>("select owner_sub from profiles where owner_sub = $1", [owner]);
  if (existing.length > 0) return;
  const inserted = await sql<{ owner_sub: string }>(
    "insert into profiles (owner_sub, data) values ($1, $2::jsonb) on conflict (owner_sub) do nothing returning owner_sub",
    [owner, JSON.stringify(seedProfile())],
  );
  if (inserted.length === 0) return;
  try {
    for (const [index, asset] of seedAssets.entries()) {
      await sql(
        `insert into assets (owner_sub, name, kind, detail, value_cop, value_is_estimate, owned, note, sort_order)
         values ($1,$2,$3,$4,$5,$6,$7,$8,$9)`,
        [owner, asset.name, asset.kind, asset.detail, asset.valueCop, asset.valueIsEstimate, asset.owned, asset.note, index],
      );
    }
    for (const [index, debt] of seedLiabilities.entries()) {
      await sql(
        `insert into liabilities (owner_sub, name, balance_cop, monthly_cop, confirmed, note, sort_order)
         values ($1,$2,$3,$4,$5,$6,$7)`,
        [owner, debt.name, debt.balanceCop, debt.monthlyCop, debt.confirmed, debt.note, index],
      );
    }
    for (const [index, cost] of seedCosts.entries()) {
      await sql(
        "insert into costs (owner_sub, name, amount_cop, note, sort_order) values ($1,$2,$3,$4,$5)",
        [owner, cost.name, cost.amountCop, cost.note, index],
      );
    }
    for (const [index, milestone] of seedMilestones.entries()) {
      await sql(
        "insert into milestones (owner_sub, happened_on, title, detail, sort_order) values ($1,$2,$3,$4,$5)",
        [owner, milestone.happenedOn, milestone.title, milestone.detail, index],
      );
    }
    const portrait = await readFile(path.join(process.cwd(), "private", "portrait.jpg"));
    await sql(
      "insert into portraits (owner_sub, image_b64, content_type) values ($1,$2,'image/jpeg')",
      [owner, portrait.toString("base64")],
    );
  } catch (error) {
    await sql("delete from portraits where owner_sub = $1", [owner]);
    await sql("delete from milestones where owner_sub = $1", [owner]);
    await sql("delete from costs where owner_sub = $1", [owner]);
    await sql("delete from liabilities where owner_sub = $1", [owner]);
    await sql("delete from assets where owner_sub = $1", [owner]);
    await sql("delete from profiles where owner_sub = $1", [owner]);
    throw error;
  }
}

async function loadProfile(owner: string): Promise<Profile> {
  const rows = await sql<{ data: unknown }>("select data from profiles where owner_sub = $1", [owner]);
  const raw = rows[0]?.data;
  const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
  return sanitizeProfile(parsed, seedProfile());
}

export async function readState(owner: string): Promise<LifeState> {
  await ensureOwner(owner);
  const [profile, assets, liabilities, costs, logs, milestones, reports, portrait] = await Promise.all([
    loadProfile(owner),
    sql("select * from assets where owner_sub = $1 order by sort_order, id", [owner]),
    sql("select * from liabilities where owner_sub = $1 order by sort_order, id", [owner]),
    sql("select * from costs where owner_sub = $1 order by sort_order, id", [owner]),
    sql("select * from daily_logs where owner_sub = $1 order by log_date desc limit 1000", [owner]),
    sql("select * from milestones where owner_sub = $1 order by happened_on desc, id desc", [owner]),
    sql(
      "select id, title, period_start, period_end, created_at from reports where owner_sub = $1 order by created_at desc limit 100",
      [owner],
    ),
    sql("select owner_sub from portraits where owner_sub = $1", [owner]),
  ]);
  return {
    today: bogotaToday(),
    profile,
    assets: assets.map(mapAsset),
    liabilities: liabilities.map(mapLiability),
    costs: costs.map(mapCost),
    logs: logs.map(mapLog),
    milestones: milestones.map(mapMilestone),
    reports: reports.map(mapReport),
    hasPortrait: portrait.length > 0,
  };
}

async function saveProfileData(owner: string, profile: Profile): Promise<void> {
  await sql("update profiles set data = $2::jsonb, updated_at = now() where owner_sub = $1", [
    owner,
    JSON.stringify(profile),
  ]);
}

export async function updateProfile(owner: string, input: unknown): Promise<LifeState> {
  await ensureOwner(owner);
  const current = await loadProfile(owner);
  await saveProfileData(owner, sanitizeProfile(input, current));
  return readState(owner);
}

export async function upsertLog(owner: string, input: unknown): Promise<LifeState> {
  await ensureOwner(owner);
  const log = sanitizeLog(input);
  if (!log) throw new Error("El día no tiene una fecha válida.");
  const count = await countOf("daily_logs", owner);
  const existing = await sql("select id from daily_logs where owner_sub = $1 and log_date = $2", [owner, log.logDate]);
  if (existing.length === 0 && count >= 2000) throw new Error("Ya hay 2000 días. Borra alguno antes de agregar otro.");
  await sql(
    `insert into daily_logs
      (owner_sub, log_date, health, energy, mood, sleep_hours, studied, worked, income_cop, expense_cop, note)
     values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
     on conflict (owner_sub, log_date) do update set
      health = excluded.health,
      energy = excluded.energy,
      mood = excluded.mood,
      sleep_hours = excluded.sleep_hours,
      studied = excluded.studied,
      worked = excluded.worked,
      income_cop = excluded.income_cop,
      expense_cop = excluded.expense_cop,
      note = excluded.note`,
    [
      owner,
      log.logDate,
      log.health,
      log.energy,
      log.mood,
      log.sleepHours,
      log.studied,
      log.worked,
      log.incomeCop,
      log.expenseCop,
      log.note,
    ],
  );
  return readState(owner);
}

export async function deleteLog(owner: string, logDate: string): Promise<LifeState> {
  if (!isIsoDate(logDate)) throw new Error("Fecha inválida.");
  await sql("delete from daily_logs where owner_sub = $1 and log_date = $2", [owner, logDate]);
  return readState(owner);
}

async function nextSort(table: "assets" | "liabilities" | "costs" | "milestones", owner: string): Promise<number> {
  const queries = {
    assets: "select coalesce(max(sort_order), -1) as n from assets where owner_sub = $1",
    liabilities: "select coalesce(max(sort_order), -1) as n from liabilities where owner_sub = $1",
    costs: "select coalesce(max(sort_order), -1) as n from costs where owner_sub = $1",
    milestones: "select coalesce(max(sort_order), -1) as n from milestones where owner_sub = $1",
  } as const;
  const rows = await sql<{ n: unknown }>(queries[table], [owner]);
  return Number(rows[0]?.n ?? -1) + 1;
}

export async function createAsset(owner: string, input: unknown): Promise<LifeState> {
  await ensureOwner(owner);
  const asset = sanitizeAsset(input);
  if (!asset) throw new Error("La cosa necesita un nombre.");
  if ((await countOf("assets", owner)) >= 100) throw new Error("Ya hay 100 cosas.");
  await sql(
    `insert into assets (owner_sub, name, kind, detail, value_cop, value_is_estimate, owned, note, sort_order)
     values ($1,$2,$3,$4,$5,$6,$7,$8,$9)`,
    [owner, asset.name, asset.kind, asset.detail, asset.valueCop, asset.valueIsEstimate, asset.owned, asset.note, await nextSort("assets", owner)],
  );
  return readState(owner);
}

export async function updateAsset(owner: string, id: number, input: unknown): Promise<LifeState> {
  const asset = sanitizeAsset(input);
  if (!asset) throw new Error("La cosa necesita un nombre.");
  const updated = await sql(
    `update assets set name=$3, kind=$4, detail=$5, value_cop=$6, value_is_estimate=$7, owned=$8, note=$9
     where owner_sub=$1 and id=$2 returning id`,
    [owner, id, asset.name, asset.kind, asset.detail, asset.valueCop, asset.valueIsEstimate, asset.owned, asset.note],
  );
  if (updated.length === 0) throw new Error("No encontré esa cosa.");
  return readState(owner);
}

export async function deleteAsset(owner: string, id: number): Promise<LifeState> {
  await sql("delete from assets where owner_sub = $1 and id = $2", [owner, id]);
  return readState(owner);
}

export async function createLiability(owner: string, input: unknown): Promise<LifeState> {
  await ensureOwner(owner);
  const debt = sanitizeLiability(input);
  if (!debt) throw new Error("La deuda necesita un nombre.");
  if ((await countOf("liabilities", owner)) >= 100) throw new Error("Ya hay 100 deudas.");
  await sql(
    `insert into liabilities (owner_sub, name, balance_cop, monthly_cop, confirmed, note, sort_order)
     values ($1,$2,$3,$4,$5,$6,$7)`,
    [owner, debt.name, debt.balanceCop, debt.monthlyCop, debt.confirmed, debt.note, await nextSort("liabilities", owner)],
  );
  return readState(owner);
}

export async function updateLiability(owner: string, id: number, input: unknown): Promise<LifeState> {
  const debt = sanitizeLiability(input);
  if (!debt) throw new Error("La deuda necesita un nombre.");
  const updated = await sql(
    `update liabilities set name=$3, balance_cop=$4, monthly_cop=$5, confirmed=$6, note=$7
     where owner_sub=$1 and id=$2 returning id`,
    [owner, id, debt.name, debt.balanceCop, debt.monthlyCop, debt.confirmed, debt.note],
  );
  if (updated.length === 0) throw new Error("No encontré esa deuda.");
  return readState(owner);
}

export async function deleteLiability(owner: string, id: number): Promise<LifeState> {
  await sql("delete from liabilities where owner_sub = $1 and id = $2", [owner, id]);
  return readState(owner);
}

export async function createCost(owner: string, input: unknown): Promise<LifeState> {
  await ensureOwner(owner);
  const cost = sanitizeCost(input);
  if (!cost) throw new Error("El costo necesita un nombre.");
  if ((await countOf("costs", owner)) >= 50) throw new Error("Ya hay 50 costos.");
  await sql(
    "insert into costs (owner_sub, name, amount_cop, note, sort_order) values ($1,$2,$3,$4,$5)",
    [owner, cost.name, cost.amountCop, cost.note, await nextSort("costs", owner)],
  );
  return readState(owner);
}

export async function updateCost(owner: string, id: number, input: unknown): Promise<LifeState> {
  const cost = sanitizeCost(input);
  if (!cost) throw new Error("El costo necesita un nombre.");
  const updated = await sql(
    "update costs set name=$3, amount_cop=$4, note=$5 where owner_sub=$1 and id=$2 returning id",
    [owner, id, cost.name, cost.amountCop, cost.note],
  );
  if (updated.length === 0) throw new Error("No encontré ese costo.");
  return readState(owner);
}

export async function deleteCost(owner: string, id: number): Promise<LifeState> {
  await sql("delete from costs where owner_sub = $1 and id = $2", [owner, id]);
  return readState(owner);
}

export async function createMilestone(owner: string, input: unknown): Promise<LifeState> {
  await ensureOwner(owner);
  const milestone = sanitizeMilestone(input);
  if (!milestone) throw new Error("El hito necesita fecha y título.");
  if ((await countOf("milestones", owner)) >= 200) throw new Error("Ya hay 200 hitos.");
  await sql(
    "insert into milestones (owner_sub, happened_on, title, detail, sort_order) values ($1,$2,$3,$4,$5)",
    [owner, milestone.happenedOn, milestone.title, milestone.detail, await nextSort("milestones", owner)],
  );
  return readState(owner);
}

export async function deleteMilestone(owner: string, id: number): Promise<LifeState> {
  await sql("delete from milestones where owner_sub = $1 and id = $2", [owner, id]);
  return readState(owner);
}

export async function setLiquidation(
  owner: string,
  status: "recibida" | "otro" | "no_llego",
  amountCop: number | null,
): Promise<LifeState> {
  await ensureOwner(owner);
  const profile = await loadProfile(owner);
  const received = status === "recibida" ? (amountCop ?? profile.liquidationExpectedCop) : amountCop;
  const next = sanitizeProfile(
    {
      ...profile,
      liquidationStatus: status,
      liquidationReceivedCop: status === "no_llego" ? null : received,
      reviewed: true,
    },
    profile,
  );
  await saveProfileData(owner, next);
  if (status !== "no_llego" && received != null) {
    const cash = await sql<{ id: unknown }>(
      "select id from assets where owner_sub = $1 and kind = 'dinero' order by sort_order, id limit 1",
      [owner],
    );
    if (cash.length > 0) {
      await sql(
        "update assets set value_cop = $3, value_is_estimate = false, note = $4 where owner_sub = $1 and id = $2",
        [
          owner,
          asNumber(cash[0].id),
          received,
          status === "recibida"
            ? "Registraste la liquidación de Nelumbo como el saldo de tus cuentas."
            : "Saldo de cuentas que anotaste al cerrar la liquidación.",
        ],
      );
    }
  }
  return readState(owner);
}

export async function createReport(owner: string, periodStart: string, periodEnd: string): Promise<{ id: number; state: LifeState }> {
  const state = await readState(owner);
  const start = isIsoDate(periodStart) ? periodStart : monthStart(state.today);
  const end = isIsoDate(periodEnd) ? periodEnd : state.today;
  const [from, to] = start <= end ? [start, end] : [end, start];
  if ((await countOf("reports", owner)) >= 200) throw new Error("Ya hay 200 reportes. Borra alguno.");
  const body: ReportBody = buildReport({
    today: state.today,
    periodStart: from,
    periodEnd: to,
    profile: state.profile,
    assets: state.assets,
    liabilities: state.liabilities,
    costs: state.costs,
    logs: state.logs,
    milestones: state.milestones,
  });
  const title = from === to ? `Punto del ${formatLongDate(from)}` : `Punto del ${formatLongDate(from)} al ${formatLongDate(to)}`;
  const inserted = await sql<{ id: unknown }>(
    "insert into reports (owner_sub, title, period_start, period_end, body) values ($1,$2,$3,$4,$5::jsonb) returning id",
    [owner, title, from, to, JSON.stringify(body)],
  );
  return { id: asNumber(inserted[0].id), state: await readState(owner) };
}

export async function deleteReport(owner: string, id: number): Promise<LifeState> {
  await sql("delete from reports where owner_sub = $1 and id = $2", [owner, id]);
  return readState(owner);
}

const IMAGE_TYPES: Record<string, string> = {
  jpeg: "image/jpeg",
  png: "image/png",
  webp: "image/webp",
};

export function sniffImage(bytes: Buffer): string | null {
  if (bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) return IMAGE_TYPES.jpeg;
  if (bytes.length >= 8 && bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47) {
    return IMAGE_TYPES.png;
  }
  if (
    bytes.length >= 12 &&
    bytes.toString("ascii", 0, 4) === "RIFF" &&
    bytes.toString("ascii", 8, 12) === "WEBP"
  ) {
    return IMAGE_TYPES.webp;
  }
  return null;
}

export async function savePortrait(owner: string, bytes: Buffer, contentType: string): Promise<LifeState> {
  await ensureOwner(owner);
  const b64 = bytes.toString("base64");
  await sql(
    `insert into portraits (owner_sub, image_b64, content_type)
     values ($1,$2,$3)
     on conflict (owner_sub) do update set image_b64 = excluded.image_b64, content_type = excluded.content_type, updated_at = now()`,
    [owner, b64, contentType],
  );
  const profile = await loadProfile(owner);
  const today = bogotaToday();
  await saveProfileData(
    owner,
    sanitizeProfile(
      { ...profile, photoCaption: `Actualizada el ${formatLongDate(today)}`, reviewed: profile.reviewed },
      profile,
    ),
  );
  return readState(owner);
}

export async function readPortrait(owner: string): Promise<{ bytes: Buffer; contentType: string } | null> {
  const rows = await sql<{ image_b64: string; content_type: string }>(
    "select image_b64, content_type from portraits where owner_sub = $1",
    [owner],
  );
  if (rows.length === 0) return null;
  return { bytes: Buffer.from(rows[0].image_b64, "base64"), contentType: rows[0].content_type };
}

export async function readReportRecord(
  owner: string,
  id: number,
): Promise<{ body: ReportBody; createdAt: string; title: string } | null> {
  const rows = await sql<{ body: unknown; title: string; created_at: unknown }>(
    "select body, title, created_at from reports where owner_sub = $1 and id = $2",
    [owner, id],
  );
  if (rows.length === 0) return null;
  const raw = rows[0].body;
  const parsed = (typeof raw === "string" ? JSON.parse(raw) : raw) as ReportBody;
  const body = { ...parsed, profile: sanitizeProfile(parsed.profile, seedProfile()) };
  return {
    body,
    title: rows[0].title,
    createdAt: asIso(rows[0].created_at),
  };
}

export { positiveId };
