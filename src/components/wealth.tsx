"use client";

import { useState } from "react";
import { formatCop, KIND_LABEL, monthlyCosts, wealthOf } from "../lib/life";
import type { Asset, Cost, Liability, LifeState } from "../lib/types";
import { CheckField, MoneyField, TextField } from "./fields";

type Action = (action: string, payload: Record<string, unknown>) => void;

export function WealthSection({ state, saving, onAction }: { state: LifeState; saving: boolean; onAction: Action }) {
  const wealth = wealthOf(state.assets, state.liabilities);
  const fixed = monthlyCosts(state.costs);
  return (
    <section className="section" id="cosas">
      <div className="section-head">
        <div>
          <p className="kicker">Patrimonio</p>
          <h2>Cosas, deudas y el mes</h2>
        </div>
      </div>
      <div className="totals">
        <div className="total">
          <span className="kicker">Cosas con valor</span>
          <strong>{formatCop(wealth.assetsCop)}</strong>
          <p className="hint">{wealth.unvaluedCount === 0 ? "Todo tiene un valor." : `${wealth.unvaluedCount} sin valorar, no entran a la suma.`}</p>
        </div>
        <div className="total">
          <span className="kicker">Deudas anotadas</span>
          <strong>{formatCop(wealth.debtsCop)}</strong>
          <p className="hint">{wealth.unconfirmedCount === 0 ? "Todas confirmadas." : `${wealth.unconfirmedCount} sin confirmar con un extracto.`}</p>
        </div>
        <div className={wealth.netCop < 0 ? "total negative" : "total"}>
          <span className="kicker">Neto estimado</span>
          <strong>{formatCop(wealth.netCop)}</strong>
          <p className="hint">Cosas menos deudas. El costo fijo del mes es {formatCop(fixed)}.</p>
        </div>
      </div>

      <div className="cards">
        {state.assets.map((asset) => (
          <ItemCard
            key={asset.id}
            title={asset.name}
            kind={KIND_LABEL[asset.kind] ?? asset.kind}
            amount={asset.valueCop == null ? "Por valorar" : formatCop(asset.valueCop)}
            estimate={asset.valueIsEstimate}
            owned={asset.owned}
            detail={asset.detail}
            note={asset.note}
            saving={saving}
            onDelete={() => {
              if (window.confirm(`¿Quitar ${asset.name} del patrimonio?`)) onAction("asset.delete", { id: asset.id });
            }}
          >
            <AssetForm
              initial={asset}
              saving={saving}
              submitLabel="Guardar cosa"
              onSubmit={(next) => onAction("asset.update", { id: asset.id, asset: next })}
            />
          </ItemCard>
        ))}
      </div>
      <details className="panel">
        <summary>Agregar una cosa</summary>
        <AssetForm
          initial={{ name: "", kind: "otro", detail: "", valueCop: null, valueIsEstimate: true, owned: true, note: "" }}
          saving={saving}
          submitLabel="Agregar"
          onSubmit={(asset) => onAction("asset.create", { asset })}
        />
      </details>

      <h3 className="display" style={{ marginTop: 28 }}>Deudas</h3>
      <div className="cards">
        {state.liabilities.map((debt) => (
          <ItemCard
            key={debt.id}
            title={debt.name}
            kind={debt.confirmed ? "Confirmada" : "Por confirmar"}
            amount={formatCop(debt.balanceCop)}
            estimate={!debt.confirmed}
            detail={debt.monthlyCop ? `Cuota ${formatCop(debt.monthlyCop)}` : ""}
            note={debt.note}
            saving={saving}
            onDelete={() => {
              if (window.confirm(`¿Quitar la deuda ${debt.name}?`)) onAction("liability.delete", { id: debt.id });
            }}
          >
            <LiabilityForm
              initial={debt}
              saving={saving}
              onSubmit={(liability) => onAction("liability.update", { id: debt.id, liability })}
            />
          </ItemCard>
        ))}
      </div>
      <details className="panel">
        <summary>Agregar una deuda</summary>
        <LiabilityForm
          initial={{ name: "", balanceCop: 0, monthlyCop: null, confirmed: false, note: "" }}
          saving={saving}
          onSubmit={(liability) => onAction("liability.create", { liability })}
        />
      </details>

      <h3 className="display" style={{ marginTop: 28 }}>Lo que pide el mes</h3>
      <div className="cards">
        {state.costs.map((cost) => (
          <ItemCard
            key={cost.id}
            title={cost.name}
            kind="Cada mes"
            amount={formatCop(cost.amountCop)}
            detail=""
            note={cost.note}
            saving={saving}
            onDelete={() => {
              if (window.confirm(`¿Quitar el costo ${cost.name}?`)) onAction("cost.delete", { id: cost.id });
            }}
          >
            <CostForm initial={cost} saving={saving} onSubmit={(next) => onAction("cost.update", { id: cost.id, cost: next })} />
          </ItemCard>
        ))}
      </div>
      <details className="panel">
        <summary>Agregar un costo mensual</summary>
        <CostForm
          initial={{ name: "", amountCop: 0, note: "" }}
          saving={saving}
          onSubmit={(cost) => onAction("cost.create", { cost })}
        />
      </details>
    </section>
  );
}

