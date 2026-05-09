import type { NextRequest } from "next/server";
import { canAccessTesterPro, type TesterEntitlement } from "./access-contract";
import { hasPrototypeSession } from "./session-prototype";

export const TESTER_PRO_FEATURES = [
  "sqx_dashboard_full",
  "strategy_builder",
  "project_generator",
  "views_creator",
  "buyer_handoff_exports",
  "support_case_bundle"
] as const;

export type TesterProFeature = (typeof TESTER_PRO_FEATURES)[number];

export type EntitlementGateResult =
  | { ok: true; entitlement: TesterEntitlement; features: readonly TesterProFeature[] }
  | { ok: false; status: 401 | 403; reasonCode: "missing_session" | "demo_entitlement_disabled" | "tester_pro_inactive" };

export const DEMO_ENTITLEMENT_FLAG = "T5_DEMO_TESTER_PRO_ENABLED";

export function isDemoTesterProEnabled(): boolean {
  return process.env[DEMO_ENTITLEMENT_FLAG] === "true";
}

export function buildPrototypeTesterEntitlement(now = new Date()): TesterEntitlement {
  const expiresAt = new Date(now.getTime() + 60 * 60 * 1000).toISOString();
  return {
    testerId: "demo-tester-local-only",
    email: "tester@example.invalid",
    displayName: "Local Demo Tester",
    status: "active",
    plan: "tester_pro",
    expiresAt
  };
}

export function hasFeatureAccess(features: readonly TesterProFeature[], feature: TesterProFeature): boolean {
  return features.includes(feature);
}

export function evaluateTesterProGate(request: NextRequest, now = new Date()): EntitlementGateResult {
  if (!hasPrototypeSession(request)) {
    return { ok: false, status: 401, reasonCode: "missing_session" };
  }

  if (!isDemoTesterProEnabled()) {
    return { ok: false, status: 403, reasonCode: "demo_entitlement_disabled" };
  }

  const entitlement = buildPrototypeTesterEntitlement(now);
  if (!canAccessTesterPro(entitlement, now)) {
    return { ok: false, status: 403, reasonCode: "tester_pro_inactive" };
  }

  return {
    ok: true,
    entitlement,
    features: TESTER_PRO_FEATURES
  };
}

