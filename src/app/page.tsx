import { headers } from "next/headers";
import { Dashboard } from "../components/dashboard";
import { Locked } from "../components/locked";
import { pageViewer, safeError } from "../lib/auth";
import { readState } from "../lib/store";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export default async function Page() {
  const headerList = await headers();
  const gate = await pageViewer(headerList);
  if ("blocked" in gate) return <Locked shared={gate.blocked === "shared"} />;
  try {
    const state = await readState(gate.owner);
    return <Dashboard initial={state} simulated={gate.simulated} />;
  } catch (error) {
    console.error(safeError(error));
    return (
      <main className="page narrow">
        <p className="kicker">Punto de vida</p>
        <h1>No pude abrir el cuaderno.</h1>
        <p>Vuelve a cargar la página. Si sigue igual, el almacén de datos no respondió.</p>
      </main>
    );
  }
}
