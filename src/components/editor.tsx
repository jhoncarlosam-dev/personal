"use client";

import { useEffect, useRef, useState } from "react";
import type { Profile } from "../lib/types";
import { CIVIL_LABEL } from "../lib/life";
import { AreaField, CheckField, DateField, MoneyField, TextField } from "./fields";

export function Editor({
  profile,
  open,
  saving,
  onClose,
  onSave,
}: {
  profile: Profile;
  open: boolean;
  saving: boolean;
  onClose: () => void;
  onSave: (profile: Profile) => void;
}) {
  const [draft, setDraft] = useState(profile);
  const [skills, setSkills] = useState(profile.skills.join(", "));
  const wasOpen = useRef(false);

  useEffect(() => {
    if (open && !wasOpen.current) {
      setDraft(profile);
      setSkills(profile.skills.join(", "));
    }
    wasOpen.current = open;
  }, [open, profile]);

  if (!open) return null;

  function set<K extends keyof Profile>(key: K, value: Profile[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  return (
    <form
      className="panel"
      id="editar"
      onSubmit={(event) => {
        event.preventDefault();
        onSave({
          ...draft,
          skills: skills.split(",").map((item) => item.trim()).filter(Boolean),
          reviewed: true,
        });
      }}
    >
      <div className="section-head">
        <h2>Actualizar mi punto</h2>
        <button className="quiet" type="button" onClick={onClose}>Cerrar</button>
      </div>
      <div className="grid-form">
        <TextField label="Nombre" value={draft.fullName} onChange={(value) => set("fullName", value)} />
        <DateField label="Fecha de nacimiento" value={draft.birthDate} onChange={(value) => set("birthDate", value)} />
        <TextField label="Ciudad" value={draft.city} onChange={(value) => set("city", value)} />
        <TextField label="Frase" value={draft.headline} onChange={(value) => set("headline", value)} />
        <TextField label="Pie de la foto" value={draft.photoCaption} onChange={(value) => set("photoCaption", value)} wide />
        <label className="field">
          <span>Estado civil</span>
          <select value={draft.civilStatus} onChange={(event) => set("civilStatus", event.target.value as Profile["civilStatus"])}>
            {Object.entries(CIVIL_LABEL).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
        <TextField label="Pareja" value={draft.partnerName} onChange={(value) => set("partnerName", value)} />
        <DateField label="Juntos desde" value={draft.relationshipSince} onChange={(value) => set("relationshipSince", value)} />
        <AreaField label="Nota del estado civil" value={draft.civilNote} onChange={(value) => set("civilNote", value)} />
        <CheckField label="Estoy estudiando" checked={draft.studying} onChange={(value) => set("studying", value)} />
        <CheckField label="Ya me gradué de la ingeniería" checked={draft.graduated} onChange={(value) => set("graduated", value)} />
        <TextField label="Universidad" value={draft.school} onChange={(value) => set("school", value)} />
        <TextField label="Programa" value={draft.program} onChange={(value) => set("program", value)} />
        <TextField label="Semestre" value={draft.semester} onChange={(value) => set("semester", value)} />
        <AreaField label="Nota de estudio" value={draft.studyNote} onChange={(value) => set("studyNote", value)} />
        <AreaField label="Nota de la graduación" value={draft.graduationNote} onChange={(value) => set("graduationNote", value)} />
        <CheckField label="Tengo trabajo" checked={draft.employed} onChange={(value) => set("employed", value)} />
        <TextField label="Cargo" value={draft.jobTitle} onChange={(value) => set("jobTitle", value)} />
        <TextField label="Dónde" value={draft.employer} onChange={(value) => set("employer", value)} />
        <DateField label="El empleo terminó" value={draft.jobEndedOn} onChange={(value) => set("jobEndedOn", value)} />
        <MoneyField label="Salario mensual" value={draft.salaryCop} onChange={(value) => set("salaryCop", value ?? 0)} />
        <MoneyField label="Último salario que sí tuve" value={draft.lastSalaryCop} onChange={(value) => set("lastSalaryCop", value ?? 0)} />
        <AreaField label="Nota del salario" value={draft.salaryNote} onChange={(value) => set("salaryNote", value)} />
        <AreaField label="Otros trabajos" value={draft.otherWork} onChange={(value) => set("otherWork", value)} />
        <MoneyField label="Otros ingresos al mes" value={draft.otherIncomeCop} onChange={(value) => set("otherIncomeCop", value ?? 0)} />
        <TextField label="Salud, en una frase" value={draft.healthStatus} onChange={(value) => set("healthStatus", value)} />
        <AreaField label="Salud, en detalle" value={draft.healthDetail} onChange={(value) => set("healthDetail", value)} />
        <TextField label="Inglés" value={draft.english} onChange={(value) => set("english", value)} wide />
        <TextField label="Habilidades, separadas por coma" value={skills} onChange={setSkills} wide />
        <TextField label="Enfoque" value={draft.focus} onChange={(value) => set("focus", value)} wide />
        <AreaField label="Dónde estoy viviendo" value={draft.situationNote} onChange={(value) => set("situationNote", value)} />
        <CheckField label="Esta nota de ciudad sigue pendiente" checked={draft.situationOpen} onChange={(value) => set("situationOpen", value)} />
      </div>
      <div className="row" style={{ marginTop: 16 }}>
        <button className="primary" type="submit" disabled={saving}>{saving ? "Guardando…" : "Guardar este punto"}</button>
      </div>
    </form>
  );
}
