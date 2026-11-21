import { isIsoDate } from "./life";
import {
  ASSET_KINDS,
  CIVIL_STATUSES,
  LIQUIDATION_STATUSES,
  type Asset,
  type AssetKind,
  type CivilStatus,
  type Cost,
  type DailyLog,
  type Liability,
  type LiquidationStatus,
  type Milestone,
  type Profile,
} from "./types";

function record(value: unknown): Record<string, unknown> | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  return value as Record<string, unknown>;
}

function text(value: unknown, max: number, fallback: string): string {
  if (typeof value !== "string") return fallback;
  return value.trim().slice(0, max);
}

function flag(value: unknown, fallback: boolean): boolean {
  if (typeof value === "boolean") return value;
  return fallback;
}

function money(value: unknown, fallback: number): number {
  const number = typeof value === "number" ? value : typeof value === "string" ? Number(value) : NaN;
  if (!Number.isSafeInteger(number) || number < 0 || number > 100_000_000_000) return fallback;
  return number;
}

function moneyOrNull(value: unknown, fallback: number | null): number | null {
  if (value === null || value === "") return null;
  const number = typeof value === "number" ? value : typeof value === "string" ? Number(value) : NaN;
  if (!Number.isSafeInteger(number) || number < 0 || number > 100_000_000_000) return fallback;
  return number;
}

function day(value: unknown, fallback: string | null): string | null {
  if (value === null || value === "") return null;
  if (typeof value !== "string" || !isIsoDate(value)) return fallback;
  const year = Number(value.slice(0, 4));
  if (year < 1920 || year > 2100) return fallback;
  return value;
}

function score(value: unknown): number | null {
  if (value === null || value === "") return null;
  const number = typeof value === "number" ? value : Number(value);
  if (!Number.isInteger(number) || number < 1 || number > 5) return null;
  return number;
}

export function sanitizeProfile(input: unknown, previous: Profile): Profile {
  const source = record(input);
  if (!source) return previous;
  const civil = CIVIL_STATUSES.includes(source.civilStatus as CivilStatus)
    ? (source.civilStatus as CivilStatus)
    : previous.civilStatus;
  const liquidation = LIQUIDATION_STATUSES.includes(source.liquidationStatus as LiquidationStatus)
    ? (source.liquidationStatus as LiquidationStatus)
    : previous.liquidationStatus;
  const skills = Array.isArray(source.skills)
    ? source.skills
        .filter((item): item is string => typeof item === "string")
        .map((item) => item.trim())
        .filter((item) => item.length > 0)
        .slice(0, 12)
        .map((item) => item.slice(0, 40))
    : previous.skills;
  const fullName = text(source.fullName, 120, previous.fullName);
  const reported =
    source.reportedAge === null
      ? null
      : Number.isInteger(source.reportedAge) &&
          Number(source.reportedAge) >= 0 &&
          Number(source.reportedAge) <= 120
        ? Number(source.reportedAge)
        : previous.reportedAge;
  return {
    fullName: fullName.length >= 2 ? fullName : previous.fullName,
    birthDate: day(source.birthDate, previous.birthDate),
    reportedAge: reported,
    reportedAgeAsOf: day(source.reportedAgeAsOf, previous.reportedAgeAsOf),
    city: text(source.city, 120, previous.city),
    headline: text(source.headline, 180, previous.headline),
    photoCaption: text(source.photoCaption, 120, previous.photoCaption),
    civilStatus: civil,
    partnerName: text(source.partnerName, 120, previous.partnerName),
    relationshipSince: day(source.relationshipSince, previous.relationshipSince),
    civilNote: text(source.civilNote, 500, previous.civilNote),
    healthStatus: text(source.healthStatus, 120, previous.healthStatus),
    healthDetail: text(source.healthDetail, 2000, previous.healthDetail),
    studying: flag(source.studying, previous.studying),
    school: text(source.school, 180, previous.school),
    program: text(source.program, 180, previous.program),
    semester: text(source.semester, 80, previous.semester),
    studyNote: text(source.studyNote, 2000, previous.studyNote),
    graduated: flag(source.graduated, previous.graduated),
    graduationNote: text(source.graduationNote, 500, previous.graduationNote),
    employed: flag(source.employed, previous.employed),
    jobTitle: text(source.jobTitle, 180, previous.jobTitle),
    employer: text(source.employer, 180, previous.employer),
    jobEndedOn: day(source.jobEndedOn, previous.jobEndedOn),
    salaryCop: money(source.salaryCop, previous.salaryCop),
    lastSalaryCop: money(source.lastSalaryCop, previous.lastSalaryCop),
    salaryNote: text(source.salaryNote, 2000, previous.salaryNote),
    otherWork: text(source.otherWork, 2000, previous.otherWork),
    otherIncomeCop: money(source.otherIncomeCop, previous.otherIncomeCop),
    english: text(source.english, 300, previous.english),
    skills,
    focus: text(source.focus, 300, previous.focus),
    situationNote: text(source.situationNote, 1000, previous.situationNote),
    situationOpen: flag(source.situationOpen, previous.situationOpen),
    liquidationStatus: liquidation,
    liquidationExpectedCop: money(source.liquidationExpectedCop, previous.liquidationExpectedCop),
    liquidationExpectedOn: day(source.liquidationExpectedOn, previous.liquidationExpectedOn),
    liquidationReceivedCop: moneyOrNull(source.liquidationReceivedCop, previous.liquidationReceivedCop),
    reviewed: flag(source.reviewed, previous.reviewed),
    github: text(source.github, 80, previous.github),
    linkedin: text(source.linkedin, 120, previous.linkedin),
  };
}

