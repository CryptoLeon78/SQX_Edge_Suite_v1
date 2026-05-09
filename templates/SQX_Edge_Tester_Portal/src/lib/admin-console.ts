import { TESTER_RENEWAL_CYCLE_DAYS, type TesterEntitlement, type TesterStatus } from "./access-contract";
import { addRenewalDays, type ManualRenewalDecision } from "./renewal-flow";

export const DEMO_ADMIN_CONSOLE_FLAG = "T7_DEMO_ADMIN_CONSOLE_ENABLED";

export const ADMIN_TESTER_ACTIONS = ["create_tester", "renew_15_days", "deny_tester", "block_tester"] as const;
export type AdminTesterAction = (typeof ADMIN_TESTER_ACTIONS)[number];

export type AdminTesterRow = TesterEntitlement & {
  lastAuditEvent: string;
  riskNote: string;
};

export type AdminActionPreview = {
  mode: "operator-preview";
  action: AdminTesterAction;
  targetTesterId: string;
  nextStatus: TesterStatus;
  nextExpiresAt: string;
  auditEventType: "tester_invited" | "renewal_approved" | "renewal_denied" | "tester_blocked";
  noMutation: true;
  persistence: "not_applied_in_template";
};

export function isDemoAdminConsoleEnabled(): boolean {
  return process.env[DEMO_ADMIN_CONSOLE_FLAG] === "true";
}

export function isAdminTesterAction(value: string): value is AdminTesterAction {
  return (ADMIN_TESTER_ACTIONS as readonly string[]).includes(value);
}

export function buildDemoAdminTesterRows(now = new Date()): AdminTesterRow[] {
  return [
    {
      testerId: "demo-tester-active",
      email: "active.tester@example.invalid",
      displayName: "Active Demo Tester",
      status: "active",
      plan: "tester_pro",
      expiresAt: addRenewalDays(now, 4),
      lastAuditEvent: "login_succeeded",
      riskNote: "normal_review"
    },
    {
      testerId: "demo-tester-renewal",
      email: "renewal.tester@example.invalid",
      displayName: "Renewal Demo Tester",
      status: "pending_renewal",
      plan: "tester_pro",
      expiresAt: new Date(now.getTime() - 1000).toISOString(),
      lastAuditEvent: "renewal_requested",
      riskNote: "operator_decision_required"
    },
    {
      testerId: "demo-tester-blocked",
      email: "blocked.tester@example.invalid",
      displayName: "Blocked Demo Tester",
      status: "blocked",
      plan: "tester_pro",
      expiresAt: new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString(),
      lastAuditEvent: "tester_blocked",
      riskNote: "distribution_risk_review"
    }
  ];
}

export function buildAdminActionPreview(action: AdminTesterAction, targetTesterId: string, now = new Date()): AdminActionPreview {
  if (action === "create_tester") {
    return {
      mode: "operator-preview",
      action,
      targetTesterId,
      nextStatus: "invited",
      nextExpiresAt: addRenewalDays(now, TESTER_RENEWAL_CYCLE_DAYS),
      auditEventType: "tester_invited",
      noMutation: true,
      persistence: "not_applied_in_template"
    };
  }

  if (action === "renew_15_days") {
    return {
      mode: "operator-preview",
      action,
      targetTesterId,
      nextStatus: "active",
      nextExpiresAt: addRenewalDays(now, TESTER_RENEWAL_CYCLE_DAYS),
      auditEventType: "renewal_approved",
      noMutation: true,
      persistence: "not_applied_in_template"
    };
  }

  const renewalDecision: ManualRenewalDecision = action === "deny_tester" ? "deny" : "block";

  return {
    mode: "operator-preview",
    action,
    targetTesterId,
    nextStatus: renewalDecision === "deny" ? "denied" : "blocked",
    nextExpiresAt: now.toISOString(),
    auditEventType: renewalDecision === "deny" ? "renewal_denied" : "tester_blocked",
    noMutation: true,
    persistence: "not_applied_in_template"
  };
}
