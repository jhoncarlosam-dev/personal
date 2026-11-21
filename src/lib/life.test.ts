import assert from "node:assert/strict";
import test from "node:test";
import {
  ageLabel,
  bogotaToday,
  buildReport,
  elapsed,
  formatCop,
  formatElapsed,
  lastNDays,
  lifeSentence,
  monthStart,
  parseCop,
  relationshipLabel,
  summarizeLogs,
  wealthOf,
} from "./life";
import type { Asset, Liability, Profile } from "./types";

const profile: Profile = {
  fullName: "Jhon Carlos Acevedo Mendoza",
  birthDate: null,
  reportedAge: 27,
  reportedAgeAsOf: "2026-07-19",
  city: "Cúcuta, Norte de Santander",
  headline: "",
  photoCaption: "",
  civilStatus: "relacion",
  partnerName: "Katerine Orjuela",
  relationshipSince: "2026-07-20",
  civilNote: "",
  healthStatus: "En seguimiento",
  healthDetail: "",
  studying: true,
  school: "UNAD",
  program: "Ingeniería de Sistemas",
  semester: "2026-2",
  studyNote: "",
  graduated: false,
  graduationNote: "",
  employed: false,
  jobTitle: "Analista de calidad de software",
  employer: "Nelumbo Consultores",
  jobEndedOn: "2026-11-06",
  salaryCop: 0,
  lastSalaryCop: 2100000,
  salaryNote: "",
  otherWork: "Freelance",
  otherIncomeCop: 0,
  english: "",
  skills: [],
  focus: "",
  situationNote: "",
  situationOpen: true,
  liquidationStatus: "por_confirmar",
  liquidationExpectedCop: 6841150,
  liquidationExpectedOn: "2026-11-12",
  liquidationReceivedCop: null,
  reviewed: false,
  github: "",
  linkedin: "",
};

test("bogota date stays on the previous evening", () => {
  assert.equal(bogotaToday(new Date("2026-11-22T04:30:00.000Z")), "2026-11-21");
  assert.equal(bogotaToday(new Date("2026-11-22T05:00:00.000Z")), "2026-11-22");
});

test("elapsed counts the relationship through 21 nov", () => {
  assert.deepEqual(elapsed("2026-07-20", "2026-11-21"), { years: 0, months: 4, days: 1 });
  assert.equal(formatElapsed({ years: 0, months: 4, days: 1 }), "4 meses y 1 día");
  assert.equal(lastNDays("2026-11-21", 3).join(","), "2026-11-19,2026-11-20,2026-11-21");
  assert.equal(monthStart("2026-11-21"), "2026-11-01");
});

test("age stays at the reported 27 until a birthday is set", () => {
  const label = ageLabel(profile, "2026-11-21");
  assert.equal(label.primary, "27 años");
  assert.match(label.secondary, /19 de julio de 2026/);
  const born = ageLabel({ ...profile, birthDate: "1999-01-15" }, "2026-11-21");
  assert.equal(born.primary, "27 años y 10 meses");
});

