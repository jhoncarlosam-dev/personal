import type {
  Asset,
  DailyLog,
  Liability,
  LogSummary,
  Milestone,
  Profile,
  ReportBody,
  Wealth,
} from "./types";

export type Elapsed = { years: number; months: number; days: number };

const DATE = /^\d{4}-\d{2}-\d{2}$/;

export function isIsoDate(value: string): boolean {
  if (!DATE.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return (
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day
  );
}

export function bogotaToday(now = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Bogota",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(now);
}

export function formatCop(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatLongDate(iso: string): string {
  if (!isIsoDate(iso)) return iso;
  const [year, month, day] = iso.split("-").map(Number);
  return new Intl.DateTimeFormat("es-CO", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, month - 1, day)));
}

export function formatStamp(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("es-CO", {
    timeZone: "America/Bogota",
    dateStyle: "long",
    timeStyle: "short",
  }).format(date);
}

export function elapsed(from: string, to: string): Elapsed | null {
  if (!isIsoDate(from) || !isIsoDate(to) || to < from) return null;
  const [toYear, toMonth, toDay] = to.split("-").map(Number);
  let years = toYear - Number(from.slice(0, 4));
  let months = toMonth - Number(from.slice(5, 7));
  let days = toDay - Number(from.slice(8, 10));
  if (days < 0) {
    months -= 1;
    const previousMonthDays = new Date(Date.UTC(toYear, toMonth - 1, 0)).getUTCDate();
    days += previousMonthDays;
  }
  if (months < 0) {
    years -= 1;
    months += 12;
  }
  if (years < 0) return null;
  return { years, months, days };
}

function unit(count: number, singular: string, plural: string): string {
  return `${count} ${count === 1 ? singular : plural}`;
}

export function formatElapsed(span: Elapsed): string {
  if (span.years === 0 && span.months === 0 && span.days === 0) return "hoy";
  if (span.years === 0 && span.months === 0) return unit(span.days, "día", "días");
  if (span.years === 0 && span.days === 0) return unit(span.months, "mes", "meses");
  if (span.years === 0) {
    return `${unit(span.months, "mes", "meses")} y ${unit(span.days, "día", "días")}`;
  }
  if (span.months === 0) return unit(span.years, "año", "años");
  return `${unit(span.years, "año", "años")} y ${unit(span.months, "mes", "meses")}`;
}

export function lastNDays(today: string, count: number): string[] {
  if (!isIsoDate(today) || count <= 0) return [];
  const [year, month, day] = today.split("-").map(Number);
  const anchor = new Date(Date.UTC(year, month - 1, day));
  const days: string[] = [];
  for (let index = count - 1; index >= 0; index -= 1) {
    const date = new Date(anchor);
    date.setUTCDate(date.getUTCDate() - index);
    days.push(date.toISOString().slice(0, 10));
  }
  return days;
}

export function monthStart(today: string): string {
  if (!isIsoDate(today)) return today;
  return `${today.slice(0, 8)}01`;
}

export function ageLabel(profile: Profile, today: string): { primary: string; secondary: string } {
  if (profile.birthDate && isIsoDate(profile.birthDate)) {
    const span = elapsed(profile.birthDate, today);
    if (span) {
      const extra = span.months > 0 ? ` y ${unit(span.months, "mes", "meses")}` : "";
      return {
        primary: `${span.years} años${extra}`,
        secondary: `Naciste el ${formatLongDate(profile.birthDate)}.`,
      };
    }
  }
  if (profile.reportedAge != null) {
    const when = profile.reportedAgeAsOf
      ? ` Lo escribiste el ${formatLongDate(profile.reportedAgeAsOf)}.`
      : "";
    return {
      primary: `${profile.reportedAge} años`,
      secondary: `Falta el día exacto de nacimiento.${when} Si naciste después de esta fecha, la edad ya pudo cambiar.`,
    };
  }
  return { primary: "Sin fecha", secondary: "Agrega tu fecha de nacimiento." };
}

export function relationshipLabel(profile: Profile, today: string): string | null {
  if (profile.civilStatus === "soltero") return "Soltero.";
  if (profile.civilStatus === "separado") {
    return profile.partnerName.trim()
      ? `Separado. Antes, con ${profile.partnerName.trim()}.`
      : "Separado.";
  }
  const verb =
    profile.civilStatus === "casado"
      ? "Casado con"
      : profile.civilStatus === "union_libre"
        ? "En unión libre con"
        : "En una relación con";
  const who = profile.partnerName.trim() || "alguien cuyo nombre falta";
  if (!profile.relationshipSince) return `${verb} ${who}.`;
  const span = elapsed(profile.relationshipSince, today);
  if (!span) return `${verb} ${who}.`;
  return `${verb} ${who} desde hace ${formatElapsed(span)}.`;
}

export function wealthOf(assets: Asset[], liabilities: Liability[]): Wealth {
  let assetsCop = 0;
  let unvaluedCount = 0;
  for (const asset of assets) {
    if (!asset.owned) continue;
    if (asset.valueCop == null) unvaluedCount += 1;
    else assetsCop += asset.valueCop;
  }
  let debtsCop = 0;
  let unconfirmedCount = 0;
  for (const debt of liabilities) {
    debtsCop += debt.balanceCop;
    if (!debt.confirmed) unconfirmedCount += 1;
  }
  return {
    assetsCop,
    unvaluedCount,
    debtsCop,
    netCop: assetsCop - debtsCop,
    unconfirmedCount,
  };
}

