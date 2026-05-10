import { NextRequest, NextResponse } from "next/server";
import { evaluateTesterProGate } from "@/lib/entitlement-gates";

export function GET(request: NextRequest) {
  const gate = evaluateTesterProGate(request);

  if (!gate.ok) {
    return NextResponse.json(
      {
        ok: false,
        reasonCode: gate.reasonCode
      },
      { status: gate.status }
    );
  }

  return NextResponse.json({
    ok: true,
    plan: gate.entitlement.plan,
    status: gate.entitlement.status,
    expiresAt: gate.entitlement.expiresAt,
    features: gate.features
  });
}

