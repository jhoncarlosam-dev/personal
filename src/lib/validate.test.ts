import assert from "node:assert/strict";
import test from "node:test";
import { sanitizeLog, sanitizeProfile } from "./validate";
import type { Profile } from "./types";

const previous = {
  fullName: "Jhon Carlos Acevedo Mendoza",
  birthDate: null,
  reportedAge: 27,
  reportedAgeAsOf: "2026-07-19",
  city: "Cúcuta",
  headline: "",
  photoCaption: "",
  civilStatus: "relacion",
  partnerName: "Katerine",
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
  jobTitle: "QA",
  employer: "Nelumbo",
  jobEndedOn: "2026-11-06",
  salaryCop: 0,
  lastSalaryCop: 2100000,
  salaryNote: "",
  otherWork: "",
  otherIncomeCop: 0,
  english: "",
  skills: ["Node.js"],
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
} satisfies Profile;

test("profile edits keep a bad field from wiping the name", () => {
  const next = sanitizeProfile(
    { fullName: "J", salaryCop: 2400000, employed: true, birthDate: "1999-02-31", city: "Arboledas" },
    previous,
  );
  assert.equal(next.fullName, previous.fullName);
  assert.equal(next.salaryCop, 2400000);
  assert.equal(next.employed, true);
  assert.equal(next.birthDate, null);
  assert.equal(next.city, "Arboledas");
});

test("a daily log rejects a score outside 1 to 5", () => {
  const log = sanitizeLog({
    logDate: "2026-11-21",
    health: 8,
    mood: 4,
    energy: 2,
    sleepHours: 7.25,
    studied: true,
    worked: false,
    incomeCop: 0,
    expenseCop: 3500,
    note: "  orden  ",
  });
  assert.equal(log?.health, null);
  assert.equal(log?.mood, 4);
  assert.equal(log?.sleepHours, 7.3);
  assert.equal(log?.note, "orden");
  assert.equal(sanitizeLog({ logDate: "no-es-fecha" }), null);
});