export function sanitizeAsset(input: unknown): Omit<Asset, "id"> | null {
  const source = record(input);
  if (!source) return null;
  const name = text(source.name, 80, "");
  if (name.length < 2) return null;
  const kind = ASSET_KINDS.includes(source.kind as AssetKind) ? (source.kind as AssetKind) : "otro";
  return {
    name,
    kind,
    detail: text(source.detail, 400, ""),
    valueCop: moneyOrNull(source.valueCop, null),
    valueIsEstimate: flag(source.valueIsEstimate, true),
    owned: flag(source.owned, true),
    note: text(source.note, 800, ""),
  };
}

export function sanitizeLiability(input: unknown): Omit<Liability, "id"> | null {
  const source = record(input);
  if (!source) return null;
  const name = text(source.name, 120, "");
  if (name.length < 2) return null;
  return {
    name,
    balanceCop: money(source.balanceCop, 0),
    monthlyCop: moneyOrNull(source.monthlyCop, null),
    confirmed: flag(source.confirmed, false),
    note: text(source.note, 800, ""),
  };
}

export function sanitizeCost(input: unknown): Omit<Cost, "id"> | null {
  const source = record(input);
  if (!source) return null;
  const name = text(source.name, 80, "");
  if (name.length < 2) return null;
  return {
    name,
    amountCop: money(source.amountCop, 0),
    note: text(source.note, 400, ""),
  };
}

export function sanitizeMilestone(input: unknown): Omit<Milestone, "id"> | null {
  const source = record(input);
  if (!source) return null;
  const title = text(source.title, 140, "");
  const happenedOn = day(source.happenedOn, null);
  if (title.length < 2 || !happenedOn) return null;
  return { happenedOn, title, detail: text(source.detail, 800, "") };
}

export function sanitizeLog(input: unknown): Omit<DailyLog, "id"> | null {
  const source = record(input);
  if (!source) return null;
  const logDate = day(source.logDate, null);
  if (!logDate) return null;
  const sleep = source.sleepHours === null || source.sleepHours === "" ? null : Number(source.sleepHours);
  const sleepHours =
    sleep == null
      ? null
      : Number.isFinite(sleep) && sleep >= 0 && sleep <= 24
        ? Math.round(sleep * 10) / 10
        : null;
  return {
    logDate,
    health: score(source.health),
    energy: score(source.energy),
    mood: score(source.mood),
    sleepHours,
    studied: flag(source.studied, false),
    worked: flag(source.worked, false),
    incomeCop: money(source.incomeCop, 0),
    expenseCop: money(source.expenseCop, 0),
    note: text(source.note, 2000, ""),
  };
}

export function positiveId(value: unknown): number | null {
  const number = typeof value === "number" ? value : Number(value);
  if (!Number.isInteger(number) || number <= 0 || number > 1_000_000_000) return null;
  return number;
}