function ItemCard({
  title,
  kind,
  amount,
  estimate = false,
  owned = true,
  detail,
  note,
  saving,
  onDelete,
  children,
}: {
  title: string;
  kind: string;
  amount: string;
  estimate?: boolean;
  owned?: boolean;
  detail: string;
  note: string;
  saving: boolean;
  onDelete: () => void;
  children: React.ReactNode;
}) {
  return (
    <article className="item">
      <header>
        <h3>{title}</h3>
        <span className="money">{amount}</span>
      </header>
      <p className="hint" style={{ margin: "4px 0 8px" }}>
        <span className={estimate ? "tag" : "tag ok"}>{owned ? kind : "No es mía"}</span>
        {estimate ? " · estimación o saldo sin confirmar" : ""}
      </p>
      {detail ? <p style={{ margin: "0 0 8px" }}>{detail}</p> : null}
      {note ? <p className="hint">{note}</p> : null}
      <details>
        <summary>Editar</summary>
        {children}
      </details>
      <button className="quiet" type="button" disabled={saving} onClick={onDelete} style={{ marginTop: 8 }}>
        Quitar
      </button>
    </article>
  );
}

function AssetForm({
  initial,
  saving,
  submitLabel,
  onSubmit,
}: {
  initial: Omit<Asset, "id">;
  saving: boolean;
  submitLabel: string;
  onSubmit: (asset: Omit<Asset, "id">) => void;
}) {
  const [draft, setDraft] = useState(initial);
  return (
    <div className="grid-form" style={{ marginTop: 10 }}>
      <TextField label="Nombre" value={draft.name} onChange={(name) => setDraft({ ...draft, name })} />
      <label className="field">
        <span>Tipo</span>
        <select value={draft.kind} onChange={(event) => setDraft({ ...draft, kind: event.target.value as Asset["kind"] })}>
          {Object.entries(KIND_LABEL).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </label>
      <TextField label="Detalle" value={draft.detail} onChange={(detail) => setDraft({ ...draft, detail })} wide />
      <MoneyField label="Valor en pesos" value={draft.valueCop} onChange={(valueCop) => setDraft({ ...draft, valueCop })} />
      <CheckField label="El valor es una estimación" checked={draft.valueIsEstimate} onChange={(valueIsEstimate) => setDraft({ ...draft, valueIsEstimate })} />
      <CheckField label="Es mía" checked={draft.owned} onChange={(owned) => setDraft({ ...draft, owned })} />
      <TextField label="Nota" value={draft.note} onChange={(note) => setDraft({ ...draft, note })} wide />
      <button className="primary" type="button" disabled={saving} onClick={() => onSubmit(draft)}>{submitLabel}</button>
    </div>
  );
}

function LiabilityForm({
  initial,
  saving,
  onSubmit,
}: {
  initial: Omit<Liability, "id">;
  saving: boolean;
  onSubmit: (debt: Omit<Liability, "id">) => void;
}) {
  const [draft, setDraft] = useState(initial);
  return (
    <div className="grid-form" style={{ marginTop: 10 }}>
      <TextField label="Nombre" value={draft.name} onChange={(name) => setDraft({ ...draft, name })} />
      <MoneyField label="Saldo" value={draft.balanceCop} onChange={(balanceCop) => setDraft({ ...draft, balanceCop: balanceCop ?? 0 })} />
      <MoneyField label="Cuota mensual" value={draft.monthlyCop} onChange={(monthlyCop) => setDraft({ ...draft, monthlyCop })} />
      <CheckField label="Ya confirmé este saldo" checked={draft.confirmed} onChange={(confirmed) => setDraft({ ...draft, confirmed })} />
      <TextField label="Nota" value={draft.note} onChange={(note) => setDraft({ ...draft, note })} wide />
      <button className="primary" type="button" disabled={saving} onClick={() => onSubmit(draft)}>Guardar deuda</button>
    </div>
  );
}

function CostForm({
  initial,
  saving,
  onSubmit,
}: {
  initial: Omit<Cost, "id">;
  saving: boolean;
  onSubmit: (cost: Omit<Cost, "id">) => void;
}) {
  const [draft, setDraft] = useState(initial);
  return (
    <div className="grid-form" style={{ marginTop: 10 }}>
      <TextField label="Nombre" value={draft.name} onChange={(name) => setDraft({ ...draft, name })} />
      <MoneyField label="Valor mensual" value={draft.amountCop} onChange={(amountCop) => setDraft({ ...draft, amountCop: amountCop ?? 0 })} />
      <TextField label="Nota" value={draft.note} onChange={(note) => setDraft({ ...draft, note })} wide />
      <button className="primary" type="button" disabled={saving} onClick={() => onSubmit(draft)}>Guardar costo</button>
    </div>
  );
}
