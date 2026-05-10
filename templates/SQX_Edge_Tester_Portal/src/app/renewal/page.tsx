import { TESTER_RENEWAL_CYCLE_DAYS } from "@/lib/access-contract";
import { MANUAL_RENEWAL_DECISIONS } from "@/lib/renewal-flow";

export default function RenewalPage() {
  return (
    <main className="shell">
      <section className="panel hero">
        <p className="eyebrow">Manual renewal</p>
        <h1>15-day tester access review</h1>
        <p>
          T6 keeps tester access under an operator decision every {TESTER_RENEWAL_CYCLE_DAYS} days. This template
          previews approve, deny and block outcomes without mutating production data.
        </p>
        <div className="grid">
          <div className="metric">
            <strong>Default state</strong>
            <p>pending_renewal until an operator decides.</p>
          </div>
          <div className="metric">
            <strong>Persistence</strong>
            <p>manual-preview only in this public-safe template.</p>
          </div>
          <div className="metric">
            <strong>Audit</strong>
            <p>future private DB must record each operator decision.</p>
          </div>
        </div>
        <div className="feature-list" aria-label="Manual renewal decision preview">
          {MANUAL_RENEWAL_DECISIONS.map((decision) => (
            <form key={decision} action="/api/tester/renewal" method="post">
              <input type="hidden" name="decision" value={decision} />
              <button type="submit">{decision}</button>
            </form>
          ))}
        </div>
      </section>
    </main>
  );
}
