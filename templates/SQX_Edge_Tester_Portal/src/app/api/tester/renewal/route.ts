import { NextRequest, NextResponse } from "next/server";
import { TESTER_RENEWAL_CYCLE_DAYS } from "@/lib/access-contract";
import { hasPrototypeSession } from "@/lib/session-prototype";
import {
  MANUAL_RENEWAL_DECISIONS,
  buildDemoRenewalEntitlement,
  buildRenewalDecisionPreview,
  evaluateRenewalGate,
  isManualRenewalDecision,
  readDemoRenewalState
} from "@/lib/renewal-flow";

function missingSessionResponse() {
  return NextResponse.json(
    {
      ok: false,
      reasonCode: "missing_session"
    },
    { status: 401 }
  );
}

export function GET(request: NextRequest) {
  if (!hasPrototypeSession(request)) {
    return missingSessionResponse();
  }

  const entitlement = buildDemoRenewalEntitlement();
  const gate = evaluateRenewalGate(entitlement);

  return NextResponse.json({
    ok: gate.ok,
    mode: "manual-review-only",
    renewalCycleDays: TESTER_RENEWAL_CYCLE_DAYS,
    state: gate.state,
    configuredDemoState: readDemoRenewalState(),
    expiresAt: gate.expiresAt,
    daysRemaining: gate.daysRemaining,
    reasonCode: gate.reasonCode,
    manualDecisions: MANUAL_RENEWAL_DECISIONS
  });
}

export async function POST(request: NextRequest) {
  if (!hasPrototypeSession(request)) {
    return missingSessionResponse();
  }

  const formData = await request.formData();
  const decision = String(formData.get("decision") ?? "");

  if (!isManualRenewalDecision(decision)) {
    return NextResponse.json(
      {
        ok: false,
        reasonCode: "unsupported_decision",
        manualDecisions: MANUAL_RENEWAL_DECISIONS
      },
      { status: 400 }
    );
  }

  const preview = buildRenewalDecisionPreview(decision);

  return NextResponse.json({
    ok: true,
    mode: "manual-preview",
    decisionPreview: preview,
    noMutation: true,
    operatorActionRequired: "Persist this decision in the future private tester database and audit log."
  });
}