export function monthlyCosts(costs: { amountCop: number }[]): number {
  return costs.reduce((sum, cost) => sum + cost.amountCop, 0);
}

function average(values: number[]): number | null {
  if (values.length === 0) return null;
  const total = values.reduce((sum, value) => sum + value, 0);
  return Math.round((total / values.length) * 10) / 10;
}

export function summarizeLogs(logs: DailyLog[]): LogSummary {
  return {
    days: logs.length,
    studied: logs.filter((log) => log.studied).length,
    worked: logs.filter((log) => log.worked).length,
    incomeCop: logs.reduce((sum, log) => sum + log.incomeCop, 0),
    expenseCop: logs.reduce((sum, log) => sum + log.expenseCop, 0),
    avgHealth: average(logs.flatMap((log) => (log.health == null ? [] : [log.health]))),
    avgMood: average(logs.flatMap((log) => (log.mood == null ? [] : [log.mood]))),
    avgEnergy: average(logs.flatMap((log) => (log.energy == null ? [] : [log.energy]))),
    avgSleep: average(logs.flatMap((log) => (log.sleepHours == null ? [] : [log.sleepHours]))),
  };
}

export function lifeSentence(profile: Profile, wealth: Wealth, today: string): string {
  const age = ageLabel(profile, today);
  const place = profile.city.trim() || "una ciudad sin anotar";
  const parts = [`Tienes ${age.primary} y estás en ${place}.`];
  const relationship = relationshipLabel(profile, today);
  if (relationship) parts.push(relationship);

  if (profile.graduated) {
    parts.push(
      `Ya te graduaste${profile.program.trim() ? ` de ${profile.program.trim()}` : ""}${
        profile.school.trim() ? ` en ${profile.school.trim()}` : ""
      }.`,
    );
  } else if (profile.studying) {
    parts.push(
      `Estudias ${profile.program.trim() || "una carrera"}${
        profile.school.trim() ? ` en ${profile.school.trim()}` : ""
      } y todavía no te gradúas.`,
    );
  } else {
    parts.push("No estás estudiando y la ficha no te marca como graduado.");
  }

  if (profile.employed) {
    parts.push(
      `Trabajas${profile.jobTitle.trim() ? ` como ${profile.jobTitle.trim()}` : ""}${
        profile.employer.trim() ? ` en ${profile.employer.trim()}` : ""
      }. El salario anotado es ${formatCop(profile.salaryCop)} al mes.`,
    );
  } else {
    const since = profile.jobEndedOn ? ` desde el ${formatLongDate(profile.jobEndedOn)}` : "";
    parts.push(
      `No tienes empleo fijo${since}. El último cargo anotado es ${
        profile.jobTitle.trim() || "sin cargo"
      }${profile.employer.trim() ? ` en ${profile.employer.trim()}` : ""}.`,
    );
  }

  if (profile.otherIncomeCop > 0) {
    parts.push(`Otros ingresos: ${formatCop(profile.otherIncomeCop)} al mes.`);
  } else if (profile.otherWork.trim()) {
    parts.push("Tienes otros trabajos anotados, sin un ingreso fijo.");
  }

  const caveat =
    wealth.unconfirmedCount > 0 ? " La cifra incluye deudas que todavía no confirmaste con un extracto." : "";
  parts.push(`Patrimonio neto estimado: ${formatCop(wealth.netCop)}.${caveat}`);
  return parts.join(" ");
}

export function buildReport(input: {
  today: string;
  periodStart: string;
  periodEnd: string;
  profile: Profile;
  assets: Asset[];
  liabilities: Liability[];
  costs: { amountCop: number; id: number; name: string; note: string }[];
  logs: DailyLog[];
  milestones: Milestone[];
}): ReportBody {
  const wealth = wealthOf(input.assets, input.liabilities);
  const age = ageLabel(input.profile, input.today);
  const logs = input.logs
    .filter((log) => log.logDate >= input.periodStart && log.logDate <= input.periodEnd)
    .sort((a, b) => a.logDate.localeCompare(b.logDate));
  return {
    generatedOn: input.today,
    periodStart: input.periodStart,
    periodEnd: input.periodEnd,
    sentence: lifeSentence(input.profile, wealth, input.today),
    profile: input.profile,
    agePrimary: age.primary,
    ageSecondary: age.secondary,
    relationshipLabel: relationshipLabel(input.profile, input.today),
    assets: input.assets,
    liabilities: input.liabilities,
    costs: input.costs,
    wealth,
    monthlyCostsCop: monthlyCosts(input.costs),
    logs,
    logSummary: summarizeLogs(logs),
    milestones: [...input.milestones].sort((a, b) => b.happenedOn.localeCompare(a.happenedOn)),
  };
}

export function parseCop(input: string): number | null {
  const digits = input.replace(/[^\d]/g, "");
  if (digits === "") return null;
  const value = Number(digits);
  if (!Number.isSafeInteger(value) || value > 100_000_000_000) return null;
  return value;
}

export const KIND_LABEL: Record<Asset["kind"], string> = {
  equipo: "Equipo",
  vehiculo: "Vehículo",
  hogar: "Hogar",
  dinero: "Dinero",
  otro: "Otro",
};

export const CIVIL_LABEL: Record<Profile["civilStatus"], string> = {
  soltero: "Soltero",
  relacion: "En una relación",
  casado: "Casado",
  union_libre: "Unión libre",
  separado: "Separado",
};
