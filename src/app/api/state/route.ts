import { json, safeError, viewer } from "../../../lib/auth";
import {
  createAsset,
  createCost,
  createLiability,
  createMilestone,
  createReport,
  deleteAsset,
  deleteCost,
  deleteLiability,
  deleteLog,
  deleteMilestone,
  deleteReport,
  positiveId,
  readState,
  setLiquidation,
  updateAsset,
  updateCost,
  updateLiability,
  updateProfile,
  upsertLog,
} from "../../../lib/store";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const KNOWN = /^(El |La |No |Ya |Fecha)/;

export async function GET(request: Request) {
  const gate = await viewer(request, false);
  if (gate instanceof Response) return gate;
  try {
    return json({ state: await readState(gate.owner) });
  } catch (error) {
    console.error(safeError(error));
    return json({ error: "No pude leer tus datos." }, 500);
  }
}

export async function POST(request: Request) {
  const gate = await viewer(request, true);
  if (gate instanceof Response) return gate;
  const length = Number(request.headers.get("content-length") || 0);
  if (length > 200_000) return json({ error: "El envío es demasiado grande." }, 413);
  let body: Record<string, unknown>;
  try {
    const parsed = await request.json();
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
      return json({ error: "El cuerpo no es válido." }, 400);
    }
    body = parsed as Record<string, unknown>;
  } catch {
    return json({ error: "El cuerpo no es JSON." }, 400);
  }
  try {
    return json(await dispatch(gate.owner, body));
  } catch (error) {
    console.error(safeError(error));
    const message = error instanceof Error ? error.message : "";
    return json({ error: KNOWN.test(message) ? message : "No se pudo guardar." }, 400);
  }
}

async function dispatch(owner: string, body: Record<string, unknown>) {
  const id = positiveId(body.id);
  switch (body.action) {
    case "profile":
      return { state: await updateProfile(owner, body.profile) };
    case "log.upsert":
      return { state: await upsertLog(owner, body.log) };
    case "log.delete":
      return { state: await deleteLog(owner, String(body.logDate ?? "")) };
    case "asset.create":
      return { state: await createAsset(owner, body.asset) };
    case "asset.update":
      if (!id) throw new Error("No encontré esa cosa.");
      return { state: await updateAsset(owner, id, body.asset) };
    case "asset.delete":
      if (!id) throw new Error("No encontré esa cosa.");
      return { state: await deleteAsset(owner, id) };
    case "liability.create":
      return { state: await createLiability(owner, body.liability) };
    case "liability.update":
      if (!id) throw new Error("No encontré esa deuda.");
      return { state: await updateLiability(owner, id, body.liability) };
    case "liability.delete":
      if (!id) throw new Error("No encontré esa deuda.");
      return { state: await deleteLiability(owner, id) };
    case "cost.create":
      return { state: await createCost(owner, body.cost) };
    case "cost.update":
      if (!id) throw new Error("No encontré ese costo.");
      return { state: await updateCost(owner, id, body.cost) };
    case "cost.delete":
      if (!id) throw new Error("No encontré ese costo.");
      return { state: await deleteCost(owner, id) };
    case "milestone.create":
      return { state: await createMilestone(owner, body.milestone) };
    case "milestone.delete":
      if (!id) throw new Error("No encontré ese hito.");
      return { state: await deleteMilestone(owner, id) };
    case "report.create": {
      const created = await createReport(owner, String(body.periodStart ?? ""), String(body.periodEnd ?? ""));
      return { id: created.id, state: created.state };
    }
    case "report.delete":
      if (!id) throw new Error("No encontré ese reporte.");
      return { state: await deleteReport(owner, id) };
    case "liquidation": {
      const status = body.status;
      if (status !== "recibida" && status !== "otro" && status !== "no_llego") {
        throw new Error("El estado de la liquidación no es válido.");
      }
      const amount =
        body.amountCop == null || body.amountCop === ""
          ? null
          : Number(body.amountCop);
      if (amount != null && (!Number.isInteger(amount) || amount < 0 || amount > 100_000_000_000)) {
        throw new Error("El valor de la liquidación no es válido.");
      }
      return { state: await setLiquidation(owner, status, amount) };
    }
    default:
      throw new Error("No reconozco esa acción.");
  }
}
