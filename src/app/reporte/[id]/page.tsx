import Link from "next/link";
import { notFound } from "next/navigation";
import { headers } from "next/headers";
import { PrintButton } from "../../../components/print-button";
import { ReportDocument } from "../../../components/report-document";
import { Locked } from "../../../components/locked";
import { pageViewer, safeError } from "../../../lib/auth";
import { positiveId, readReportRecord, readState } from "../../../lib/store";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id: raw } = await params;
  const id = positiveId(raw);
  if (!id) notFound();
  const headerList = await headers();
  const gate = await pageViewer(headerList);
  if ("blocked" in gate) return <Locked shared={gate.blocked === "shared"} />;
  try {
    const [record, state] = await Promise.all([
      readReportRecord(gate.owner, id),
      readState(gate.owner),
    ]);
    if (!record) notFound();
    return (
      <main className="page">
        <div className="row no-print" style={{ marginBottom: 16 }}>
          <Link href="/">Volver al punto</Link>
          <PrintButton />
        </div>
        <ReportDocument
          body={record.body}
          title={record.title}
          createdAt={record.createdAt}
          hasPortrait={state.hasPortrait}
        />
      </main>
    );
  } catch (error) {
    console.error(safeError(error));
    return (
      <main className="page narrow">
        <h1>No pude abrir el reporte.</h1>
        <p><Link href="/">Volver al punto</Link></p>
      </main>
    );
  }
}
