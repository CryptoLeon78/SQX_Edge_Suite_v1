import { NextRequest, NextResponse } from "next/server";
import {
  ADMIN_TESTER_ACTIONS,
  buildAdminActionPreview,
  buildDemoAdminTesterRows,
  isAdminTesterAction,
  isDemoAdminConsoleEnabled
} from "@/lib/admin-console";
import { hasPrototypeSession } from "@/lib/session-prototype";

function missingSessionResponse() {
  return NextResponse.json(
    {
      ok: false,
      reasonCode: "missing_session"
    },
    { status: 401 }
  );
}

function disabledResponse() {
  return NextResponse.json(
    {
      ok: false,
      reasonCode: "demo_admin_console_disabled"
    },
    { status: 403 }
  );
}

export function GET(request: NextRequest) {
  if (!hasPrototypeSession(request)) {
    return missingSessionResponse();
  }

  if (!isDemoAdminConsoleEnabled()) {
    return disabledResponse();
  }

  return NextResponse.json({
    ok: true,
    mode: "operator-preview",
    testers: buildDemoAdminTesterRows(),
    actions: ADMIN_TESTER_ACTIONS,
    noMutation: true
  });
}

export async function POST(request: NextRequest) {
  if (!hasPrototypeSession(request)) {
    return missingSessionResponse();
  }

  if (!isDemoAdminConsoleEnabled()) {
    return disabledResponse();
  }

  const formData = await request.formData();
  const action = String(formData.get("action") ?? "");
  const targetTesterId = String(formData.get("testerId") ?? "demo-new-tester");

  if (!isAdminTesterAction(action)) {
    return NextResponse.json(
      {
        ok: false,
        reasonCode: "unsupported_admin_action",
        actions: ADMIN_TESTER_ACTIONS
      },
      { status: 400 }
    );
  }

  return NextResponse.json({
    ok: true,
    mode: "operator-preview",
    actionPreview: buildAdminActionPreview(action, targetTesterId),
    noMutation: true,
    operatorActionRequired: "Persist the tester change and audit event in the future private tester database."
  });
}
