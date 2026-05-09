import { NextRequest, NextResponse } from "next/server";

export function GET(request: NextRequest) {
  const auth = request.headers.get("authorization");
  const expected = process.env.CRON_SECRET ? `Bearer ${process.env.CRON_SECRET}` : null;

  if (!expected || auth !== expected) {
    return NextResponse.json({ ok: false, error: "unauthorized" }, { status: 401 });
  }

  return NextResponse.json({
    ok: true,
    mode: "dry-run",
    phase: "T2",
    message: "Expiry scanner placeholder. T6 owns real renewal state changes."
  });
}

