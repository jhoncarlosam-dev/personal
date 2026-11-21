"use client";

import { useEffect, useState } from "react";
import { formatCop, formatLongDate, lastNDays } from "../lib/life";
import type { DailyLog, LifeState } from "../lib/types";

type Draft = Omit<DailyLog, "id">;

const empty = (date: string): Draft => ({
  logDate: date,
  health: null,
  energy: null,
  mood: null,
  sleepHours: null,
  studied: false,
  worked: false,
  incomeCop: 0,
  expenseCop: 0,
  note: "",
});

export function DailySection({
  state,
  saving,
  onSave,
  onDelete,
}: {
  state: LifeState;
  saving: boolean;
  onSave: (log: Draft) => void;
  onDelete: (logDate: string) => void;
}) {
  const [draft, setDraft] = useState<Draft>(empty(state.today));

  useEffect(() => {
    const found = state.logs.find((log) => log.logDate === draft.logDate);
    if (!found) return;
    setDraft({
      logDate: found.logDate,
      health: found.health,
      energy: found.energy,
      mood: found.mood,
      sleepHours: found.sleepHours,
      studied: found.studied,
      worked: found.worked,
      incomeCop: found.incomeCop,
      expenseCop: found.expenseCop,
      note: found.note,
    });
  }, [draft.logDate, state.logs]);

  const days = lastNDays(state.today, 14);
  const byDate = new Map(state.logs.map((log) => [log.logDate, log]));
  const hasMood = days.some((day) => byDate.get(day)?.mood != null);

  return (
    <section className="section" id="hoy">
      <div className="section-head">
        <div>
          <p className="kicker">Seguimiento</p>
          <h2>El día</h2>
        </div>
      </div>
      <form
        className="panel"
        onSubmit={(event) => {
          event.preventDefault();
          onSave(draft);
        }}
      >
        <div className="daily">
          <label className="field">
            <span>Fecha</span>
            <input
              type="date"
              value={draft.logDate}
              onChange={(event) => {
                const logDate = event.target.value;
                const found = state.logs.find((log) => log.logDate === logDate);
                setDraft(found ? { ...found } : empty(logDate || state.today));
              }}
            />
          </label>
          <div>
            <Scale label="Cuerpo" value={draft.health} onChange={(health) => setDraft({ ...draft, health })} />
            <Scale label="Ánimo" value={draft.mood} onChange={(mood) => setDraft({ ...draft, mood })} />
            <Scale label="Energía" value={draft.energy} onChange={(energy) => setDraft({ ...draft, energy })} />
          </div>
        </div>
        <div className="grid-form" style={{ marginTop: 12 }}>
          <label className="field">
            <span>Horas de sueño</span>
            <input
              inputMode="decimal"
              value={draft.sleepHours ?? ""}
              onChange={(event) => {
                const raw = event.target.value.replace(",", ".");
                setDraft({ ...draft, sleepHours: raw === "" ? null : Number(raw) });
              }}
            />
          </label>
          <label className="field">
            <span>Ingresos del día</span>
            <input
              inputMode="numeric"
              value={String(draft.incomeCop)}
              onChange={(event) => setDraft({ ...draft, incomeCop: Number(event.target.value.replace(/[^\d]/g, "") || 0) })}
            />
          </label>
          <label className="field">
            <span>Gastos del día</span>
            <input
              inputMode="numeric"
              value={String(draft.expenseCop)}
              onChange={(event) => setDraft({ ...draft, expenseCop: Number(event.target.value.replace(/[^\d]/g, "") || 0) })}
            />
          </label>
          <div className="row" style={{ alignItems: "end" }}>
            <label className="check">
              <input type="checkbox" checked={draft.studied} onChange={(event) => setDraft({ ...draft, studied: event.target.checked })} />
              Estudié
            </label>
            <label className="check">
              <input type="checkbox" checked={draft.worked} onChange={(event) => setDraft({ ...draft, worked: event.target.checked })} />
              Trabajé
            </label>
          </div>
          <label className="field wide">
            <span>Qué pasó</span>
            <textarea value={draft.note} onChange={(event) => setDraft({ ...draft, note: event.target.value })} />
          </label>
        </div>
        <button className="primary" type="submit" disabled={saving} style={{ marginTop: 12 }}>
          {saving ? "Guardando…" : "Guardar el día"}
        </button>
      </form>

      {hasMood ? (
        <figure>
          <figcaption className="kicker" style={{ marginTop: 18 }}>Ánimo de los últimos 14 días</figcaption>
          <div className="bars" role="img" aria-label="Ánimo diario del 1 al 5">
            {days.map((day) => {
              const mood = byDate.get(day)?.mood;
              return (
                <div
                  key={day}
                  className={mood == null ? "bar empty" : "bar"}
                  style={{ height: mood == null ? "2px" : `${mood * 20}%` }}
                  title={`${formatLongDate(day)}: ${mood == null ? "sin registro" : mood}`}
                />
              );
            })}
          </div>
          <div className="bar-labels"><span>{formatLongDate(days[0])}</span><span>{formatLongDate(days[days.length - 1])}</span></div>
          <p className="axis">Eje vertical: ánimo de 1 a 5. Los días sin registro quedan en la base. Fuente: los días que guardas aquí.</p>
        </figure>
      ) : null}

      <div className="log-list">
        {state.logs.length === 0 ? <p className="hint">Todavía no hay días. El primero puede ser hoy.</p> : null}
        {state.logs.map((log) => (
          <article className="log" key={log.id}>
            <div>
              <strong>{formatLongDate(log.logDate)}</strong>
              <div className="hint">Cuerpo {log.health ?? "—"} · Ánimo {log.mood ?? "—"} · Sueño {log.sleepHours ?? "—"}</div>
            </div>
            <div>
              <div>{log.studied ? "Estudió" : "No estudió"} · {log.worked ? "Trabajó" : "No trabajó"}</div>
              <div className="hint">Entró {formatCop(log.incomeCop)} · salió {formatCop(log.expenseCop)}</div>
              {log.note ? <p style={{ margin: "6px 0 0" }}>{log.note}</p> : null}
            </div>
            <button
              className="quiet"
              type="button"
              onClick={() => {
                if (window.confirm("¿Borrar este día?")) onDelete(log.logDate);
              }}
            >
              Borrar
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

function Scale({ label, value, onChange }: { label: string; value: number | null; onChange: (value: number) => void }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
      <span className="hint" style={{ width: 70 }}>{label}</span>
      <div className="scale" role="group" aria-label={label}>
        {[1, 2, 3, 4, 5].map((score) => (
          <button key={score} type="button" aria-pressed={value === score} onClick={() => onChange(score)}>
            {score}
          </button>
        ))}
      </div>
    </div>
  );
}
