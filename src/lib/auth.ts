import "server-only";
import { getIdentity, requireIdentity } from "../../cursor/identity.js";

export const NO_STORE = { "cache-control": "private, no-store" };

export function json(data: unknown, status = 200): Response {
  return Response.json(data, { status, headers: NO_STORE });
}

export function safeError(error: unknown): string {
  const message = error instanceof Error ? error.message : "error";
  return message.replace(/postgres(?:ql)?:\/\/\S+/gi, "postgres://redacted");
}

type Person = {
  sub: string;
  stage: string;
  simulated: boolean;
  kind: string;
  appVisibility?: string;
};

function asPerson(identity: unknown): Person | null {
  if (typeof identity !== "object" || identity === null) return null;
  const value = identity as Record<string, unknown>;
  if (value.verified !== true || value.kind !== "person" || typeof value.sub !== "string" || value.sub === "") {
    return null;
  }
  return {
    sub: value.sub,
    stage: value.stage === "preview" ? "preview" : "production",
    simulated: value.simulated === true,
    kind: "person",
    appVisibility: typeof value.appVisibility === "string" ? value.appVisibility : undefined,
  };
}

export function sameOrigin(request: Request): boolean {
  const site = request.headers.get("sec-fetch-site");
  if (site === "same-origin") return true;
  if (site === "cross-site" || site === "same-site") return false;
  const origin = request.headers.get("origin");
  const host = request.headers.get("x-forwarded-host") ?? request.headers.get("host");
  if (!origin || !host) return false;
  try {
    return new URL(origin).host === host;
  } catch {
    return false;
  }
}

export async function viewer(request: Request, mutate: boolean): Promise<{ owner: string; simulated: boolean } | Response> {
  const identity = await requireIdentity(request);
  if (identity instanceof Response) return identity;
  const person = asPerson(identity);
  if (!person) return json({ error: "Esta página solo se abre con tu sesión." }, 403);
  if (person.appVisibility === "public" || (person.appVisibility === "team" && !person.simulated)) {
    return json(
      { error: "Ábrela publicada como privada. En equipo o en público no cargo el diario." },
      403,
    );
  }
  if (mutate && !sameOrigin(request)) return json({ error: "El origen de la petición no coincide." }, 403);
  return { owner: `${person.stage}:${person.sub}`, simulated: person.simulated };
}

export async function pageViewer(headerList: Headers): Promise<
  { owner: string; simulated: boolean } | { blocked: "signed_out" | "shared" }
> {
  const identity = await getIdentity(headerList);
  const person = asPerson(identity);
  if (!person) return { blocked: "signed_out" };
  if (person.appVisibility === "public" || (person.appVisibility === "team" && !person.simulated)) {
    return { blocked: "shared" };
  }
  return { owner: `${person.stage}:${person.sub}`, simulated: person.simulated };
}
