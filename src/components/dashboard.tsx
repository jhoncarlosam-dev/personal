"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { DailySection } from "./daily";
import { Editor } from "./editor";
import { WealthSection } from "./wealth";
import {
  CIVIL_LABEL,
  ageLabel,
  formatCop,
  formatLongDate,
  formatStamp,
  lifeSentence,
  monthStart,
  monthlyCosts,
  relationshipLabel,
  wealthOf,
} from "../lib/life";
import type { LifeState, Profile } from "../lib/types";

export function Dashboard({ initial, simulated }: { initial: LifeState; simulated: boolean }) {
  const router = useRouter();
  const [state, setState] = useState(initial);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [photoVersion, setPhotoVersion] = useState(1);
  const [periodStart, setPeriodStart] = useState(monthStart(initial.today));
  const [periodEnd, setPeriodEnd] = useState(initial.today);
  const [milestone, setMilestone] = useState({ happenedOn: initial.today, title: "", detail: "" });

  const { profile } = state;
  const wealth = wealthOf(state.assets, state.liabilities);
  const age = ageLabel(profile, state.today);
  const fixed = monthlyCosts(state.costs);
  const deadline = state.today >= "2026-11-22" && !profile.employed && profile.situationOpen;

  async function commit(action: string, payload: Record<string, unknown>) {
    setSaving(true);
    setError(null);
    try {
      const response = await fetch("/api/state", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ action, ...payload }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof data.error === "string" ? data.error : "No se pudo guardar.");
      setState(data.state as LifeState);
      return data as { state: LifeState; id?: number };
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "No se pudo guardar.");
      return null;
    } finally {
      setSaving(false);
    }
  }

  async function onPhoto(file: File | undefined) {
    if (!file) return;
    if (file.size > 1_500_000) {
      setError("La foto pasa de 1,5 MB.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const form = new FormData();
      form.set("file", file);
      const response = await fetch("/api/portrait", { method: "POST", body: form });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof data.error === "string" ? data.error : "No pude guardar la foto.");
      setState(data.state as LifeState);
      setPhotoVersion((version) => version + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "No pude guardar la foto.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="page">
      <header id="punto">
        <p className="kicker">Punto de vida · {formatLongDate(state.today)} · hora de Colombia</p>
        <h1>{profile.fullName}</h1>
        <p className="headline">{profile.headline}</p>
        {simulated ? (
          <p className="sim">
            Estás viendo una sesión local de prueba. Los datos salen de tu CV y de tu diario; cuando la publiques en privado, entras con tu cuenta.
          </p>
        ) : null}
      </header>

      <nav className="topnav no-print" aria-label="Secciones">
        <a href="#punto">Punto</a>
        <a href="#hoy">Hoy</a>
        <a href="#cosas">Cosas</a>
        <a href="#hitos">Hitos</a>
        <a href="#reportes">Reportes</a>
      </nav>

      {error ? <p className="error" role="alert">{error}</p> : null}

      <section className="hero">
        <figure className="frame">
          {state.hasPortrait ? (
            <img src={`/api/portrait?v=${photoVersion}`} alt={`${profile.fullName}, retrato sentado con camisa de rayas y gafas`} />
          ) : (
            <div className="monogram" aria-hidden="true">JC</div>
          )}
          <figcaption>
            <span>{profile.photoCaption || "Foto"}</span>
            <label className="file">
              Cambiar
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  void onPhoto(file);
                  event.target.value = "";
                }}
              />
            </label>
          </figcaption>
        </figure>
        <div>
          <p className="lead">{lifeSentence(profile, wealth, state.today)}</p>
          <div className="stats">
            <Stat tone="olive" kicker="¿Cuánto patrimonio tengo?" value={formatCop(wealth.netCop)} detail={`${formatCop(wealth.assetsCop)} en cosas menos ${formatCop(wealth.debtsCop)} en deudas. ${wealth.unconfirmedCount} deudas siguen sin confirmar.`} />
            <Stat kicker="¿Cuántos años tengo?" value={age.primary} detail={age.secondary} />
            <Stat kicker="¿Cuál es mi estado civil?" value={CIVIL_LABEL[profile.civilStatus]} detail={[relationshipLabel(profile, state.today), profile.civilNote].filter(Boolean).join(" ")} />
            <Stat kicker="¿Estoy estudiando?" value={profile.studying ? "Sí, en la UNAD" : "No"} detail={profile.studying ? `${profile.program} · ${profile.semester}` : "No hay matrícula anotada."} />
            <Stat kicker="¿Ya me gradué de la ingeniería?" value={profile.graduated ? "Sí" : "Todavía no"} detail={profile.graduationNote} />
            <Stat
              tone={profile.employed ? undefined : "clay"}
              kicker="¿Tengo trabajo y cuánto gano?"
              value={profile.employed ? formatCop(profile.salaryCop) : "Sin empleo"}
              detail={
                profile.employed
                  ? `${profile.jobTitle} · ${profile.employer}.`
                  : `Sin empleo${profile.jobEndedOn ? ` desde el ${formatLongDate(profile.jobEndedOn)}` : ""}. Antes, ${profile.jobTitle} en ${profile.employer}. Último salario anotado: ${formatCop(profile.lastSalaryCop)}.`
              }
            />
            <Stat kicker="¿Tengo otros trabajos?" value={profile.otherIncomeCop > 0 ? formatCop(profile.otherIncomeCop) : "Sin ingreso fijo"} detail={profile.otherWork} />
            <Stat kicker="¿Cómo está mi salud?" value={profile.healthStatus || "Sin anotar"} detail={profile.healthDetail} />
            <Stat kicker="¿Cuánto pide el mes?" value={formatCop(fixed)} detail={state.costs.map((cost) => `${cost.name} ${formatCop(cost.amountCop)}`).join(" · ")} />
          </div>
          {profile.skills.length > 0 ? (
            <div className="chips" aria-label="Habilidades">
              {profile.skills.map((skill) => <span className="chip" key={skill}>{skill}</span>)}
            </div>
          ) : null}
          {profile.english ? <p className="hint">{profile.english}</p> : null}
          <div className="row" style={{ marginTop: 16 }}>
            <button type="button" onClick={() => setEditing((open) => !open)}>
              {editing ? "Cerrar el formulario" : "Actualizar mi punto"}
            </button>
          </div>
        </div>
      </section>

      <Editor
        profile={profile}
        open={editing}
        saving={saving}
        onClose={() => setEditing(false)}
        onSave={(next: Profile) => {
          void commit("profile", { profile: next }).then((result) => {
            if (result) setEditing(false);
          });
        }}
      />

      {!profile.reviewed ? (
        <aside className="banner">
          <p>
            Esta lectura sale del CV y del diario, con corte el 14 de noviembre de 2026. La edad exacta, el efectivo, la tarjeta y si sigues en Cúcuta hay que confirmarlos.
          </p>
          <button type="button" onClick={() => setEditing(true)}>Revisar y corregir</button>
        </aside>
      ) : null}

      {profile.situationOpen && profile.situationNote ? (
        <aside className={deadline ? "banner urgent" : "banner"}>
          <p>{profile.situationNote}</p>
          <button
            type="button"
            disabled={saving}
            onClick={() => commit("profile", { profile: { ...profile, situationOpen: false, reviewed: true } })}
          >
            Ya actualicé dónde estoy
          </button>
        </aside>
      ) : null}

      {profile.liquidationStatus === "por_confirmar" ? (
        <aside className="banner">
          <p>
            Liquidación de Nelumbo: {formatCop(profile.liquidationExpectedCop)}, prevista para el {profile.liquidationExpectedOn ? formatLongDate(profile.liquidationExpectedOn) : "12 de noviembre"}. No está sumada al patrimonio.
          </p>
          <div className="row">
            <button type="button" disabled={saving} onClick={() => commit("liquidation", { status: "recibida" })}>
              Llegó y eso es lo que tengo en cuentas
            </button>
            <button type="button" disabled={saving} onClick={() => commit("liquidation", { status: "no_llego" })}>
              Todavía no llega
            </button>
            <a href="#cosas">El saldo es otro: lo anoto en efectivo</a>
          </div>
        </aside>
      ) : null}

      <details className="panel">
        <summary>Salario, estudio y enfoque, completos</summary>
        <p>{profile.salaryNote}</p>
        <p>{profile.studyNote}</p>
        <p>{profile.focus}</p>
        <p className="hint">GitHub {profile.github} · LinkedIn {profile.linkedin}</p>
      </details>

      <DailySection
        state={state}
        saving={saving}
        onSave={(log) => void commit("log.upsert", { log })}
        onDelete={(logDate) => void commit("log.delete", { logDate })}
      />

      <WealthSection state={state} saving={saving} onAction={(action, payload) => void commit(action, payload)} />

      <section className="section" id="hitos">
        <div className="section-head">
          <div>
            <p className="kicker">Historia</p>
            <h2>Hitos</h2>
          </div>
        </div>
        <form
          className="grid-form panel"
          onSubmit={(event) => {
            event.preventDefault();
            void commit("milestone.create", { milestone }).then((result) => {
              if (result) setMilestone({ happenedOn: state.today, title: "", detail: "" });
            });
          }}
        >
          <label className="field">
            <span>Fecha</span>
            <input type="date" value={milestone.happenedOn} onChange={(event) => setMilestone({ ...milestone, happenedOn: event.target.value })} />
          </label>
          <label className="field">
            <span>Qué pasó</span>
            <input value={milestone.title} onChange={(event) => setMilestone({ ...milestone, title: event.target.value })} />
          </label>
          <label className="field wide">
            <span>Detalle</span>
            <input value={milestone.detail} onChange={(event) => setMilestone({ ...milestone, detail: event.target.value })} />
          </label>
          <button className="primary" type="submit" disabled={saving}>Agregar hito</button>
        </form>
        <ol className="timeline">
          {state.milestones.map((item) => (
            <li key={item.id}>
              <span className="when">{formatLongDate(item.happenedOn)}</span>
              <div>
                <strong>{item.title}</strong>
                {item.detail ? <p style={{ margin: "4px 0 0" }}>{item.detail}</p> : null}
              </div>
              <button className="quiet" type="button" onClick={() => {
                if (window.confirm("¿Quitar este hito?")) void commit("milestone.delete", { id: item.id });
              }}>Quitar</button>
            </li>
          ))}
        </ol>
      </section>

      <section className="section" id="reportes">
        <div className="section-head">
          <div>
            <p className="kicker">Reportes</p>
            <h2>El punto, en un documento</h2>
          </div>
        </div>
        <p className="hint">El reporte congela las cifras de este momento y los días del rango. Si luego corriges un saldo, el reporte viejo no cambia.</p>
        <div className="row" style={{ margin: "12px 0" }}>
          <label className="field">
            <span>Desde</span>
            <input type="date" value={periodStart} onChange={(event) => setPeriodStart(event.target.value)} />
          </label>
          <label className="field">
            <span>Hasta</span>
            <input type="date" value={periodEnd} onChange={(event) => setPeriodEnd(event.target.value)} />
          </label>
          <button
            className="primary"
            type="button"
            disabled={saving}
            onClick={() => {
              void commit("report.create", { periodStart, periodEnd }).then((result) => {
                if (result?.id) router.push(`/reporte/${result.id}`);
              });
            }}
          >
            Generar reporte
          </button>
          <button type="button" disabled={saving} onClick={() => {
            setPeriodStart(state.today);
            setPeriodEnd(state.today);
          }}>Usar solo hoy</button>
        </div>
        <ul className="timeline">
          {state.reports.length === 0 ? <li><span className="when">Aún no hay</span><div>Genera el primero cuando quieras guardar este punto.</div><span /></li> : null}
          {state.reports.map((report) => (
            <li key={report.id}>
              <span className="when">{formatStamp(report.createdAt)}</span>
              <div>
                <a href={`/reporte/${report.id}`}><strong>{report.title}</strong></a>
                <p className="hint" style={{ margin: "4px 0 0" }}>
                  {report.periodStart ? formatLongDate(report.periodStart) : "—"} a {report.periodEnd ? formatLongDate(report.periodEnd) : "—"}
                </p>
              </div>
              <button className="quiet" type="button" onClick={() => {
                if (window.confirm("¿Borrar este reporte?")) void commit("report.delete", { id: report.id });
              }}>Borrar</button>
            </li>
          ))}
        </ul>
      </section>

      <p className="footnote">
        Punto de partida: CV y diario de 2026, corte 14 de noviembre. Las estimaciones de las cosas no son una tasación y los saldos sin confirmar no son un extracto del banco.
      </p>
    </main>
  );
}

function Stat({ kicker, value, detail, tone }: { kicker: string; value: string; detail: string; tone?: "olive" | "clay" }) {
  return (
    <article className={tone ? `stat ${tone}` : "stat"}>
      <p className="kicker">{kicker}</p>
      <p className="stat-value">{value}</p>
      {detail ? <p className="stat-detail">{detail}</p> : null}
    </article>
  );
}
