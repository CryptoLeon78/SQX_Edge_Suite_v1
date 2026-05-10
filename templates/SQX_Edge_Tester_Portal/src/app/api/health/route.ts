import { NextResponse } from "next/server";
import { buildDeploymentProtectionSummary } from "@/lib/deployment-protection";
import { HARDENING_ENV, isGlobalKillSwitchEnabled, isRateLimitEnabled } from "@/lib/security-hardening";

export function GET() {
  return NextResponse.json({
    ok: true,
    service: "sqx-edge-tester-portal",
    phase: "T8",
    containsTesterData: false,
    hardening: {
      globalKillSwitchEnabled: isGlobalKillSwitchEnabled(),
      rateLimitEnabled: isRateLimitEnabled(),
      env: HARDENING_ENV,
      deploymentProtection: buildDeploymentProtectionSummary()
    }
  });
}
