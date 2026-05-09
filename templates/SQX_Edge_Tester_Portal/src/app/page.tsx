export default function HomePage() {
  return (
    <main className="shell">
      <section className="panel hero">
        <p className="eyebrow">Controlled tester access</p>
        <h1>SQX Edge Tester Portal</h1>
        <p>
          Private bootstrap for the future Pro tester experience. Login, renewal and audit behavior are intentionally
          placeholders until T3-T8 define and verify the real access contracts.
        </p>
        <div className="grid" aria-label="Access rules">
          <div className="metric">
            <strong>Per-user identity</strong>
            <p>Email/password access replaces shared tester passwords.</p>
          </div>
          <div className="metric">
            <strong>15-day cycle</strong>
            <p>Tester access must expire into manual review.</p>
          </div>
          <div className="metric">
            <strong>No public launch</strong>
            <p>No Vercel deployment or tester invite is part of this bootstrap.</p>
          </div>
        </div>
      </section>
    </main>
  );
}

