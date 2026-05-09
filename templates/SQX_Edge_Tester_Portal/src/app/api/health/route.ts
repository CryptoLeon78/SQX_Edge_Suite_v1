import { NextResponse } from "next/server";

export function GET() {
  return NextResponse.json({
    ok: true,
    service: "sqx-edge-tester-portal",
    phase: "T2",
    containsTesterData: false
  });
}

