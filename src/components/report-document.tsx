import { formatCop, formatLongDate, formatStamp } from "../lib/life";
import type { ReportBody } from "../lib/types";

export function ReportDocument({
  body,
  title,
  createdAt,
  hasPortrait,
}: {
  body: ReportBody;
  title: string;
  createdAt: string;
  hasPortrait: boolean;
}) {
  const profile = body.profile;
  return (
    <article className="sheet">
      <header className="sheet-top">
        {hasPortrait ? (
          <img src="/api/portrait" alt={`Foto de ${profile.fullName}`} />
        ) : (
          <div className="monogram" aria-hidden="true">JC</div>
        )}
        <div>
          <p className="kicker">Reporte de punto de vida</p>
          <h1>{profile.fullName}</h1>
          <p className="headline">{title}</p>
          <p className="hint">
            Generado el {formatLongDate(body.generatedOn)} · guardado {formatStamp(createdAt)} · hora de Colombia.
            La foto es la que está en el cuaderno ahora.
          </p>
        </div>
      </header>
      <p className="lead" style={{ marginTop: 22 }}>{body.sentence}</p>
      <div className="stats">
        <Fact kicker="Edad" value={body.agePrimary} detail={body.ageSecondary} />
        <Fact kicker="Estado civil" value={body.relationshipLabel ?? "Sin anotar"} detail={profile.civilNote} />
        <Fact kicker="Salud" value={profile.healthStatus} detail={profile.healthDetail} />
        <Fact kicker="Estudio" value={profile.studying ? "Estudiando" : "No estudia"} detail={`${profile.program} · ${profile.school} · ${profile.semester}`} />
        <Fact kicker="Ingeniería" value={profile.graduated ? "Graduado" : "Sin graduarse"} detail={profile.graduationNote} />
        <Fact kicker="Trabajo" value={profile.employed ? formatCop(profile.salaryCop) : "Sin empleo"} detail={`${profile.jobTitle} · ${profile.employer}. ${profile.salaryNote}`} />
      </div>
      <h2 style={{ marginTop: 28 }}>Patrimonio</h2>
      <p>
        Cosas {formatCop(body.wealth.assetsCop)} · deudas {formatCop(body.wealth.debtsCop)} · neto {formatCop(body.wealth.netCop)}.
        El mes, según los costos guardados, pide {formatCop(body.monthlyCostsCop)}.
      </p>
      <table>
        <thead>
          <tr><th>Cosa</th><th>Detalle</th><th className="num">Valor</th></tr>
        </thead>
        <tbody>
          {body.assets.map((asset) => (
            <tr key={asset.id}>
              <td>{asset.name}{asset.owned ? "" : " (no es mía)"}</td>
              <td>{asset.detail}{asset.valueIsEstimate ? " · estimación" : ""}</td>
              <td className="num">{asset.valueCop == null ? "Por valorar" : formatCop(asset.valueCop)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <table>
        <thead>
          <tr><th>Deuda</th><th>Nota</th><th className="num">Saldo</th></tr>
        </thead>
        <tbody>
          {body.liabilities.map((debt) => (
            <tr key={debt.id}>
              <td>{debt.name}{debt.confirmed ? "" : " · sin confirmar"}</td>
              <td>{debt.note}</td>
              <td className="num">{formatCop(debt.balanceCop)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2>Días del {formatLongDate(body.periodStart)} al {formatLongDate(body.periodEnd)}</h2>
      <p>
        {body.logSummary.days} días · estudió {body.logSummary.studied} · trabajó {body.logSummary.worked} ·
        ingresos {formatCop(body.logSummary.incomeCop)} · gastos {formatCop(body.logSummary.expenseCop)} ·
        ánimo promedio {body.logSummary.avgMood ?? "—"} · cuerpo promedio {body.logSummary.avgHealth ?? "—"} ·
        sueño promedio {body.logSummary.avgSleep ?? "—"} horas.
      </p>
      {body.logs.length > 0 ? (
        <table>
          <thead>
            <tr><th>Día</th><th>Cuerpo</th><th>Ánimo</th><th>Sueño</th><th>Nota</th></tr>
          </thead>
          <tbody>
            {body.logs.map((log) => (
              <tr key={log.id}>
                <td>{formatLongDate(log.logDate)}</td>
                <td>{log.health ?? "—"}</td>
                <td>{log.mood ?? "—"}</td>
                <td>{log.sleepHours ?? "—"}</td>
                <td>{log.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : <p>En ese rango no hay días guardados. El reporte igual deja el punto de vida.</p>}
      <h2>Hitos guardados</h2>
      <ul>
        {body.milestones.map((item) => (
          <li key={item.id}><strong>{formatLongDate(item.happenedOn)}.</strong> {item.title} {item.detail}</li>
        ))}
      </ul>
      <p className="footnote">
        Otros trabajos: {profile.otherWork || "ninguno anotado"}. Inglés: {profile.english || "sin nota"}.
        Las estimaciones no son una tasación y un saldo sin confirmar no es el extracto del banco.
      </p>
    </article>
  );
}

function Fact({ kicker, value, detail }: { kicker: string; value: string; detail: string }) {
  return (
    <article className="stat">
      <p className="kicker">{kicker}</p>
      <p className="stat-value">{value}</p>
      <p className="stat-detail">{detail}</p>
    </article>
  );
}
