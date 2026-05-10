import { TESTER_RENEWAL_CYCLE_DAYS } from "@/lib/access-contract";
import { buildDeploymentProtectionSummary } from "@/lib/deployment-protection";
import { TESTER_PRO_FEATURES } from "@/lib/entitlement-gates";
import { MANUAL_RENEWAL_DECISIONS } from "@/lib/renewal-flow";
import { buildDemoVisibleWatermark } from "@/lib/security-hardening";

export default function PortalPage() {
  const deploymentProtection = buildDeploymentProtectionSummary();
  const watermark = buildDemoVisibleWatermark();

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
        <div className="feature-list" aria-label="Tester Pro feature gates">
          {TESTER_PRO_FEATURES.map((feature) => (
            <span key={feature}>{feature}</span>
          ))}
        </div>
        <div className="metric">
          <strong>Manual renewal actions</strong>
          <p>{MANUAL_RENEWAL_DECISIONS.join(" / ")}.</p>
          <a href="/renewal">Review renewal state</a>
        </div>
        <div className="metric">
          <strong>Admin preview</strong>
          <p>Create, renew, deny, block and audit review stay operator-only.</p>
          <a href="/admin/testers">Open admin console</a>
        </div>
        <div className="metric">
          <strong>Hardening</strong>
          <p>{deploymentProtection.requiredBeforePreview.length} deployment-protection checks required before preview.</p>
        </div>
        <p>
          Feature access is checked by `/api/tester/features`; visible UI alone must never grant paid functionality.
        </p>
        <form action="/api/auth/logout" method="post">
          <button type="submit">Sign out</button>
        </form>
      </section>
      <p className="watermark">{watermark}</p>
    </main>
  );
}
