import { TESTER_RENEWAL_CYCLE_DAYS, type TesterEntitlement, type TesterStatus } from "./access-contract";

export const DEMO_RENEWAL_STATE_ENV = "T6_DEMO_RENEWAL_STATE";

export const RENEWAL_STATES = ["active", "pending_renewal", "expired", "denied", "blocked"] as const;
export type RenewalState = (typeof RENEWAL_STATES)[number];

export const MANUAL_RENEWAL_DECISIONS = ["approve_15_days", "deny", "block"] as const;
export type ManualRenewalDecision = (typeof MANUAL_RENEWAL_DECISIONS)[number];

export type RenewalGateResult =
  | {
      ok: true;
      state: "active";
      entitlement: TesterEntitlement;
      expiresAt: string;
      daysRemaining: number;
      reasonCode: null;
    }
  | {
      ok: false;
      status: 403;
      state: Exclude<RenewalState, "active">;
      entitlement: TesterEntitlement;
      expiresAt: string;
      daysRemaining: number;
      reasonCode: "renewal_pending_operator_approval" | "tester_expired" | "renewal_denied" | "tester_blocked";
    };

export type RenewalDecisionPreview = {
  mode: "manual-preview";
  decision: ManualRenewalDecision;
  nextStatus: TesterStatus;
  nextExpiresAt: string;
  auditEventType: "renewal_approved" | "renewal_denied" | "tester_blocked";
  persistence: "not_applied_in_template";
};

function parseTimestamp(value: string): number {
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp) ? timestamp : 0;
}

export function addRenewalDays(now = new Date(), days = TESTER_RENEWAL_CYCLE_DAYS): string {
  return new Date(now.getTime() + days * 24 * 60 * 60 * 1000).toISOString();
}

export function isRenewalState(value: string): value is RenewalState {
  return (RENEWAL_STATES as readonly string[]).includes(value);
}

export function isManualRenewalDecision(value: string): value is ManualRenewalDecision {
  return (MANUAL_RENEWAL_DECISIONS as readonly string[]).includes(value);
}

export function readDemoRenewalState(): RenewalState {
  const configuredState = process.env[DEMO_RENEWAL_STATE_ENV] ?? "pending_renewal";
  return isRenewalState(configuredState) ? configuredState : "pending_renewal";
}

export function buildDemoRenewalEntitlement(now = new Date()): TesterEntitlement {
  const state = readDemoRenewalState();
  const expiresAt = state === "active" ? addRenewalDays(now) : new Date(now.getTime() - 1000).toISOString();

  return {
    testerId: "demo-tester-local-only",
    email: "tester@example.invalid",
    displayName: "Local Demo Tester",
    status: state,
    plan: "tester_pro",
    expiresAt
  };
}

export function classifyRenewalState(entitlement: TesterEntitlement, now = new Date()): RenewalState {
  if (entitlement.status === "denied" || entitlement.status === "blocked" || entitlement.status === "pending_renewal") {
    return entitlement.status;
  }

  if (entitlement.status === "expired") {
    return "expired";
  }

  return parseTimestamp(entitlement.expiresAt) > now.getTime() ? "active" : "expired";
}

export function calculateDaysRemaining(expiresAt: string, now = new Date()): number {
  const diffMs = parseTimestamp(expiresAt) - now.getTime();
  return Math.max(0, Math.ceil(diffMs / (24 * 60 * 60 * 1000)));
}

export function evaluateRenewalGate(entitlement: TesterEntitlement, now = new Date()): RenewalGateResult {
  const state = classifyRenewalState(entitlement, now);
  const daysRemaining = calculateDaysRemaining(entitlement.expiresAt, now);

  if (state === "active") {
    return {
      ok: true,
      state,
      entitlement,
      expiresAt: entitlement.expiresAt,
      daysRemaining,
      reasonCode: null
    };
  }

  const reasonByState = {
    pending_renewal: "renewal_pending_operator_approval",
    expired: "tester_expired",
    denied: "renewal_denied",
    blocked: "tester_blocked"
  } as const;

  return {
    ok: false,
    status: 403,
    state,
    entitlement,
    expiresAt: entitlement.expiresAt,
    daysRemaining,
    reasonCode: reasonByState[state]
  };
}

export function buildRenewalDecisionPreview(decision: ManualRenewalDecision, now = new Date()): RenewalDecisionPreview {
  if (decision === "approve_15_days") {
    return {
      mode: "manual-preview",
      decision,
      nextStatus: "active",
      nextExpiresAt: addRenewalDays(now),
      auditEventType: "renewal_approved",
      persistence: "not_applied_in_template"
    };
  }

  if (decision === "deny") {
    return {
      mode: "manual-preview",
      decision,
      nextStatus: "denied",
      nextExpiresAt: now.toISOString(),
      auditEventType: "renewal_denied",
      persistence: "not_applied_in_template"
    };
  }

  return {
    mode: "manual-preview",
    decision,
    nextStatus: "blocked",
    nextExpiresAt: now.toISOString(),
    auditEventType: "tester_blocked",
    persistence: "not_applied_in_template"
  };
}
