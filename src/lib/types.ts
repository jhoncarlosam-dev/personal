export const CIVIL_STATUSES = [
  "soltero",
  "relacion",
  "casado",
  "union_libre",
  "separado",
] as const;

export type CivilStatus = (typeof CIVIL_STATUSES)[number];

export const LIQUIDATION_STATUSES = ["por_confirmar", "recibida", "otro", "no_llego"] as const;
export type LiquidationStatus = (typeof LIQUIDATION_STATUSES)[number];

export const ASSET_KINDS = ["equipo", "vehiculo", "hogar", "dinero", "otro"] as const;
export type AssetKind = (typeof ASSET_KINDS)[number];

export type Profile = {
  fullName: string;
  birthDate: string | null;
  reportedAge: number | null;
  reportedAgeAsOf: string | null;
  city: string;
  headline: string;
  photoCaption: string;
  civilStatus: CivilStatus;
  partnerName: string;
  relationshipSince: string | null;
  civilNote: string;
  healthStatus: string;
  healthDetail: string;
  studying: boolean;
  school: string;
  program: string;
  semester: string;
  studyNote: string;
  graduated: boolean;
  graduationNote: string;
  employed: boolean;
  jobTitle: string;
  employer: string;
  jobEndedOn: string | null;
  salaryCop: number;
  lastSalaryCop: number;
  salaryNote: string;
  otherWork: string;
  otherIncomeCop: number;
  english: string;
  skills: string[];
  focus: string;
  situationNote: string;
  situationOpen: boolean;
  liquidationStatus: LiquidationStatus;
  liquidationExpectedCop: number;
  liquidationExpectedOn: string | null;
  liquidationReceivedCop: number | null;
  reviewed: boolean;
  github: string;
  linkedin: string;
};

export type Asset = {
  id: number;
  name: string;
  kind: AssetKind;
  detail: string;
  valueCop: number | null;
  valueIsEstimate: boolean;
  owned: boolean;
  note: string;
};

export type Liability = {
  id: number;
  name: string;
  balanceCop: number;
  monthlyCop: number | null;
  confirmed: boolean;
  note: string;
};

export type Cost = {
  id: number;
  name: string;
  amountCop: number;
  note: string;
};

export type DailyLog = {
  id: number;
  logDate: string;
  health: number | null;
  energy: number | null;
  mood: number | null;
  sleepHours: number | null;
  studied: boolean;
  worked: boolean;
  incomeCop: number;
  expenseCop: number;
  note: string;
};

export type Milestone = {
  id: number;
  happenedOn: string;
  title: string;
  detail: string;
};

export type ReportSummary = {
  id: number;
  title: string;
  periodStart: string | null;
  periodEnd: string | null;
  createdAt: string;
};

export type LifeState = {
  today: string;
  profile: Profile;
  assets: Asset[];
  liabilities: Liability[];
  costs: Cost[];
  logs: DailyLog[];
  milestones: Milestone[];
  reports: ReportSummary[];
  hasPortrait: boolean;
};

export type Wealth = {
  assetsCop: number;
  unvaluedCount: number;
  debtsCop: number;
  unconfirmedCount: number;
  netCop: number;
};

export type LogSummary = {
  days: number;
  studied: number;
  worked: number;
  incomeCop: number;
  expenseCop: number;
  avgHealth: number | null;
  avgMood: number | null;
  avgEnergy: number | null;
  avgSleep: number | null;
};

export type ReportBody = {
  generatedOn: string;
  periodStart: string;
  periodEnd: string;
  sentence: string;
  profile: Profile;
  agePrimary: string;
  ageSecondary: string;
  relationshipLabel: string | null;
  assets: Asset[];
  liabilities: Liability[];
  costs: Cost[];
  wealth: Wealth;
  monthlyCostsCop: number;
  logs: DailyLog[];
  logSummary: LogSummary;
  milestones: Milestone[];
};