test("money and net worth use the seeded estimates", () => {
  assert.equal(parseCop("2.100.000"), 2100000);
  assert.equal(parseCop(""), null);
  assert.match(formatCop(2100000), /2\.100\.000/);
  const assets: Asset[] = [
    { id: 1, name: "Laptop", kind: "equipo", detail: "", valueCop: 1700000, valueIsEstimate: true, owned: true, note: "" },
    { id: 2, name: "Moto", kind: "vehiculo", detail: "", valueCop: 8500000, valueIsEstimate: true, owned: true, note: "" },
    { id: 3, name: "Monitor", kind: "equipo", detail: "", valueCop: 550000, valueIsEstimate: true, owned: true, note: "" },
    { id: 4, name: "Celular", kind: "equipo", detail: "", valueCop: 250000, valueIsEstimate: true, owned: true, note: "" },
    { id: 5, name: "Auriculares", kind: "equipo", detail: "", valueCop: 280000, valueIsEstimate: true, owned: true, note: "" },
    { id: 6, name: "Nevera", kind: "hogar", detail: "", valueCop: null, valueIsEstimate: true, owned: true, note: "" },
    { id: 7, name: "Teclado", kind: "equipo", detail: "", valueCop: 80000, valueIsEstimate: true, owned: true, note: "" },
    { id: 8, name: "Mouse", kind: "equipo", detail: "", valueCop: 40000, valueIsEstimate: true, owned: true, note: "" },
    { id: 9, name: "Parlante", kind: "equipo", detail: "", valueCop: 150000, valueIsEstimate: true, owned: true, note: "" },
    { id: 10, name: "Cascos", kind: "vehiculo", detail: "", valueCop: 350000, valueIsEstimate: true, owned: true, note: "" },
    { id: 11, name: "Efectivo", kind: "dinero", detail: "", valueCop: null, valueIsEstimate: false, owned: true, note: "" },
  ];
  const debts: Liability[] = [
    { id: 1, name: "Moto", balanceCop: 9771842, monthlyCop: 354000, confirmed: false, note: "" },
    { id: 2, name: "Tarjeta", balanceCop: 2100000, monthlyCop: null, confirmed: false, note: "" },
    { id: 3, name: "Anderson", balanceCop: 1000000, monthlyCop: null, confirmed: false, note: "" },
    { id: 4, name: "David", balanceCop: 13000, monthlyCop: null, confirmed: false, note: "" },
  ];
  const wealth = wealthOf(assets, debts);
  assert.equal(wealth.assetsCop, 11900000);
  assert.equal(wealth.debtsCop, 12884842);
  assert.equal(wealth.netCop, -984842);
  assert.equal(wealth.unvaluedCount, 2);
  assert.equal(wealth.unconfirmedCount, 4);
});

test("the life sentence answers the status questions", () => {
  const sentence = lifeSentence(
    profile,
    { assetsCop: 11900000, debtsCop: 12884842, netCop: -984842, unvaluedCount: 2, unconfirmedCount: 4 },
    "2026-11-21",
  );
  assert.match(sentence, /27 años/);
  assert.match(sentence, /Cúcuta/);
  assert.match(sentence, /Katerine Orjuela/);
  assert.match(sentence, /4 meses y 1 día/);
  assert.match(sentence, /Ingeniería de Sistemas/);
  assert.match(sentence, /todavía no te gradúas/);
  assert.match(sentence, /No tienes empleo fijo/);
  assert.match(sentence, /6 de noviembre de 2026/);
  assert.match(relationshipLabel(profile, "2026-11-21") ?? "", /relación/);
});

test("a report averages only the days inside the period", () => {
  const report = buildReport({
    today: "2026-11-21",
    periodStart: "2026-11-01",
    periodEnd: "2026-11-21",
    profile,
    assets: [],
    liabilities: [],
    costs: [{ id: 1, name: "Arriendo", amountCop: 600000, note: "" }],
    logs: [
      {
        id: 1,
        logDate: "2026-10-02",
        health: 1,
        energy: 1,
        mood: 1,
        sleepHours: 4,
        studied: false,
        worked: false,
        incomeCop: 0,
        expenseCop: 0,
        note: "",
      },
      {
        id: 2,
        logDate: "2026-11-21",
        health: 4,
        energy: 3,
        mood: 5,
        sleepHours: 7,
        studied: true,
        worked: false,
        incomeCop: 0,
        expenseCop: 12000,
        note: "Día honesto",
      },
    ],
    milestones: [],
  });
  assert.equal(report.logSummary.days, 1);
  assert.equal(report.logSummary.studied, 1);
  assert.equal(report.logSummary.avgMood, 5);
  assert.equal(report.monthlyCostsCop, 600000);
  assert.equal(summarizeLogs(report.logs).expenseCop, 12000);
});
