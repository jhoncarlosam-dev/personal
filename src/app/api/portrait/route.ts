import { NO_STORE, json, safeError, viewer } from "../../../lib/auth";
import { readPortrait, savePortrait, sniffImage } from "../../../lib/store";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const gate = await viewer(request, false);
  if (gate instanceof Response) return gate;
  try {
    const image = await readPortrait(gate.owner);
    if (!image) return new Response(null, { status: 404, headers: NO_STORE });
    return new Response(new Uint8Array(image.bytes), {
      headers: {
        "content-type": image.contentType,
        "cache-control": "private, no-store",
        "x-content-type-options": "nosniff",
      },
    });
  } catch (error) {
    console.error(safeError(error));
    return new Response(null, { status: 500, headers: NO_STORE });
  }
}

export async function POST(request: Request) {
  const gate = await viewer(request, true);
  if (gate instanceof Response) return gate;
  const length = Number(request.headers.get("content-length") || 0);
  if (length > 2_200_000) return json({ error: "La foto pasa de 1,5 MB." }, 413);
  try {
    const form = await request.formData();
    const file = form.get("file");
    if (!(file instanceof File)) return json({ error: "Falta la foto." }, 400);
    if (file.size > 1_500_000) return json({ error: "La foto pasa de 1,5 MB." }, 400);
    const bytes = Buffer.from(await file.arrayBuffer());
    const contentType = sniffImage(bytes);
    if (!contentType) return json({ error: "La foto tiene que ser JPG, PNG o WebP." }, 400);
    return json({ state: await savePortrait(gate.owner, bytes, contentType) });
  } catch (error) {
    console.error(safeError(error));
    return json({ error: "No pude guardar la foto." }, 400);
  }
}
