export const TESTER_RENEWAL_CYCLE_DAYS = 15;

export const TESTER_STATUSES = [
  "invited",
  "active",
  "pending_renewal",
  "expired",
  "denied",
  "blocked"
] as const;

export type TesterStatus = (typeof TESTER_STATUSES)[number];
export type TesterPlan = "tester_pro";

export type TesterEntitlement = {
  testerId: string;
  email: string;
  displayName: string;
  status: TesterStatus;
  plan: TesterPlan;
  expiresAt: string;
};

export function canAccessTesterPro(entitlement: TesterEntitlement, now = new Date()): boolean {
  return (
    entitlement.status === "active" &&
    entitlement.plan === "tester_pro" &&
    Number.isFinite(Date.parse(entitlement.expiresAt)) &&
    new Date(entitlement.expiresAt).getTime() > now.getTime()
  );
}

export function buildTesterWatermark(entitlement: Pick<TesterEntitlement, "testerId" | "email">): string {
  return `SQX TESTER ${entitlement.testerId} ${entitlement.email}`;
}

