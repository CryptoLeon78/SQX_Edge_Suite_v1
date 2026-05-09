import { TESTER_RENEWAL_CYCLE_DAYS } from "@/lib/access-contract";

export default function PortalPage() {
  return (
    <main className="shell">
      <section className="panel hero">
        <p className="eyebrow">Tester Pro</p>
        <h1>Protected portal placeholder</h1>
        <p>
          This route is intentionally protected by middleware. Real features stay blocked until T3-T8 provide auth,
          entitlement, renewal and audit persistence.
        </p>
        <div className="grid">
          <div className="metric">
            <strong>Renewal cycle</strong>
            <p>{TESTER_RENEWAL_CYCLE_DAYS} days.</p>
          </div>
          <div className="metric">
            <strong>Entitlement</strong>
            <p>Requires active `tester_pro` access.</p>
          </div>
          <div className="metric">
            <strong>Watermark</strong>
            <p>Every tester view must show a visible identity marker.</p>
          </div>
        </div>
      </section>
      <p className="watermark">SQX TESTER WATERMARK PLACEHOLDER</p>
    </main>
  );
}

