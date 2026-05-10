import json
import py_compile
import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SENSITIVE_LITERAL_FORBIDDEN = "".join(["TbNX3", "XLrg!", "4Dc6J"])
APP_ROOT = PROJECT_ROOT / "app"
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
ANALYSIS_ROOT = PROJECT_ROOT / "analysis"
ARCHITECTURE_DOC = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
PROJECT_GOVERNANCE_DOC = PROJECT_ROOT / "docs" / "PROJECT_GOVERNANCE.md"
J1_CHAMPION_CHALLENGER_DOC = PROJECT_ROOT / "docs" / "J1_CHAMPION_CHALLENGER_CONTRACT.md"
J2_CHAMPION_CHALLENGER_DOC = PROJECT_ROOT / "docs" / "J2_CHAMPION_CHALLENGER_CORE.md"
J3_CHAMPION_CHALLENGER_DOC = PROJECT_ROOT / "docs" / "J3_CHAMPION_CHALLENGER_OOS.md"
J4_CHAMPION_CHALLENGER_DOC = PROJECT_ROOT / "docs" / "J4_CHAMPION_CHALLENGER_UI.md"
J5_CHAMPION_CHALLENGER_DOC = PROJECT_ROOT / "docs" / "J5_CHAMPION_CHALLENGER_REGIME_EGT.md"
J6_CHAMPION_CHALLENGER_DOC = PROJECT_ROOT / "docs" / "J6_CHAMPION_CHALLENGER_EXPORT_HANDOFF.md"
J7_TEMPORAL_HEALTH_EGT_V2_DOC = PROJECT_ROOT / "docs" / "J7_TEMPORAL_HEALTH_EGT_V2_CONTRACT.md"
J8_TEMPORAL_HEALTH_EGT_V2_DOC = PROJECT_ROOT / "docs" / "J8_TEMPORAL_HEALTH_EGT_V2_HELPERS.md"
J9_TEMPORAL_HEALTH_EGT_V2_DOC = PROJECT_ROOT / "docs" / "J9_TEMPORAL_HEALTH_EGT_V2_UI.md"
J10_TEMPORAL_HEALTH_EGT_V2_DOC = PROJECT_ROOT / "docs" / "J10_TEMPORAL_HEALTH_EGT_V2_HANDOFF.md"
J11_DIRECTIONAL_COHERENCE_SCORE_DOC = PROJECT_ROOT / "docs" / "J11_DIRECTIONAL_COHERENCE_SCORE.md"
SB1_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB1_STRATEGY_BUILDER_DISCOVERY.md"
SB2_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB2_STRATEGY_BUILDER_WORKFLOW.md"
SB3_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB3_STRATEGY_BUILDER_PROTOTYPE.md"
SB4_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB4_STRATEGY_BUILDER_IMPORT_EXPORT.md"
SB5_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB5_STRATEGY_BUILDER_PROJECT_GENERATOR_PREFILL.md"
SB6_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB6_STRATEGY_BUILDER_PRESET_HANDOFF.md"
SB7_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB7_STRATEGY_BUILDER_VIEWS_HANDOFF.md"
SB8_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB8_STRATEGY_BUILDER_AUDIT_WORKFLOW.md"
SB9_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB9_STRATEGY_BUILDER_CLEANER_HANDOFF.md"
SB10_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB10_STRATEGY_BUILDER_BUYER_HANDOFF_PACK.md"
SB11_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB11_STRATEGY_BUILDER_BUYER_PACK_IMPORT_REVIEW.md"
SB12_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB12_STRATEGY_BUILDER_BUYER_SESSION_CHECKLIST.md"
SB13_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB13_STRATEGY_BUILDER_BUYER_SESSION_SUMMARY_EXPORT.md"
SB14_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB14_STRATEGY_BUILDER_BUYER_SESSION_PRINTABLE_NOTES.md"
SB15_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB15_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_CASE_BUNDLE.md"
SB16_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB16_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_RESOLUTION_CHECKLIST.md"
SB17_STRATEGY_BUILDER_DOC = PROJECT_ROOT / "docs" / "SB17_STRATEGY_BUILDER_EVIDENCE_HANDOFF_INDEX.md"
PG7_PROJECT_GENERATOR_DOC = PROJECT_ROOT / "docs" / "PG7_PROJECT_GENERATOR_BUYER_CFX_HANDOFF.md"
T1_CLOUD_TESTER_DOC = PROJECT_ROOT / "docs" / "T1_CLOUD_TESTER_ARCHITECTURE_CONTRACT.md"
T2_TESTER_PORTAL_DOC = PROJECT_ROOT / "docs" / "T2_TESTER_PORTAL_BOOTSTRAP.md"
T3_TESTER_AUTH_DOC = PROJECT_ROOT / "docs" / "T3_TESTER_AUTH_DATA_CONTRACT.md"
T4_LOGIN_SESSION_DOC = PROJECT_ROOT / "docs" / "T4_LOGIN_SESSION_PROTOTYPE.md"
T5_TESTER_PRO_DOC = PROJECT_ROOT / "docs" / "T5_TESTER_PRO_ENTITLEMENT_GATES.md"
T6_RENEWAL_DOC = PROJECT_ROOT / "docs" / "T6_15_DAY_EXPIRY_RENEWAL_FLOW.md"
T7_ADMIN_CONSOLE_DOC = PROJECT_ROOT / "docs" / "T7_ADMIN_TESTER_CONSOLE.md"
T8_SECURITY_HARDENING_DOC = PROJECT_ROOT / "docs" / "T8_TESTER_PORTAL_SECURITY_HARDENING.md"
T9_VERCEL_PREFLIGHT_DOC = PROJECT_ROOT / "docs" / "T9_PROTECTED_VERCEL_PREVIEW_PREFLIGHT.md"
T9B_VERCEL_ROLLBACK_DOC = PROJECT_ROOT / "docs" / "T9B_VERCEL_PREVIEW_DEPLOY_ROLLBACK.md"
T9C_VERCEL_PROTECTION_GATE_DOC = PROJECT_ROOT / "docs" / "T9C_VERCEL_DEPLOYMENT_PROTECTION_GATE.md"
T9D_VERCEL_AUTH_PROTECTION_DOC = PROJECT_ROOT / "docs" / "T9D_VERCEL_AUTH_PROTECTION_VERIFIED.md"
T9E_PROTECTED_PREVIEW_ROLLBACK_DOC = PROJECT_ROOT / "docs" / "T9E_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md"
T9F_PREVIEW_PATH_PROOF_DOC = PROJECT_ROOT / "docs" / "T9F_PREVIEW_PATH_PROOF.md"
T9G_PRIVATE_GIT_PREVIEW_SOURCE_DOC = PROJECT_ROOT / "docs" / "T9G_PRIVATE_GIT_PREVIEW_SOURCE.md"
T10_INTERNAL_PREVIEW_ROLLBACK_DOC = PROJECT_ROOT / "docs" / "T10_INTERNAL_PREVIEW_ROLLBACK.md"
T10B_VERCEL_TARGET_GUARD_DOC = PROJECT_ROOT / "docs" / "T10B_VERCEL_TARGET_GUARD.md"
T10C_EXPLICIT_API_PREVIEW_PATH_DOC = PROJECT_ROOT / "docs" / "T10C_EXPLICIT_API_PREVIEW_PATH.md"
T10D_EXPLICIT_API_PREVIEW_ROLLBACK_DOC = PROJECT_ROOT / "docs" / "T10D_EXPLICIT_API_PREVIEW_ROLLBACK.md"
T10E_OMITTED_TARGET_PREVIEW_ROLLBACK_DOC = PROJECT_ROOT / "docs" / "T10E_OMITTED_TARGET_PREVIEW_ROLLBACK.md"
T10F_SEPARATED_PREVIEW_PROJECT_DOC = PROJECT_ROOT / "docs" / "T10F_SEPARATED_PREVIEW_PROJECT.md"
T10G_LINKED_PREVIEW_PROJECT_DOC = PROJECT_ROOT / "docs" / "T10G_LINKED_PREVIEW_PROJECT_PROOF.md"
T10H_PROTECTED_PREVIEW_ROLLBACK_DOC = PROJECT_ROOT / "docs" / "T10H_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md"
T10I_CLI_DEFAULT_PREVIEW_ROUTE_DOC = PROJECT_ROOT / "docs" / "T10I_CLI_DEFAULT_PREVIEW_ROUTE.md"
T10J_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK_DOC = PROJECT_ROOT / "docs" / "T10J_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK.md"
T10K_CLI_DEFAULT_PREVIEW_ROLLBACK_DOC = PROJECT_ROOT / "docs" / "T10K_CLI_DEFAULT_PREVIEW_ROLLBACK.md"
T10L_VERCEL_ROUTE_INVESTIGATION_DOC = PROJECT_ROOT / "docs" / "T10L_VERCEL_ROUTE_INVESTIGATION.md"
T10M_VERCEL_CONFIG_HARDENING_DOC = PROJECT_ROOT / "docs" / "T10M_VERCEL_CONFIG_HARDENING.md"
T10N_VERCEL_ROUTE_DECISION_DOC = PROJECT_ROOT / "docs" / "T10N_VERCEL_ROUTE_DECISION.md"
T10O_REPLACEMENT_ROUTE_CONTRACT_DOC = PROJECT_ROOT / "docs" / "T10O_REPLACEMENT_ROUTE_CONTRACT.md"
T10P_FRESH_STAGING_ROUTE_PREFLIGHT_DOC = PROJECT_ROOT / "docs" / "T10P_FRESH_STAGING_ROUTE_PREFLIGHT.md"
T10Q_FRESH_STAGING_ROUTE_ACCESS_CHECK_DOC = PROJECT_ROOT / "docs" / "T10Q_FRESH_STAGING_ROUTE_ACCESS_CHECK.md"
T10R_FRESH_STAGING_PROJECT_CREATED_DOC = PROJECT_ROOT / "docs" / "T10R_FRESH_STAGING_PROJECT_CREATED.md"
T10S_STAGING_PROTECTION_VERIFIED_DOC = PROJECT_ROOT / "docs" / "T10S_STAGING_PROTECTION_VERIFIED.md"
T10T_STAGING_LOCAL_LINK_CONFIGURED_DOC = PROJECT_ROOT / "docs" / "T10T_STAGING_LOCAL_LINK_CONFIGURED.md"
TESTER_PORTAL_TEMPLATE_ROOT = PROJECT_ROOT / "templates" / "SQX_Edge_Tester_Portal"
R45_PUBLICATION_PLAN_DOC = PROJECT_ROOT / "docs" / "R45_CONTROLLED_PUBLICATION_PLAN.md"
R47_CONTROLLED_COMMERCIAL_RELEASE_DOC = PROJECT_ROOT / "docs" / "R47_CONTROLLED_COMMERCIAL_RELEASE.md"
GOVERNANCE_ADR_DOC = PROJECT_ROOT / "docs" / "decisions" / "ADR-0001-specialist-agent-governance.md"
MONETIZATION_ROADMAP_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_ROADMAP.md"
MONETIZATION_M1_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M1.md"
MONETIZATION_M2_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M2.md"
MONETIZATION_M3_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M3.md"
MONETIZATION_M4_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M4.md"
MONETIZATION_M5_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M5.md"
MONETIZATION_M6_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M6.md"
MONETIZATION_M7_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M7.md"
MONETIZATION_M8_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M8.md"
MONETIZATION_M9_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M9.md"
MONETIZATION_M10_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M10.md"
MONETIZATION_M11_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M11.md"
MONETIZATION_M12_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M12.md"
MONETIZATION_M13_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M13.md"
MONETIZATION_M14_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M14.md"
MONETIZATION_M15_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M15.md"
MONETIZATION_M16_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M16.md"
MONETIZATION_M17_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M17.md"
MONETIZATION_M18_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M18.md"
MONETIZATION_M19_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M19.md"
MONETIZATION_M20_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M20.md"
MONETIZATION_M21_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M21.md"
MONETIZATION_M22_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M22.md"
MONETIZATION_M23_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M23.md"
MONETIZATION_M24_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M24.md"
MONETIZATION_M25_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M25.md"
MONETIZATION_M26_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M26.md"
MONETIZATION_M27_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M27.md"
MONETIZATION_M28_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M28.md"
MONETIZATION_M29_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M29.md"
MONETIZATION_M30_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M30.md"
MONETIZATION_M31_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M31.md"
MONETIZATION_M32_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M32.md"
MONETIZATION_M33_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M33.md"
MONETIZATION_M34_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M34.md"
MONETIZATION_M35_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M35.md"
MONETIZATION_M36_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M36.md"
MONETIZATION_M37_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M37.md"
MONETIZATION_M38_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M38.md"
MONETIZATION_M39_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M39.md"
MONETIZATION_M40_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M40.md"
MONETIZATION_M41_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M41.md"
MONETIZATION_M42_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M42.md"
MONETIZATION_M43_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M43.md"
MONETIZATION_M44_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M44.md"
MONETIZATION_M45_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M45.md"
MONETIZATION_M46_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M46.md"
MONETIZATION_M47_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M47.md"
MONETIZATION_M48_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M48.md"
MONETIZATION_M49_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M49.md"
MONETIZATION_M50_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M50.md"
MONETIZATION_M51_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M51.md"
MONETIZATION_M52_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M52.md"
MONETIZATION_M53_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M53.md"
MONETIZATION_M54_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M54.md"
MONETIZATION_M55_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M55.md"
MONETIZATION_M56_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M56.md"
MONETIZATION_M57_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M57.md"
MONETIZATION_M58_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M58.md"
MONETIZATION_M59_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M59.md"
MONETIZATION_M60_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M60.md"
MONETIZATION_M61_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M61.md"
MONETIZATION_M62_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M62.md"
MONETIZATION_M63_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M63.md"
MONETIZATION_M64_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M64.md"
MONETIZATION_M65_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M65.md"
MONETIZATION_M66_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M66.md"
MONETIZATION_M67_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M67.md"
MONETIZATION_M68_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M68.md"
MONETIZATION_M69_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M69.md"
MONETIZATION_M70_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M70.md"
MONETIZATION_M72_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M72.md"
MONETIZATION_M73_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M73.md"
MONETIZATION_M74_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M74.md"
MONETIZATION_M75_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M75.md"
MONETIZATION_M76_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M76.md"
MONETIZATION_M77_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M77.md"
MONETIZATION_M78_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M78.md"
MONETIZATION_M79_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M79.md"
MONETIZATION_M80_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M80.md"
MONETIZATION_M81_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M81.md"
MONETIZATION_M82_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M82.md"
MONETIZATION_M83_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M83.md"
MONETIZATION_M84_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M84.md"
MONETIZATION_M85_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M85.md"
MONETIZATION_M86_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M86.md"
MONETIZATION_M87_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M87.md"
MONETIZATION_M88_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M88.md"
MONETIZATION_M89_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M89.md"
MONETIZATION_M90_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M90.md"
MONETIZATION_M91_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M91.md"
MONETIZATION_M92_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M92.md"
MONETIZATION_M93_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M93.md"
MONETIZATION_M94_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M94.md"
MONETIZATION_M95_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M95.md"
MONETIZATION_M96_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M96.md"
MONETIZATION_M97_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M97.md"
MONETIZATION_M98_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M98.md"
MONETIZATION_M99_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M99.md"


class DashboardStaticTestCase(unittest.TestCase):
    def setUp(self):
        self.html_path = APP_ROOT / "SQX_Dashboard_v6.html"
        self.html = self.html_path.read_text(encoding="utf-8-sig")

    def assert_public_redaction_pointer(self, path):
        text = path.read_text(encoding="utf-8-sig")
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        lowered = text.lower()
        self.assertTrue(
            "public redaction" in lowered or "public_redaction" in lowered or "publicredaction" in lowered,
            text,
        )
        self.assertIn(rel.lower(), lowered)
        self.assertIn("https://github.com/cryptoleon78/sqx-edge-commercial-private", lowered)
        self.assertIn("ed79719", lowered)

    def test_script_files_exist_in_expected_order(self):
        scripts = re.findall(r'<script\s+src="([^"]+)"', self.html)
        self.assertEqual(
            scripts,
            [
                "js/historical-data.js",
                "js/scores-data.js",
                "js/manifest-data.js",
                "js/app-config.js",
                "js/modules/core.js",
                "js/modules/config.js",
                "js/modules/storage.js",
                "js/modules/state-backup.js",
                "js/modules/license.js",
                "js/modules/ui.js",
                "js/modules/formatters.js",
                "js/modules/champion-challenger-core.js",
                "js/modules/domain.js",
                "js/modules/datasets.js",
                "js/modules/champion-challenger-regime.js",
                "js/modules/champion-challenger.js",
                "js/modules/strategy-builder-core.js",
                "js/modules/strategy-builder.js",
                "js/modules/renderers.js",
                "js/modules/charts.js",
                "js/modules/strategies.js",
                "js/modules/analyzer.js",
                "js/modules/home.js",
                "js/modules/mtf-evidence.js",
                "js/modules/support.js",
                "js/modules/fulfillment.js",
                "js/modules/customer-cockpit.js",
                "js/modules/workflow.js",
                "js/modules/view-creator.js",
                "js/modules/project-generator-core.js",
                "js/modules/project-generator-config.js",
                "js/modules/project-generator-dom.js",
                "js/modules/project-generator-bindings.js",
                "js/modules/project-generator-renderers.js",
                "js/modules/project-generator-status.js",
                "js/modules/project-generator-cleaner.js",
                "js/modules/project-generator.js",
                "js/modules/index.js",
                "js/data.js",
                "js/dashboard.js",
                "js/main.js",
                "js/project-generator-main.js",
            ],
        )
        for script in scripts:
            self.assertTrue((APP_ROOT / script).is_file(), script)

    def test_architecture_doc_matches_dashboard_load_order(self):
        scripts = re.findall(r'<script\s+src="([^"]+)"', self.html)
        architecture = ARCHITECTURE_DOC.read_text(encoding="utf-8-sig")
        match = re.search(
            r"## Frontend Load Order\s+.*?(?=\n## )",
            architecture,
            flags=re.S,
        )
        self.assertIsNotNone(match, "ARCHITECTURE.md is missing Frontend Load Order section")
        documented_scripts = re.findall(r"^\d+\.\s+`([^`]+)`", match.group(0), flags=re.M)

        self.assertEqual(documented_scripts, scripts)

    def test_project_governance_defines_agent_ownership_and_m46_entry(self):
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        adr = GOVERNANCE_ADR_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        codeowners = (PROJECT_ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8-sig")
        institutional_auditor = (PROJECT_ROOT / ".github" / "workflows" / "institutional-auditor.yml").read_text(encoding="utf-8-sig")
        leakage_monitor = (PROJECT_ROOT / ".github" / "workflows" / "leakage-monitor.yml").read_text(encoding="utf-8-sig")
        operational_discipline = (PROJECT_ROOT / "DISCIPLINA_OPERATIVA.md").read_text(encoding="utf-8-sig")

        for pattern in (
            "G1 - Specialist Agent Operating Model",
            "G2 - Governance Lookup Before Work",
            "G3 - Internal Automation and Agent Gate",
            "G4 - Institutional Core Repository Gate",
            "G5 - Institutional Core Synchronized Gate",
            "G6 - Institutional Dashboard Quick Actions Gate",
            "Access/Security Gatekeeper",
            "Frontend/UI",
            "Backend/API",
            "QA/Release",
            "Monetization/Product",
            "Security/Distribution",
            "Architecture/Docs",
            "M46 Entry Criteria",
            "Before every work phase/message",
            "Specialist Agents ownership matrix",
            "active ownership",
            "Customer cockpit source of truth",
            "no license payloads",
            "Use prefixed phase IDs",
            "Internal Automation Risk Levels",
            "Agent And Command Matrix",
            "Local Tooling Notes",
            "Optional but useful for upcoming release/CI automation: GitHub CLI `gh`",
            "Every new internal automation must declare its risk level",
            "External action",
            "`SBxx`: Strategy Builder and \"only one platform\" workflow phases.",
            "`Txx`: cloud tester access",
            "Never commit `backend/sqx-edge-tool/config/license.json`",
            "https://github.com/CryptoLeon78/SQX_Institutional_Core.git",
            "local remote name `institutional`",
            "Never force-push `institutional/main`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "ADR-0001",
            "Status: Accepted",
            "Frontend/UI",
            "Mxx",
            "G1: Specialist Agent Operating Model",
            "G2 extends the baseline",
            "G3 extends the baseline",
            "consult `docs/PROJECT_GOVERNANCE.md`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, adr)

        self.assertIn("Phase G1: define specialist agent ownership, phase namespaces, workflow and M46 entry criteria. Done.", next_steps)
        self.assertIn("Phase G2: require governance/ownership lookup before each work phase/message. Done.", next_steps)
        self.assertIn("Phase G3: define internal automation risk levels, specialist-agent escalation rules, command matrix and local tooling notes. Done.", next_steps)
        self.assertIn("Phase G4: add Institutional Core as first-class repository discipline with separate non-destructive push rules. Done.", next_steps)
        self.assertIn("Phase G5: reconcile `institutional/main` with current `main`", next_steps)
        self.assertIn("Phase G6: selectively integrate `institutional/feat/dashboard-quick-actions`", next_steps)
        self.assertIn("Governance baseline: G6 - Institutional Dashboard Quick Actions Gate.", next_steps)
        self.assertIn("Phase T1: define the Vercel-hosted tester architecture contract", next_steps)
        self.assertIn("Phase T2: create/private-bootstrap `SQX_Edge_Tester_Portal`", next_steps)
        self.assertIn("Phase T3: define tester auth data contract", next_steps)
        self.assertIn("Any new visible tab, panel, module or manifest-driven UI state", architecture := ARCHITECTURE_DOC.read_text(encoding="utf-8-sig"))
        self.assertIn("docs/PROJECT_GOVERNANCE.md", readme)
        self.assertIn("consulta obligatoria antes de fases/mensajes de trabajo", readme)
        self.assertIn("incluye G4 para tratar `SQX_Institutional_Core`", readme)
        self.assertIn("/app/js/modules/analyzer.js", codeowners)
        self.assertIn("Institutional Quality Auditor", institutional_auditor)
        self.assertIn("git merge-base --is-ancestor", leakage_monitor)
        self.assertIn("ramas `codex/*`", operational_discipline)

    def test_operational_discipline_pushes_after_commit(self):
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        expected = "Push immediately after every successful commit unless the user explicitly asks to hold the push or the remote is unavailable."
        self.assertIn(expected, governance)
        self.assertIn(expected, next_steps)
        self.assertIn("push separately to `institutional` only when the remote is aligned", governance)
        self.assertIn("Never force-push `institutional/main`", next_steps)

    def test_champion_challenger_contract_is_documented_before_runtime(self):
        contract = J1_CHAMPION_CHALLENGER_DOC.read_text(encoding="utf-8-sig")
        j2 = J2_CHAMPION_CHALLENGER_DOC.read_text(encoding="utf-8-sig")
        j3 = J3_CHAMPION_CHALLENGER_DOC.read_text(encoding="utf-8-sig")
        j4 = J4_CHAMPION_CHALLENGER_DOC.read_text(encoding="utf-8-sig")
        j5 = J5_CHAMPION_CHALLENGER_DOC.read_text(encoding="utf-8-sig")
        j6 = J6_CHAMPION_CHALLENGER_DOC.read_text(encoding="utf-8-sig")
        j7 = J7_TEMPORAL_HEALTH_EGT_V2_DOC.read_text(encoding="utf-8-sig")
        j8 = J8_TEMPORAL_HEALTH_EGT_V2_DOC.read_text(encoding="utf-8-sig")
        j9 = J9_TEMPORAL_HEALTH_EGT_V2_DOC.read_text(encoding="utf-8-sig")
        j10 = J10_TEMPORAL_HEALTH_EGT_V2_DOC.read_text(encoding="utf-8-sig")
        j11 = J11_DIRECTIONAL_COHERENCE_SCORE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        comparison = (PROJECT_ROOT / "docs" / "EXTERNAL_REPO_COMPARISON_JOSE.md").read_text(encoding="utf-8-sig")

        for pattern in (
            "J1 Champion vs Challenger Contract",
            "No `Top Picks` tab, block or headline.",
            "No `Matriz Completa` tab, heatmap tab or heatmap panel.",
            "Pure parsing and scoring logic first, without DOM access.",
            "Do not use imported names as DOM IDs without normalization.",
            "CSV parser handles comma, semicolon, quotes and escaped quotes.",
            "`J2` - Pure parser, alias resolver and formal comparison core with tests.",
            "No copied Jose code.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, contract)

        for pattern in (
            "Phase J1: document the Champion vs Challenger integration contract",
            "Phase J2: implement the pure parser, alias resolver and formal comparison core with contracts",
            "Phase J3: add OOS block parsing and stability scoring with contracts",
            "Phase J4: add native dashboard UI using the current SQX module architecture",
            "Phase J5: add regime/EGT evidence through first-party historical-data adapters",
            "Phase J6: add export and future Strategy Builder handoff",
            "Phase J7: document the Temporal Health and EGT v2 contract",
            "Phase J8: implement pure Temporal Health and EGT v2 helpers",
            "Phase J9: add compact dashboard chips and optional filters",
            "Phase J10: extend redacted review export and Strategy Builder handoff",
            "Phase J11: add native direction detection, directional coherence, Score Pro",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        self.assertIn("`Jxx`: Jose-derived selective integrations", governance)
        self.assertIn("docs/J1_CHAMPION_CHALLENGER_CONTRACT.md", governance)
        self.assertIn("docs/J2_CHAMPION_CHALLENGER_CORE.md", governance)
        self.assertIn("docs/J3_CHAMPION_CHALLENGER_OOS.md", governance)
        self.assertIn("docs/J4_CHAMPION_CHALLENGER_UI.md", governance)
        self.assertIn("docs/J5_CHAMPION_CHALLENGER_REGIME_EGT.md", governance)
        self.assertIn("docs/J6_CHAMPION_CHALLENGER_EXPORT_HANDOFF.md", governance)
        self.assertIn("docs/J7_TEMPORAL_HEALTH_EGT_V2_CONTRACT.md", governance)
        self.assertIn("docs/J8_TEMPORAL_HEALTH_EGT_V2_HELPERS.md", governance)
        self.assertIn("docs/J9_TEMPORAL_HEALTH_EGT_V2_UI.md", governance)
        self.assertIn("docs/J10_TEMPORAL_HEALTH_EGT_V2_HANDOFF.md", governance)
        self.assertIn("docs/J11_DIRECTIONAL_COHERENCE_SCORE.md", governance)
        self.assertIn("Phase J1 starts the selective Champion vs Challenger track", comparison)
        self.assertIn("Phase J2 implements the first native Champion vs Challenger core", comparison)
        self.assertIn("Phase J3 adds the OOS stability layer", comparison)
        self.assertIn("Phase J4 exposes the comparison workflow as native SQX dashboard UI", comparison)
        self.assertIn("Phase J5 adds first-party Regime/EGT evidence", comparison)
        self.assertIn("Phase J6 closes the first Champion vs Challenger integration track", comparison)
        self.assertIn("Phase J7 documents the latest JoseLivan improvement", comparison)
        self.assertIn("Phase J8 implements that contract as native pure helpers", comparison)
        self.assertIn("Phase J9 exposes the J8 evidence in the existing dashboard", comparison)
        self.assertIn("Phase J10 carries the J9 evidence into safe payloads", comparison)
        self.assertIn("Phase J11 adapts JoseLivan commit `ff73a66`", comparison)

        for pattern in (
            "J11 Directional Coherence and Score Pro",
            "`SQX.championChallengerCore.detectDirection(record)`",
            "`SQX.championChallengerRegime.assessDirectionalCoherence",
            "No `Top Picks` tab, block, headline",
            "No `Matriz Completa`, matrix tab, heatmap tab",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j11)

        for pattern in (
            "J2 Champion vs Challenger Core",
            "`SQX.championChallengerCore`",
            "No dashboard UI was added.",
            "Duplicate aliases are warnings, not silent overwrites.",
            "XSS-like strategy names rendered as text.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j2)

        for pattern in (
            "J3 Champion vs Challenger OOS Stability",
            "`CAGR/Max DD (OOS1)`",
            "`stable_enough` requires at least `defaultMinOosBlocks`",
            "No dashboard UI was added.",
            "missing OOS metric-column rejection.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j3)

        for pattern in (
            "J4 Champion vs Challenger Dashboard UI",
            "`SQX.championChallenger`",
            "`tab-cvc`",
            "No `Top Picks` tab, block or headline.",
            "No `Matriz Completa` tab, heatmap tab or heatmap panel.",
            "The UI stores no CSV payloads in localStorage.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j4)

        for pattern in (
            "J5 Champion vs Challenger Regime/EGT Evidence",
            "`SQX.championChallengerRegime`",
            "`SQX_HISTORICAL_DATA`",
            "`SQX_SCORES_DATA`",
            "`COMPLIANT`",
            "`RISK`",
            "`FLAT`",
            "`UNKNOWN`",
            "contextual evidence, not final truth",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j5)

        for pattern in (
            "J6 Champion vs Challenger Export and Strategy Builder Handoff",
            "`SQX.championChallenger`",
            "`buildReviewExport(model)`",
            "`buildStrategyBuilderHandoff(reviewOrModel)`",
            "No raw CSV payloads.",
            "No remote calls.",
            "No automatic localStorage writes.",
            "No `Matriz Completa`, matrix tab or heatmap panel restoration.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j6)

        for pattern in (
            "J7 Temporal Health and EGT v2 Contract",
            "`06767d8eef597987530f152d54860ab96e590ffa`",
            "`fresh`, `recovered`, `old_peak`, `declining`, `unknown`",
            "`STRONG`, `COMPLIANT`, `DEFENSIVE`, `INSUFFICIENT`, `RISK`, `UNKNOWN`",
            "`min_blocks_per_regime`",
            "`temporal_health_metric_fallback`",
            "Do not use a hard `Stagnation < X days` promotion filter.",
            "No copied Jose runtime code.",
            "No automatic promotion decision.",
            "No `Top Picks` tab, Top Picks block, matrix tab, full matrix, heatmap tab or heatmap panel.",
            "`J8` - implement pure Temporal Health and EGT v2 helpers with JS contracts.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j7)

        for pattern in (
            "J8 Temporal Health and EGT v2 Helpers",
            "`SQX.championChallengerCore.computeTemporalHealth(oosRecord, options)`",
            "`SQX.championChallengerRegime.assessEgtV2(oosRecord, regimeBlocks, options)`",
            "`temporal_health_metric_fallback`",
            "`STRONG`, `COMPLIANT`, `DEFENSIVE`, `INSUFFICIENT`, `RISK` or `UNKNOWN`",
            "No dashboard rendering, backend endpoint, persistence or buyer-facing claim is added in J8.",
            "No `Top Picks` tab, Top Picks block, matrix tab, full matrix, heatmap tab or heatmap panel.",
            "`J9` - add compact dashboard chips and optional filters using these helpers.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j8)

        for pattern in (
            "J9 Temporal Health and EGT v2 UI",
            "`Health OK`",
            "`EGT v2 OK`",
            "`cvc-filter-health-ok`",
            "`cvc-filter-egt-v2-ok`",
            "`Health fresh`",
            "`EGT v2 STRONG`",
            "`STRONG`, `COMPLIANT` and `DEFENSIVE` count as EGT v2 OK",
            "No export payload changes.",
            "No Strategy Builder handoff changes.",
            "No `Top Picks` tab, Top Picks block, matrix tab, full matrix, heatmap tab or heatmap panel.",
            "`J10` should extend the redacted review export",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j9)

        for pattern in (
            "J10 Temporal Health and EGT v2 Export Handoff",
            "`buildReviewExport(model)` includes reduced `temporal_health` and `egt_v2` fields",
            "`temporal_health_ok_count` and `egt_v2_ok_count`",
            "`source_summary` and `asset_profile.cvc_evidence_summary`",
            "No `metrics_by_block` export.",
            "No historical price series export.",
            "No regime block payload export.",
            "No automatic StrategyQuant generation.",
            "No automatic promotion decision.",
            "`J11` can make Strategy Builder's UI display the imported reduced evidence",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, j10)

    def test_strategy_builder_discovery_is_documented_before_runtime(self):
        sb1 = SB1_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb2 = SB2_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb3 = SB3_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb4 = SB4_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb5 = SB5_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb6 = SB6_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb7 = SB7_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb8 = SB8_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb9 = SB9_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb10 = SB10_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb11 = SB11_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb12 = SB12_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb13 = SB13_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb14 = SB14_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb15 = SB15_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb16 = SB16_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        sb17 = SB17_STRATEGY_BUILDER_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")

        for pattern in (
            "SB1 Strategy Builder Discovery",
            "minimum viable Strategy Builder scope",
            "only one platform",
            "This phase is discovery and contract work only.",
            "The buyer-facing promise is not \"the app prints profitable strategies\".",
            "Champion vs Challenger",
            "`sqx-edge.strategy-builder-handoff`",
            "Project Generator",
            "SQX Views",
            "Plan Quality / MTF evidence",
            "Strategy Cleaner",
            "`sqx-edge.strategy-builder-scope`",
            "`sqx-edge.strategy-builder-package`",
            "No auto-trading.",
            "No promise of profitability.",
            "No remote AI calls with strategy data.",
            "No Top Picks or matrix/heatmap restoration.",
            "SB2 should design the workflow before UI",
            "No frontend, backend or packaging behavior changes in SB1.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb1)

        for pattern in (
            "SB2 Strategy Builder Controlled Workflow Design",
            "This phase is workflow and contract design only.",
            "`source_selected`",
            "`context_resolved`",
            "`idea_framed`",
            "`validation_planned`",
            "`handoff_prepared`",
            "`operator_reviewed`",
            "`package_exportable`",
            "`blocked_missing_source`",
            "`blocked_claims_boundary`",
            "`blank`",
            "`cvc_handoff`",
            "`project_generator_profile`",
            "`views_workflow`",
            "Every mode must resolve to the same internal context shape.",
            "`sqx-edge.strategy-builder-package`",
            "`indicator_family_candidates`",
            "`blocked_claims`",
            "Accept J6 reduced summary only.",
            "Preserve custom project freedom outside plan mining.",
            "StrategyQuant settings will be reviewed manually",
            "`app/js/modules/strategy-builder-core.js`",
            "No frontend, backend or packaging behavior changes in SB2.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb2)

        for pattern in (
            "SB3 Strategy Builder Read-Only Prototype",
            "`app/js/modules/strategy-builder-core.js`",
            "`app/js/modules/strategy-builder.js`",
            "`Strategy Builder` tab",
            "`sqx-edge.strategy-builder-package`",
            "No backend endpoint.",
            "No remote calls.",
            "No generated trading logic.",
            "No Top Picks restoration.",
            "No matrix/heatmap restoration.",
            "`SQX.strategyBuilderCore`",
            "`SQX.strategyBuilder`",
            "`loadCvcSample`",
            "E2E smoke opens the Strategy Builder tab",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb3)

        for pattern in (
            "SB4 Strategy Builder Import/Export Hardening",
            "`importPayload`",
            "`validateImportPayload`",
            "Imported packages are re-built through the same core contract",
            "The dashboard remains a dedicated tab.",
            "No backend endpoint.",
            "No remote calls.",
            "No Top Picks restoration.",
            "No matrix/heatmap restoration.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb4)

        for pattern in (
            "SB5 Strategy Builder to Project Generator Prefill",
            "`projectGeneratorPrefillFromPackage`",
            "`sendToProjectGenerator`",
            "Prefill only.",
            "No backend endpoint.",
            "No API call.",
            "No automatic generation.",
            "The operator must press `Generar custom` manually.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb5)

        for pattern in (
            "SB6 Strategy Builder Review Checklist and Preset Handoff",
            "`reviewChecklistSummary`",
            "`projectGeneratorPresetDraftFromPackage`",
            "`prepareProjectGeneratorPreset`",
            "No automatic preset save.",
            "No backend endpoint.",
            "No API call.",
            "The operator must press `Guardar preset` manually.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb6)

        for pattern in (
            "SB7 Strategy Builder SQX Views Handoff",
            "`sqxViewsHandoffFromPackage`",
            "`sendToViews`",
            "No automatic template save.",
            "No backend endpoint.",
            "No API call.",
            "The operator must press",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb7)

        for pattern in (
            "SB8 Strategy Builder Audit Trail and Buyer Workflow Polish",
            "`buyerWorkflowSummary`",
            "`handoffAuditEntry`",
            "No hidden localStorage write.",
            "No backend endpoint.",
            "No API call.",
            "The operator must press every final destination action manually.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb8)

        for pattern in (
            "SB9 Strategy Builder Strategy Cleaner Draft Handoff",
            "`strategyCleanerDraftFromPackage`",
            "`prepareStrategyCleaner`",
            "No folder scan triggered.",
            "No `.sqx` file mutation.",
            "No automatic cleanup.",
            "The operator must press `Escanear` and `Procesar seleccion` manually.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb9)

        for pattern in (
            "SB10 Strategy Builder Unified Buyer Handoff Pack",
            "`unifiedBuyerHandoffPackFromPackage`",
            "`prepareBuyerHandoffPack`",
            "`sqx-edge.strategy-builder-buyer-handoff-pack`",
            "No backend endpoint.",
            "No API call.",
            "No destination action is triggered.",
            "The operator must execute each destination manually.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb10)

        for pattern in (
            "SB11 Strategy Builder Buyer Handoff Pack Import and Review",
            "`buyerHandoffPackReview`",
            "`sqx-edge.strategy-builder-buyer-handoff-pack-review`",
            "No backend endpoint.",
            "No API call.",
            "No destination action is triggered.",
            "Imported buyer packs are review-only until the operator confirms manual review.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb11)

        for pattern in (
            "SB12 Strategy Builder Guided Buyer Session Checklist",
            "`guidedBuyerSessionChecklist`",
            "`prepareBuyerSessionChecklist`",
            "`sqx-edge.strategy-builder-buyer-session-checklist`",
            "No backend endpoint.",
            "No API call.",
            "No destination action is triggered.",
            "The operator executes every step manually.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb12)

        for pattern in (
            "SB13 Strategy Builder Buyer Session Handoff Summary Export",
            "`buyerSessionHandoffSummary`",
            "`exportBuyerSessionSummary`",
            "`sqx-edge.strategy-builder-buyer-session-summary`",
            "No backend endpoint.",
            "No API call.",
            "No destination action is triggered.",
            "No hidden localStorage write.",
            "No buyer identity.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb13)

        for pattern in (
            "SB14 Strategy Builder Buyer Session Printable Operator Notes",
            "`buyerSessionOperatorNotes`",
            "`prepareBuyerSessionNotes`",
            "`sqx-edge.strategy-builder-buyer-session-notes`",
            "No backend endpoint.",
            "No API call.",
            "No destination action is triggered.",
            "No automatic browser print dialog.",
            "No hidden localStorage write.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb14)

        for pattern in (
            "SB15 Strategy Builder Buyer Session Support Case Bundle",
            "`buyerSessionSupportCaseBundle`",
            "`exportBuyerSupportCaseBundle`",
            "`sqx-edge.strategy-builder-buyer-session-support-case-bundle`",
            "No backend endpoint.",
            "No API call.",
            "No remote ticket is created.",
            "No hidden localStorage write.",
            "No full Strategy Builder package by default.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb15)

        for pattern in (
            "SB16 Strategy Builder Buyer Session Support Resolution Checklist",
            "`buyerSessionSupportResolutionChecklist`",
            "`prepareBuyerResolutionChecklist`",
            "`sqx-edge.strategy-builder-buyer-session-support-resolution-checklist`",
            "No backend endpoint.",
            "No API call.",
            "No remote ticket is created or changed.",
            "No hidden localStorage write.",
            "No profitability claim.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb16)

        for pattern in (
            "SB17 Strategy Builder Buyer Session Evidence Handoff Index",
            "`handoffEvidenceIndex`",
            "`prepareEvidenceHandoffIndex`",
            "`sqx-edge.strategy-builder-evidence-handoff-index`",
            "No backend endpoint.",
            "No API call.",
            "No remote ticket is created or changed.",
            "No hidden localStorage write.",
            "No raw CSV payloads.",
            "No profitability claim.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, sb17)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("M100 - execute exactly the M99-approved controlled commercial movement", governance)
        self.assertIn("Current product/commercial state: `next_controlled_commercial_movement_from_m98_decision_ready`.", governance)
        self.assertIn("The institutional analyzer is exposed as a normal SQX tab", governance)
        self.assertIn("Asset detail/category rows expose quick actions", governance)
        self.assertIn("docs/PG7_PROJECT_GENERATOR_BUYER_CFX_HANDOFF.md", governance)
        self.assertIn("docs/T1_CLOUD_TESTER_ARCHITECTURE_CONTRACT.md", governance)
        self.assertIn("docs/T2_TESTER_PORTAL_BOOTSTRAP.md", governance)
        self.assertIn("docs/T3_TESTER_AUTH_DATA_CONTRACT.md", governance)
        self.assertIn("docs/T4_LOGIN_SESSION_PROTOTYPE.md", governance)
        self.assertIn("docs/T5_TESTER_PRO_ENTITLEMENT_GATES.md", governance)
        self.assertIn("docs/T6_15_DAY_EXPIRY_RENEWAL_FLOW.md", governance)
        self.assertIn("docs/T7_ADMIN_TESTER_CONSOLE.md", governance)
        self.assertIn("docs/T8_TESTER_PORTAL_SECURITY_HARDENING.md", governance)
        self.assertIn("docs/T9_PROTECTED_VERCEL_PREVIEW_PREFLIGHT.md", governance)
        self.assertIn("templates/SQX_Edge_Tester_Portal/", governance)
        self.assertIn("`SBxx`: Strategy Builder and \"only one platform\" workflow phases.", governance)
        self.assertIn("docs/SB1_STRATEGY_BUILDER_DISCOVERY.md", governance)
        self.assertIn("docs/SB2_STRATEGY_BUILDER_WORKFLOW.md", governance)
        self.assertIn("docs/SB3_STRATEGY_BUILDER_PROTOTYPE.md", governance)
        self.assertIn("docs/SB4_STRATEGY_BUILDER_IMPORT_EXPORT.md", governance)
        self.assertIn("docs/SB5_STRATEGY_BUILDER_PROJECT_GENERATOR_PREFILL.md", governance)
        self.assertIn("docs/SB6_STRATEGY_BUILDER_PRESET_HANDOFF.md", governance)
        self.assertIn("docs/SB7_STRATEGY_BUILDER_VIEWS_HANDOFF.md", governance)
        self.assertIn("docs/SB8_STRATEGY_BUILDER_AUDIT_WORKFLOW.md", governance)
        self.assertIn("docs/SB9_STRATEGY_BUILDER_CLEANER_HANDOFF.md", governance)
        self.assertIn("docs/SB10_STRATEGY_BUILDER_BUYER_HANDOFF_PACK.md", governance)
        self.assertIn("docs/SB11_STRATEGY_BUILDER_BUYER_PACK_IMPORT_REVIEW.md", governance)
        self.assertIn("docs/SB12_STRATEGY_BUILDER_BUYER_SESSION_CHECKLIST.md", governance)
        self.assertIn("docs/SB13_STRATEGY_BUILDER_BUYER_SESSION_SUMMARY_EXPORT.md", governance)
        self.assertIn("docs/SB14_STRATEGY_BUILDER_BUYER_SESSION_PRINTABLE_NOTES.md", governance)
        self.assertIn("docs/SB15_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_CASE_BUNDLE.md", governance)
        self.assertIn("docs/SB16_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_RESOLUTION_CHECKLIST.md", governance)
        self.assertIn("docs/SB17_STRATEGY_BUILDER_EVIDENCE_HANDOFF_INDEX.md", governance)
        self.assertIn("app/js/modules/strategy-builder-core.js", governance)
        self.assertIn("app/js/modules/strategy-builder.js", governance)
        self.assertIn("Phase SB1: discover the minimum viable Strategy Builder scope", next_steps)
        self.assertIn("Done; see `docs/SB1_STRATEGY_BUILDER_DISCOVERY.md`", next_steps)
        self.assertIn("Phase SB2: design a controlled Builder flow", next_steps)
        self.assertIn("Done; see `docs/SB2_STRATEGY_BUILDER_WORKFLOW.md`", next_steps)
        self.assertIn("Phase SB3: prototype read-only previews", next_steps)
        self.assertIn("Done; see `docs/SB3_STRATEGY_BUILDER_PROTOTYPE.md`", next_steps)
        self.assertIn("Phase SB4: harden Strategy Builder handoff import/export", next_steps)
        self.assertIn("Done; see `docs/SB4_STRATEGY_BUILDER_IMPORT_EXPORT.md`", next_steps)
        self.assertIn("Phase SB5: add Strategy Builder to Project Generator prefill bridge", next_steps)
        self.assertIn("Done; see `docs/SB5_STRATEGY_BUILDER_PROJECT_GENERATOR_PREFILL.md`", next_steps)
        self.assertIn("Phase SB6: add Strategy Builder review checklist and Project Generator save-as-preset handoff", next_steps)
        self.assertIn("Done; see `docs/SB6_STRATEGY_BUILDER_PRESET_HANDOFF.md`", next_steps)
        self.assertIn("Phase SB7: add Strategy Builder SQX Views validation-pack handoff", next_steps)
        self.assertIn("Done; see `docs/SB7_STRATEGY_BUILDER_VIEWS_HANDOFF.md`", next_steps)
        self.assertIn("Phase SB8: add Strategy Builder handoff audit trail and buyer workflow polish", next_steps)
        self.assertIn("Done; see `docs/SB8_STRATEGY_BUILDER_AUDIT_WORKFLOW.md`", next_steps)
        self.assertIn("Phase SB9: add Strategy Builder Strategy Cleaner draft handoff", next_steps)
        self.assertIn("Done; see `docs/SB9_STRATEGY_BUILDER_CLEANER_HANDOFF.md`", next_steps)
        self.assertIn("Phase SB10: add Strategy Builder unified buyer handoff pack", next_steps)
        self.assertIn("Done; see `docs/SB10_STRATEGY_BUILDER_BUYER_HANDOFF_PACK.md`", next_steps)
        self.assertIn("Phase SB11: add Strategy Builder buyer handoff pack import and review", next_steps)
        self.assertIn("Done; see `docs/SB11_STRATEGY_BUILDER_BUYER_PACK_IMPORT_REVIEW.md`", next_steps)
        self.assertIn("Phase SB12: add Strategy Builder guided buyer session checklist", next_steps)
        self.assertIn("Done; see `docs/SB12_STRATEGY_BUILDER_BUYER_SESSION_CHECKLIST.md`", next_steps)
        self.assertIn("Phase SB13: add Strategy Builder buyer session handoff summary export", next_steps)
        self.assertIn("Done; see `docs/SB13_STRATEGY_BUILDER_BUYER_SESSION_SUMMARY_EXPORT.md`", next_steps)
        self.assertIn("Phase SB14: add Strategy Builder buyer session printable operator notes", next_steps)
        self.assertIn("Done; see `docs/SB14_STRATEGY_BUILDER_BUYER_SESSION_PRINTABLE_NOTES.md`", next_steps)
        self.assertIn("Phase SB15: add Strategy Builder buyer session support case bundle", next_steps)
        self.assertIn("Done; see `docs/SB15_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_CASE_BUNDLE.md`", next_steps)
        self.assertIn("Phase SB16: add Strategy Builder buyer session support resolution checklist", next_steps)
        self.assertIn("Done; see `docs/SB16_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_RESOLUTION_CHECKLIST.md`", next_steps)
        self.assertIn("Phase SB17: add Strategy Builder buyer session evidence handoff index", next_steps)
        self.assertIn("Done; see `docs/SB17_STRATEGY_BUILDER_EVIDENCE_HANDOFF_INDEX.md`", next_steps)
        self.assertIn("Phase SB18: add Strategy Builder buyer evidence export polish", next_steps)

    def test_modular_scaffold_loads_before_legacy_logic(self):
        scripts = re.findall(r'<script\s+src="([^"]+)"', self.html)
        module_scripts = [
            "js/modules/core.js",
            "js/modules/config.js",
            "js/modules/storage.js",
            "js/modules/state-backup.js",
            "js/modules/license.js",
            "js/modules/ui.js",
            "js/modules/formatters.js",
            "js/modules/champion-challenger-core.js",
            "js/modules/domain.js",
            "js/modules/datasets.js",
            "js/modules/champion-challenger-regime.js",
            "js/modules/champion-challenger.js",
            "js/modules/strategy-builder-core.js",
            "js/modules/strategy-builder.js",
            "js/modules/renderers.js",
            "js/modules/charts.js",
            "js/modules/strategies.js",
            "js/modules/analyzer.js",
            "js/modules/home.js",
            "js/modules/mtf-evidence.js",
            "js/modules/support.js",
            "js/modules/fulfillment.js",
            "js/modules/customer-cockpit.js",
            "js/modules/workflow.js",
            "js/modules/view-creator.js",
            "js/modules/project-generator-core.js",
            "js/modules/project-generator-config.js",
            "js/modules/project-generator-dom.js",
            "js/modules/project-generator-bindings.js",
            "js/modules/project-generator-renderers.js",
            "js/modules/project-generator-status.js",
            "js/modules/project-generator-cleaner.js",
            "js/modules/project-generator.js",
            "js/modules/index.js",
        ]

        for script in module_scripts:
            with self.subTest(script=script):
                self.assertLess(scripts.index(script), scripts.index("js/data.js"))

        core_js = (APP_ROOT / "js" / "modules" / "core.js").read_text(encoding="utf-8-sig")
        config_js = (APP_ROOT / "js" / "modules" / "config.js").read_text(encoding="utf-8-sig")
        storage_js = (APP_ROOT / "js" / "modules" / "storage.js").read_text(encoding="utf-8-sig")
        state_backup_js = (APP_ROOT / "js" / "modules" / "state-backup.js").read_text(encoding="utf-8-sig")
        license_js = (APP_ROOT / "js" / "modules" / "license.js").read_text(encoding="utf-8-sig")
        ui_js = (APP_ROOT / "js" / "modules" / "ui.js").read_text(encoding="utf-8-sig")
        formatters_js = (APP_ROOT / "js" / "modules" / "formatters.js").read_text(encoding="utf-8-sig")
        champion_core_js = (APP_ROOT / "js" / "modules" / "champion-challenger-core.js").read_text(encoding="utf-8-sig")
        champion_ui_js = (APP_ROOT / "js" / "modules" / "champion-challenger.js").read_text(encoding="utf-8-sig")
        strategy_builder_core_js = (APP_ROOT / "js" / "modules" / "strategy-builder-core.js").read_text(encoding="utf-8-sig")
        strategy_builder_js = (APP_ROOT / "js" / "modules" / "strategy-builder.js").read_text(encoding="utf-8-sig")
        domain_js = (APP_ROOT / "js" / "modules" / "domain.js").read_text(encoding="utf-8-sig")
        datasets_js = (APP_ROOT / "js" / "modules" / "datasets.js").read_text(encoding="utf-8-sig")
        champion_regime_js = (APP_ROOT / "js" / "modules" / "champion-challenger-regime.js").read_text(encoding="utf-8-sig")
        renderers_js = (APP_ROOT / "js" / "modules" / "renderers.js").read_text(encoding="utf-8-sig")
        charts_js = (APP_ROOT / "js" / "modules" / "charts.js").read_text(encoding="utf-8-sig")
        strategies_js = (APP_ROOT / "js" / "modules" / "strategies.js").read_text(encoding="utf-8-sig")
        analyzer_js = (APP_ROOT / "js" / "modules" / "analyzer.js").read_text(encoding="utf-8-sig")
        home_js = (APP_ROOT / "js" / "modules" / "home.js").read_text(encoding="utf-8-sig")
        mtf_evidence_js = (APP_ROOT / "js" / "modules" / "mtf-evidence.js").read_text(encoding="utf-8-sig")
        support_js = (APP_ROOT / "js" / "modules" / "support.js").read_text(encoding="utf-8-sig")
        fulfillment_js = (APP_ROOT / "js" / "modules" / "fulfillment.js").read_text(encoding="utf-8-sig")
        customer_cockpit_js = (APP_ROOT / "js" / "modules" / "customer-cockpit.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")
        view_creator_js = (APP_ROOT / "js" / "modules" / "view-creator.js").read_text(encoding="utf-8-sig")
        project_generator_core_js = (APP_ROOT / "js" / "modules" / "project-generator-core.js").read_text(encoding="utf-8-sig")
        project_generator_config_js = (APP_ROOT / "js" / "modules" / "project-generator-config.js").read_text(encoding="utf-8-sig")
        project_generator_dom_js = (APP_ROOT / "js" / "modules" / "project-generator-dom.js").read_text(encoding="utf-8-sig")
        project_generator_bindings_js = (APP_ROOT / "js" / "modules" / "project-generator-bindings.js").read_text(encoding="utf-8-sig")
        project_generator_renderers_js = (APP_ROOT / "js" / "modules" / "project-generator-renderers.js").read_text(encoding="utf-8-sig")
        project_generator_status_js = (APP_ROOT / "js" / "modules" / "project-generator-status.js").read_text(encoding="utf-8-sig")
        project_generator_cleaner_js = (APP_ROOT / "js" / "modules" / "project-generator-cleaner.js").read_text(encoding="utf-8-sig")
        project_generator_js = (APP_ROOT / "js" / "modules" / "project-generator.js").read_text(encoding="utf-8-sig")
        index_js = (APP_ROOT / "js" / "modules" / "index.js").read_text(encoding="utf-8-sig")
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")

        self.assertIn("global.SQX = global.SQX || {}", core_js)
        self.assertIn("registerModule", core_js)
        self.assertIn("SQX.config", config_js)
        self.assertIn("SQX.storage", storage_js)
        self.assertIn("SQX.stateBackup", state_backup_js)
        self.assertIn("window.SQX.stateBackup.init()", main_js)
        self.assertIn('id="state-backup-now"', self.html)
        self.assertIn('id="state-backup-restore"', self.html)
        self.assertIn('id="state-restore-list"', self.html)
        self.assertIn('id="wf-plan-v2-summary"', self.html)
        self.assertIn('id="priority-tf-selector"', self.html)
        self.assertNotIn("Matriz Completa", self.html)
        self.assertIn("SQX.license", license_js)
        self.assertIn("SQX.ui", ui_js)
        self.assertIn("SQX.formatters", formatters_js)
        self.assertIn("SQX.analyzer", analyzer_js)
        self.assertIn("SQX.registerModule('analyzer'", analyzer_js)
        self.assertIn("window.SQX.analyzer.init()", main_js)
        self.assertIn('id="tab-analyzer"', self.html)
        self.assertIn('id="analyzer-file-input"', self.html)
        self.assertIn('href="css/analyzer.css"', self.html)
        self.assertIn("SQX.championChallengerCore", champion_core_js)
        self.assertIn("computeTemporalHealth", champion_core_js)
        self.assertIn("detectDirection", champion_core_js)
        self.assertIn("temporal_health_metric_fallback", champion_core_js)
        self.assertIn("SQX.championChallenger", champion_ui_js)
        self.assertIn("buildReviewExport", champion_ui_js)
        self.assertIn("buildStrategyBuilderHandoff", champion_ui_js)
        self.assertIn("compactTemporalHealth", champion_ui_js)
        self.assertIn("compactEgtV2", champion_ui_js)
        self.assertIn("compactDirectionalCoherence", champion_ui_js)
        self.assertIn("compactConsolidatedScore", champion_ui_js)
        self.assertIn("temporal_health_ok_count", champion_ui_js)
        self.assertIn("egt_v2_ok_count", champion_ui_js)
        self.assertIn("directional_coherence_ok_count", champion_ui_js)
        self.assertIn("score_pro_ok_count", champion_ui_js)
        self.assertNotIn("localStorage.setItem", champion_ui_js)
        self.assertIn("SQX.strategyBuilderCore", strategy_builder_core_js)
        self.assertIn("buildPackage", strategy_builder_core_js)
        self.assertIn("sqx-edge.strategy-builder-package", strategy_builder_core_js)
        self.assertIn("sampleCvcHandoff", strategy_builder_core_js)
        self.assertIn("cvc_evidence_summary", strategy_builder_core_js)
        self.assertIn("directional_coherence", strategy_builder_core_js)
        self.assertIn("consolidated_score", strategy_builder_core_js)
        self.assertIn("evidence_review", strategy_builder_core_js)
        self.assertIn("validateImportPayload", strategy_builder_core_js)
        self.assertIn("importPayload", strategy_builder_core_js)
        self.assertIn("projectGeneratorPrefillFromPackage", strategy_builder_core_js)
        self.assertIn("projectGeneratorPresetDraftFromPackage", strategy_builder_core_js)
        self.assertIn("reviewChecklistSummary", strategy_builder_core_js)
        self.assertIn("sqxViewsHandoffFromPackage", strategy_builder_core_js)
        self.assertIn("buyerWorkflowSummary", strategy_builder_core_js)
        self.assertIn("buyerHandoffPackReview", strategy_builder_core_js)
        self.assertIn("guidedBuyerSessionChecklist", strategy_builder_core_js)
        self.assertIn("buyerSessionHandoffSummary", strategy_builder_core_js)
        self.assertIn("buyerSessionOperatorNotes", strategy_builder_core_js)
        self.assertIn("buyerSessionSupportCaseBundle", strategy_builder_core_js)
        self.assertIn("buyerSessionSupportResolutionChecklist", strategy_builder_core_js)
        self.assertIn("handoffEvidenceIndex", strategy_builder_core_js)
        self.assertIn("sqx-edge.strategy-builder-evidence-handoff-index", strategy_builder_core_js)
        self.assertIn("handoffAuditEntry", strategy_builder_core_js)
        self.assertIn("strategyCleanerDraftFromPackage", strategy_builder_core_js)
        self.assertIn("unifiedBuyerHandoffPackFromPackage", strategy_builder_core_js)
        self.assertIn("SQX.strategyBuilder", strategy_builder_js)
        self.assertIn("loadCvcSample", strategy_builder_js)
        self.assertIn("exportPackage", strategy_builder_js)
        self.assertIn("importText", strategy_builder_js)
        self.assertIn("sendToProjectGenerator", strategy_builder_js)
        self.assertIn("prepareProjectGeneratorPreset", strategy_builder_js)
        self.assertIn("sendToViews", strategy_builder_js)
        self.assertIn("prepareStrategyCleaner", strategy_builder_js)
        self.assertIn("prepareBuyerHandoffPack", strategy_builder_js)
        self.assertIn("prepareBuyerSessionChecklist", strategy_builder_js)
        self.assertIn("exportBuyerSessionSummary", strategy_builder_js)
        self.assertIn("prepareBuyerSessionNotes", strategy_builder_js)
        self.assertIn("exportBuyerSupportCaseBundle", strategy_builder_js)
        self.assertIn("prepareBuyerResolutionChecklist", strategy_builder_js)
        self.assertIn("prepareEvidenceHandoffIndex", strategy_builder_js)
        self.assertIn("Buyer Pack Import Review", strategy_builder_js)
        self.assertIn("Buyer Session Checklist", strategy_builder_js)
        self.assertIn("Buyer Session Summary", strategy_builder_js)
        self.assertIn("Buyer Session Notes", strategy_builder_js)
        self.assertIn("Buyer Support Case", strategy_builder_js)
        self.assertIn("Buyer Resolution Checklist", strategy_builder_js)
        self.assertIn("Evidence Index", strategy_builder_js)
        self.assertIn("renderAuditTrail", strategy_builder_js)
        self.assertIn("openHandoff", strategy_builder_js)
        self.assertNotIn("localStorage.setItem", strategy_builder_js)
        self.assertIn("writeCustomProjectInputs", strategy_builder_js)
        self.assertIn("FileReader", strategy_builder_js)
        self.assertNotIn("fetch(", strategy_builder_js)
        self.assertIn("window.SQX.championChallenger.init()", main_js)
        self.assertIn("window.SQX.strategyBuilder.init()", main_js)
        self.assertIn('id="tab-cvc"', self.html)
        self.assertIn('id="tab-strategybuilder"', self.html)
        self.assertIn('id="sb-build-btn"', self.html)
        self.assertIn('id="sb-send-views-btn"', self.html)
        self.assertIn('id="sb-prepare-cleaner-btn"', self.html)
        self.assertIn('id="sb-prepare-buyer-pack-btn"', self.html)
        self.assertIn('id="sb-buyer-session-btn"', self.html)
        self.assertIn('id="sb-buyer-summary-btn"', self.html)
        self.assertIn('id="sb-buyer-notes-btn"', self.html)
        self.assertIn('id="sb-buyer-support-case-btn"', self.html)
        self.assertIn('id="sb-buyer-resolution-btn"', self.html)
        self.assertIn('id="sb-evidence-index-btn"', self.html)
        self.assertIn('id="sb-workflow-steps"', self.html)
        self.assertIn('id="sb-audit-list"', self.html)
        self.assertIn('id="sb-import-btn"', self.html)
        self.assertIn('id="sb-import-file"', self.html)
        self.assertIn('id="sb-send-pg-btn"', self.html)
        self.assertIn('id="sb-prepare-preset-btn"', self.html)
        self.assertIn('id="sb-review-list"', self.html)
        self.assertIn('id="sb-package-preview"', self.html)
        self.assertIn('id="cvc-run-btn"', self.html)
        self.assertIn('id="cvc-export-btn"', self.html)
        self.assertIn('id="cvc-handoff-btn"', self.html)
        self.assertIn('id="cvc-handoff-preview"', self.html)
        self.assertIn('id="cvc-filter-health-ok"', self.html)
        self.assertIn('id="cvc-filter-egt-v2-ok"', self.html)
        self.assertIn('id="cvc-filter-coherence-ok"', self.html)
        self.assertIn('id="cvc-ranking"', self.html)
        self.assertIn('data-home-tab="cvc"', self.html)
        self.assertIn("SQX.domain", domain_js)
        self.assertIn("SQX.datasets", datasets_js)
        self.assertIn("SQX.championChallengerRegime", champion_regime_js)
        self.assertIn("assessEgtV2", champion_regime_js)
        self.assertIn("assessDirectionalCoherence", champion_regime_js)
        self.assertIn("buildRegimeBlocksForSymbol", champion_regime_js)
        self.assertIn("EGT_V2_THRESHOLDS", champion_regime_js)
        self.assertIn("SQX_HISTORICAL_DATA", champion_regime_js)
        self.assertIn("SQX_SCORES_DATA", champion_regime_js)
        self.assertIn('id="cvc-regime-ready-count"', self.html)
        self.assertIn("SQX.renderers", renderers_js)
        self.assertIn("SQX.charts", charts_js)
        self.assertIn("SQX.strategies", strategies_js)
        self.assertIn("SQX.home", home_js)
        self.assertIn("SQX.mtfEvidence", mtf_evidence_js)
        self.assertIn("SQX.support", support_js)
        self.assertIn("SQX.fulfillment", fulfillment_js)
        self.assertIn("SQX.customerCockpit", customer_cockpit_js)
        self.assertIn("SQX.workflow", workflow_js)
        self.assertIn("SQX.viewCreator", view_creator_js)
        self.assertIn("buildViewXml", view_creator_js)
        self.assertIn("BUYER_READY_TEMPLATE_DEFINITIONS", view_creator_js)
        self.assertIn("BUYER_PROFILE_PACK_DEFINITIONS", view_creator_js)
        self.assertIn("VALIDATION_WORKFLOW_PACK_DEFINITIONS", view_creator_js)
        self.assertIn("buildBuyerReadyTemplatePack", view_creator_js)
        self.assertIn("buildBuyerProfilePack", view_creator_js)
        self.assertIn("buildAllBuyerProfilePacks", view_creator_js)
        self.assertIn("buildValidationWorkflowPack", view_creator_js)
        self.assertIn("buildAllValidationWorkflowPacks", view_creator_js)
        self.assertIn("renderValidationWorkflowPacks", view_creator_js)
        self.assertIn("presetImportPreviewFromText", view_creator_js)
        self.assertIn("presetImportPreviewHtml", view_creator_js)
        self.assertIn("presetImportPreviewSummary", view_creator_js)
        self.assertIn('id="vc-template-list"', self.html)
        self.assertIn('id="vc-export-template-pack-btn"', self.html)
        self.assertIn('id="vc-profile-list"', self.html)
        self.assertIn('id="vc-profile-count"', self.html)
        self.assertIn('id="vc-workflow-pack-list"', self.html)
        self.assertIn('id="vc-workflow-pack-count"', self.html)
        self.assertIn('id="vc-import-preview"', self.html)
        self.assertIn("SQX.projectGenerator", project_generator_core_js)
        self.assertIn("SQX.projectGenerator", project_generator_config_js)
        self.assertIn("SQX.projectGenerator", project_generator_dom_js)
        self.assertIn("SQX.projectGenerator", project_generator_bindings_js)
        self.assertIn("SQX.projectGenerator", project_generator_renderers_js)
        self.assertIn("SQX.projectGenerator", project_generator_status_js)
        self.assertIn("SQX.projectGenerator", project_generator_cleaner_js)
        self.assertIn("SQX.projectGenerator", project_generator_js)
        self.assertIn("SQX.boot", index_js)
        self.assertIn("dashboard-legacy", dashboard_js)

    def test_dashboard_history_chart_delegates_to_charts_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        charts_js = (APP_ROOT / "js" / "modules" / "charts.js").read_text(encoding="utf-8-sig")

        self.assertIn("SQX_CHARTS", dashboard_js)
        self.assertIn("SQX_CHARTS.renderHistoryChart", dashboard_js)
        self.assertIn("renderHistoryChart", charts_js)
        self.assertIn("history-chart", charts_js)

    def test_dashboard_html_helpers_delegate_to_renderers_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        renderers_js = (APP_ROOT / "js" / "modules" / "renderers.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "sqxBadge",
            "sqxPreviewHTML",
            "ratingPairBadge",
            "compositeBar",
            "historySection",
            "sqxLegend",
            "sortableHeader",
            "sparkHTML",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, renderers_js)
                self.assertIn(f"SQX_RENDERERS.{export}", dashboard_js)

    def test_dashboard_strategy_logic_delegates_to_strategies_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        strategies_js = (APP_ROOT / "js" / "modules" / "strategies.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "strategyKey",
            "getAllStrategies",
            "filterStrategies",
            "summarize",
            "summaryHtml",
            "filterOptionsHtml",
            "strategyCard",
            "sortForDisplay",
            "exportCsvRows",
            "dedupeImportedStrategies",
            "consolidateJson",
            "consolidatedPopupHtml",
            "manualStrategyFromValues",
            "autoDetectTemplate",
            "parseCSV",
            "detectSeparator",
            "filterCsvRows",
            "csvPreviewTable",
            "csvConfirmHtml",
            "rowToStrategy",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, strategies_js)
                self.assertIn(f"SQX_STRATEGIES.{export}", dashboard_js)

    def test_dashboard_home_logic_delegates_to_home_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        home_js = (APP_ROOT / "js" / "modules" / "home.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "addTrace",
            "applyHomeModel",
            "computeHomeModel",
            "createTraceItem",
            "escapeHtml",
            "traceHtml",
            "trimAction",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, home_js)
                self.assertIn(f"SQX_HOME.{export}", dashboard_js)

    def test_support_diagnostics_module_and_ui_are_wired(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        support_js = (APP_ROOT / "js" / "modules" / "support.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        support_py = (TOOL_ROOT / "core" / "support_diagnostics.py").read_text(encoding="utf-8-sig")
        product_manifest = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))

        expected_ids = [
            "support-panel",
            "support-diagnostic-btn",
            "support-diagnostic-status",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        for export in [
            "diagnosticsFilename",
            "downloadJson",
            "fetchDiagnostics",
            "generateDiagnostics",
            "setStatus",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, support_js)

        self.assertIn("js/modules/support.js", self.html)
        self.assertIn("window.SQX.support.init()", main_js)
        self.assertIn("/api/support/diagnostics", server_py)
        self.assertIn("build_support_diagnostics", server_py)
        self.assertIn("safe_to_send", support_py)
        self.assertIn("license_payload", support_py)
        self.assertIn("strategy_files", support_py)
        self.assertEqual(product_manifest["support"]["diagnosticsEndpoint"], "/api/support/diagnostics")
        self.assertTrue(product_manifest["support"]["safeToSend"])

    def test_mtf_evidence_module_and_ui_are_wired(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        mtf_evidence_js = (APP_ROOT / "js" / "modules" / "mtf-evidence.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        mtf_evidence_py = (TOOL_ROOT / "core" / "mtf_evidence.py").read_text(encoding="utf-8-sig")

        expected_ids = [
            "mtf-evidence-panel",
            "mtf-evidence-refresh-btn",
            "mtf-evidence-tf-count",
            "mtf-evidence-asset-count",
            "mtf-evidence-covered-count",
            "mtf-evidence-badge",
            "mtf-evidence-status",
            "mtf-evidence-list",
            "mtf-evidence-empty",
            "priority-source-current",
            "priority-source-note",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        for export in [
            "apiBase",
            "endpoint",
            "fetchEvidence",
            "init",
            "refreshEvidence",
            "renderEvidence",
            "setStatus",
            "statusClass",
            "updatePriorityStrip",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, mtf_evidence_js)

        self.assertIn("js/modules/mtf-evidence.js", self.html)
        self.assertIn("window.SQX.mtfEvidence.init()", main_js)
        self.assertIn("/api/mtf/evidence", server_py)
        self.assertIn("build_mtf_evidence", server_py)
        self.assertIn("read_only_after_a56_go", mtf_evidence_py)
        self.assertIn("a56_real_mtf_pipeline_run.json", mtf_evidence_py)
        self.assertIn("available && payload.status === 'GO'", mtf_evidence_js)

    def test_fulfillment_operator_module_and_ui_are_wired(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        fulfillment_js = (APP_ROOT / "js" / "modules" / "fulfillment.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        product_manifest = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))

        expected_ids = [
            "fulfillment-panel",
            "fulfillment-refresh-btn",
            "fulfillment-queue-count",
            "fulfillment-needs-review-count",
            "fulfillment-failed-count",
            "fulfillment-processed-count",
            "fulfillment-private-key",
            "fulfillment-zip-path",
            "fulfillment-support-email",
            "fulfillment-queue-status",
            "fulfillment-request-list",
            "fulfillment-empty",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        for export in [
            "fetchQueue",
            "handleAction",
            "loadSettings",
            "processRequest",
            "renderQueue",
            "saveSettings",
            "setStatus",
            "storageKey",
            "updateRequestStatus",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, fulfillment_js)

        self.assertIn("js/modules/fulfillment.js", self.html)
        self.assertIn("window.SQX.fulfillment.init()", main_js)
        self.assertIn("/api/fulfillment/request-status", server_py)
        self.assertIn("/api/fulfillment/relay-ingest", server_py)
        self.assertIn("fulfillment_queue_overview", server_py)
        self.assertEqual(product_manifest["upgrade"]["checkout"]["status"], "next_controlled_commercial_movement_from_m98_decision_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["status"], "next_controlled_commercial_movement_from_m98_decision_ready")
        self.assertIn("checkout_live_readiness.py", product_manifest["upgrade"]["checkout"]["liveReadinessTool"])
        self.assertIn("commercial_release_candidate.py", product_manifest["upgrade"]["checkout"]["commercialReleaseCandidateTool"])
        self.assertIn("pilot_purchase_kit.py", product_manifest["upgrade"]["checkout"]["pilotPurchaseKitTool"])
        self.assertIn("pilot_purchase_kit", product_manifest["upgrade"]["checkout"]["pilotPurchaseKitEvidenceDir"])
        self.assertIn("limited_public_launch.py", product_manifest["upgrade"]["checkout"]["limitedPublicLaunchTool"])
        self.assertIn("limited_public_launch", product_manifest["upgrade"]["checkout"]["limitedPublicLaunchEvidenceDir"])
        self.assertIn("post_launch_control.py", product_manifest["upgrade"]["checkout"]["postLaunchControlTool"])
        self.assertIn("post_launch_control", product_manifest["upgrade"]["checkout"]["postLaunchControlEvidenceDir"])
        self.assertIn("commercial_feedback_loop.py", product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopTool"])
        self.assertIn("commercial_feedback_loop", product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopEvidenceDir"])
        self.assertIn("public_offer_pack.py", product_manifest["upgrade"]["checkout"]["publicOfferPackTool"])
        self.assertIn("public_offer_pack", product_manifest["upgrade"]["checkout"]["publicOfferPackEvidenceDir"])
        self.assertIn("launch_assets_kit.py", product_manifest["upgrade"]["checkout"]["launchAssetsKitTool"])
        self.assertIn("launch_assets_kit", product_manifest["upgrade"]["checkout"]["launchAssetsKitEvidenceDir"])
        self.assertIn("public_release_gate.py", product_manifest["upgrade"]["checkout"]["publicReleaseGateTool"])
        self.assertIn("public_release_gate", product_manifest["upgrade"]["checkout"]["publicReleaseGateEvidenceDir"])
        self.assertIn("release_publication_record.py", product_manifest["upgrade"]["checkout"]["releasePublicationRecordTool"])
        self.assertIn("release_publication_record", product_manifest["upgrade"]["checkout"]["releasePublicationRecordEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["verifiedReleaseCandidate"]["phase"], "R47")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["verifiedReleaseCandidate"]["status"], "controlled_commercial_candidate_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["verifiedReleaseCandidate"]["tagDraft"], "v0.2.0-r47")
        self.assertIn("SQX_Edge_Tool_Portable_20260509_102131.zip", product_manifest["upgrade"]["checkout"]["verifiedReleaseCandidate"]["portableZip"])
        self.assertIn("18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D", product_manifest["upgrade"]["checkout"]["verifiedReleaseCandidate"]["sha256"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["verifiedReleaseCandidate"]["publicationPlan"], "docs/R47_CONTROLLED_COMMERCIAL_RELEASE.md")
        self.assertIn("post_release_monitor.py", product_manifest["upgrade"]["checkout"]["postReleaseMonitorTool"])
        self.assertIn("post_release_monitor", product_manifest["upgrade"]["checkout"]["postReleaseMonitorEvidenceDir"])
        self.assertIn("hotfix_rollback_release.py", product_manifest["upgrade"]["checkout"]["hotfixRollbackReleaseTool"])
        self.assertIn("hotfix_rollback_release", product_manifest["upgrade"]["checkout"]["hotfixRollbackReleaseEvidenceDir"])
        self.assertIn("customer_success_renewal.py", product_manifest["upgrade"]["checkout"]["customerSuccessRenewalTool"])
        self.assertIn("customer_success_renewal", product_manifest["upgrade"]["checkout"]["customerSuccessRenewalEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayIngestEndpoint"], "/api/fulfillment/relay-ingest")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayConfigCheckEndpoint"], "/relay/config-check")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayObservabilityEndpoint"], "/relay/observability")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relaySnapshotEndpoint"], "/relay/observability/snapshot")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayDispatchEndpoint"], "/relay/dispatch")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayOperatorTokenEnv"], "SQX_RELAY_OPERATOR_TOKEN")
        self.assertIn("dispatch_worker.py", product_manifest["upgrade"]["checkout"]["automation"]["relayWorkerScript"])
        self.assertIn("simulate_purchase_flow.py", product_manifest["upgrade"]["checkout"]["automation"]["relaySimulationTool"])
        self.assertIn("deployment_check.py", product_manifest["upgrade"]["checkout"]["automation"]["relayDeploymentCheckTool"])
        self.assertIn("staging_smoke.py", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingSmokeTool"])
        self.assertIn("staging_evidence.py", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingEvidenceTool"])
        self.assertIn("render_api_preflight.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderApiPreflightTool"])
        self.assertIn("render_credentials_handshake.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderCredentialsHandshakeTool"])
        self.assertIn("render_staging_gate.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderStagingGateTool"])
        self.assertIn("render_staging_launch_pack.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderStagingLaunchPackTool"])
        self.assertIn("render_staging_secrets_kit.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderStagingSecretsKitTool"])
        self.assertIn("local_ingest_tunnel_check.py", product_manifest["upgrade"]["checkout"]["automation"]["relayLocalIngestTunnelCheckTool"])
        self.assertIn("local_ingest_tunnel_launcher.py", product_manifest["upgrade"]["checkout"]["automation"]["relayLocalIngestTunnelLauncherTool"])
        self.assertIn("local_ingest_staging_session.py", product_manifest["upgrade"]["checkout"]["automation"]["relayLocalIngestStagingSessionTool"])
        self.assertIn("local_ingest_render_handoff.py", product_manifest["upgrade"]["checkout"]["automation"]["relayLocalIngestRenderHandoffTool"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayRenderCredentialPolicy"], "api_key_only_no_account_password")
        self.assertIn(".env.staging.example", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingEnvExample"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayRecommendedStagingProvider"], "render")
        self.assertIn("Dockerfile", product_manifest["upgrade"]["checkout"]["automation"]["relayDockerfile"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["requestStatusEndpoint"], "/api/fulfillment/request-status")
        self.assertTrue(product_manifest["upgrade"]["checkout"]["automation"]["operatorPanelEnabled"])

    def test_customer_cockpit_module_and_ui_are_wired(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        customer_cockpit_js = (APP_ROOT / "js" / "modules" / "customer-cockpit.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        customer_cockpit_py = (TOOL_ROOT / "core" / "customer_cockpit.py").read_text(encoding="utf-8-sig")
        product_manifest = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))

        expected_ids = [
            "customer-cockpit-panel",
            "customer-cockpit-refresh-btn",
            "customer-cockpit-customer-count",
            "customer-cockpit-renewal-count",
            "customer-cockpit-support-count",
            "customer-cockpit-opportunity-count",
            "customer-cockpit-status",
            "customer-cockpit-list",
            "customer-cockpit-empty",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        for export in [
            "apiBase",
            "endpoint",
            "fetchCockpit",
            "init",
            "renderCockpit",
            "riskClass",
            "riskLabel",
            "setStatus",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, customer_cockpit_js)

        self.assertIn("SQX.registerModule('customer-cockpit'", customer_cockpit_js)
        self.assertIn("js/modules/customer-cockpit.js", self.html)
        self.assertIn("window.SQX.customerCockpit.init()", main_js)
        self.assertIn("/api/customer-cockpit", server_py)
        self.assertIn("customer_cockpit_overview", server_py)
        self.assertIn("redacted_operator_summary", customer_cockpit_py)
        self.assertIn("license payloads", customer_cockpit_py)
        self.assertEqual(product_manifest["upgrade"]["checkout"]["status"], "next_controlled_commercial_movement_from_m98_decision_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["status"], "next_controlled_commercial_movement_from_m98_decision_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerCockpitEndpoint"], "/api/customer-cockpit")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerCockpitConfig"], "backend/sqx-edge-tool/config/customer_cockpit.json")
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["customerCockpitPolicy"],
            "render_redacted_operator_summary_without_license_payloads_or_raw_events",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["proBuyerPackConfig"], "backend/sqx-edge-tool/config/pro_buyer_pack.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["proBuyerPackResourceDir"], "resources/pro-buyer-pack")
        self.assertIn("pro_buyer_pack.py", product_manifest["upgrade"]["checkout"]["proBuyerPackValidationTool"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["proBuyerPackPolicy"],
            "ship_safe_buyer_material_without_license_payloads_private_keys_or_financial_promises",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateConfig"],
            "backend/sqx-edge-tool/config/buyer_onboarding_support_gate.json",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["buyerOnboardingResourceDir"], "resources/pro-buyer-pack/onboarding")
        self.assertIn("buyer_onboarding_support_gate.py", product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateTool"])
        self.assertIn("buyer_onboarding_support_gate", product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGatePolicy"],
            "confirm_purchase_zip_license_start_here_faq_support_and_safe_claims_before_handoff",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1Config"], "backend/sqx-edge-tool/config/template_pack_1.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1ResourceDir"], "resources/pro-template-pack-1")
        self.assertIn("template_pack_1_delivery.py", product_manifest["upgrade"]["checkout"]["templatePack1DeliveryTool"])
        self.assertIn("template_pack_1_delivery", product_manifest["upgrade"]["checkout"]["templatePack1EvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1Policy"],
            "deliver_as_separate_addon_zip_after_buyer_onboarding_gate_and_safe_claims_review",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1OfferConfig"], "backend/sqx-edge-tool/config/template_pack_1_offer.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1OfferResourceDir"], "resources/pro-template-pack-1/offer")
        self.assertIn("template_pack_1_offer.py", product_manifest["upgrade"]["checkout"]["templatePack1OfferTool"])
        self.assertIn("template_pack_1_offer", product_manifest["upgrade"]["checkout"]["templatePack1OfferEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1PublicationConfig"], "backend/sqx-edge-tool/config/template_pack_1_publication.json")
        self.assertIn("template_pack_1_publication.py", product_manifest["upgrade"]["checkout"]["templatePack1PublicationTool"])
        self.assertIn("template_pack_1_publication", product_manifest["upgrade"]["checkout"]["templatePack1PublicationEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1OfferPolicy"],
            "prepare_public_addon_offer_copy_faq_checkout_draft_delivery_macro_and_support_macro_before_live_checkout",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1PublicationConfig"],
            "backend/sqx-edge-tool/config/template_pack_1_publication.json",
        )
        self.assertIn("template_pack_1_publication.py", product_manifest["upgrade"]["checkout"]["templatePack1PublicationTool"])
        self.assertIn("template_pack_1_publication", product_manifest["upgrade"]["checkout"]["templatePack1PublicationEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1PublicationPolicy"],
            "require_real_checkout_url_variant_support_email_and_rollback_before_controlled_publication",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1PurchaseDrillConfig"], "backend/sqx-edge-tool/config/template_pack_1_purchase_drill.json")
        self.assertIn("template_pack_1_purchase_drill.py", product_manifest["upgrade"]["checkout"]["templatePack1PurchaseDrillTool"])
        self.assertIn("template_pack_1_purchase_drill", product_manifest["upgrade"]["checkout"]["templatePack1PurchaseDrillEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1PurchaseDrillPolicy"],
            "record_controlled_addon_order_payment_delivery_support_and_refund_pause_before_scaling",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1HandoffConfig"], "backend/sqx-edge-tool/config/template_pack_1_handoff.json")
        self.assertIn("template_pack_1_handoff.py", product_manifest["upgrade"]["checkout"]["templatePack1HandoffTool"])
        self.assertIn("template_pack_1_handoff", product_manifest["upgrade"]["checkout"]["templatePack1HandoffEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1HandoffPolicy"],
            "confirm_delivery_support_first_value_and_scale_or_pause_decision_after_controlled_purchase",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1SalesRegisterConfig"], "backend/sqx-edge-tool/config/template_pack_1_sales_register.json")
        self.assertIn("template_pack_1_sales_register.py", product_manifest["upgrade"]["checkout"]["templatePack1SalesRegisterTool"])
        self.assertIn("template_pack_1_sales_register", product_manifest["upgrade"]["checkout"]["templatePack1SalesRegisterEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1SalesRegisterPolicy"],
            "track_redacted_addon_sales_delivery_support_refunds_and_scale_decision_before_more_traffic",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1FeedbackCohortConfig"], "backend/sqx-edge-tool/config/template_pack_1_feedback_cohort.json")
        self.assertIn("template_pack_1_feedback_cohort.py", product_manifest["upgrade"]["checkout"]["templatePack1FeedbackCohortTool"])
        self.assertIn("template_pack_1_feedback_cohort", product_manifest["upgrade"]["checkout"]["templatePack1FeedbackCohortEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1FeedbackCohortPolicy"],
            "review_redacted_buyer_feedback_support_refunds_and_positive_signals_before_scaling_or_template_pack_2",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1ActionPlanConfig"], "backend/sqx-edge-tool/config/template_pack_1_action_plan.json")
        self.assertIn("template_pack_1_action_plan.py", product_manifest["upgrade"]["checkout"]["templatePack1ActionPlanTool"])
        self.assertIn("template_pack_1_action_plan", product_manifest["upgrade"]["checkout"]["templatePack1ActionPlanEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1ActionPlanPolicy"],
            "convert_feedback_cohort_into_owner_priority_support_claims_distribution_and_next_phase_actions",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2SpecsConfig"], "backend/sqx-edge-tool/config/template_pack_2_specs.json")
        self.assertIn("template_pack_2_specs.py", product_manifest["upgrade"]["checkout"]["templatePack2SpecsTool"])
        self.assertIn("template_pack_2_specs", product_manifest["upgrade"]["checkout"]["templatePack2SpecsEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2SpecsPolicy"],
            "define_pack_2_scope_assets_presets_support_delivery_and_next_phase_before_building_resources",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2AssetsConfig"], "backend/sqx-edge-tool/config/template_pack_2_assets.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2ResourceDir"], "resources/pro-template-pack-2")
        self.assertIn("template_pack_2_assets.py", product_manifest["upgrade"]["checkout"]["templatePack2AssetsTool"])
        self.assertIn("template_pack_2_assets", product_manifest["upgrade"]["checkout"]["templatePack2AssetsEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2AssetsPolicy"],
            "deliver_initial_pack_2_assets_as_separate_addon_zip_after_specs_gate_and_safe_claims_review",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2OfferPackConfig"], "backend/sqx-edge-tool/config/template_pack_2_offer_pack.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2OfferPackResourceDir"], "resources/pro-template-pack-2/offer")
        self.assertIn("template_pack_2_offer_pack.py", product_manifest["upgrade"]["checkout"]["templatePack2OfferPackTool"])
        self.assertIn("template_pack_2_offer_pack", product_manifest["upgrade"]["checkout"]["templatePack2OfferPackEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2OfferPackPolicy"],
            "prepare_pack_2_offer_copy_faq_checkout_draft_delivery_macro_and_support_macro_before_live_checkout",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2PublicationConfig"], "backend/sqx-edge-tool/config/template_pack_2_publication.json")
        self.assertIn("template_pack_2_publication.py", product_manifest["upgrade"]["checkout"]["templatePack2PublicationTool"])
        self.assertIn("template_pack_2_publication", product_manifest["upgrade"]["checkout"]["templatePack2PublicationEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2PublicationPolicy"],
            "require_real_checkout_url_variant_support_rollback_and_purchase_drill_before_controlled_publication",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2PurchaseDrillConfig"], "backend/sqx-edge-tool/config/template_pack_2_purchase_drill.json")
        self.assertIn("template_pack_2_purchase_drill.py", product_manifest["upgrade"]["checkout"]["templatePack2PurchaseDrillTool"])
        self.assertIn("template_pack_2_purchase_drill", product_manifest["upgrade"]["checkout"]["templatePack2PurchaseDrillEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2PurchaseDrillPolicy"],
            "record_controlled_pack_2_order_payment_delivery_support_and_refund_pause_before_scaling",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2HandoffConfig"], "backend/sqx-edge-tool/config/template_pack_2_handoff.json")
        self.assertIn("template_pack_2_handoff.py", product_manifest["upgrade"]["checkout"]["templatePack2HandoffTool"])
        self.assertIn("template_pack_2_handoff", product_manifest["upgrade"]["checkout"]["templatePack2HandoffEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2HandoffPolicy"],
            "confirm_delivery_support_first_value_and_scale_or_pause_decision_after_controlled_pack_2_purchase",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2SalesRegisterConfig"], "backend/sqx-edge-tool/config/template_pack_2_sales_register.json")
        self.assertIn("template_pack_2_sales_register.py", product_manifest["upgrade"]["checkout"]["templatePack2SalesRegisterTool"])
        self.assertIn("template_pack_2_sales_register", product_manifest["upgrade"]["checkout"]["templatePack2SalesRegisterEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2SalesRegisterPolicy"],
            "track_redacted_pack_2_sales_delivery_support_refunds_and_scale_decision_before_more_traffic",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2FeedbackCohortConfig"], "backend/sqx-edge-tool/config/template_pack_2_feedback_cohort.json")
        self.assertIn("template_pack_2_feedback_cohort.py", product_manifest["upgrade"]["checkout"]["templatePack2FeedbackCohortTool"])
        self.assertIn("template_pack_2_feedback_cohort", product_manifest["upgrade"]["checkout"]["templatePack2FeedbackCohortEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2FeedbackCohortPolicy"],
            "review_redacted_pack_2_buyer_feedback_support_refunds_and_positive_signals_before_expanding_traffic",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["buyerReadyCheckoutCloseoutConfig"], "backend/sqx-edge-tool/config/buyer_ready_checkout_closeout.json")
        self.assertIn("buyer_ready_checkout_closeout.py", product_manifest["upgrade"]["checkout"]["buyerReadyCheckoutCloseoutTool"])
        self.assertIn("buyer_ready_checkout_closeout", product_manifest["upgrade"]["checkout"]["buyerReadyCheckoutCloseoutEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["buyerReadyCheckoutCloseoutPolicy"],
            "confirm_basic_user_checkout_release_license_support_and_rollback_before_controlled_sales",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["publicBuyerPageCadenceConfig"], "backend/sqx-edge-tool/config/public_buyer_page_cadence.json")
        self.assertIn("public_buyer_page_cadence.py", product_manifest["upgrade"]["checkout"]["publicBuyerPageCadenceTool"])
        self.assertIn("public_buyer_page_cadence", product_manifest["upgrade"]["checkout"]["publicBuyerPageCadenceEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["publicBuyerPageCadencePolicy"],
            "prepare_public_buyer_page_checklist_support_cadence_and_first_sale_operations_before_wider_distribution",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["firstControlledBuyerLogConfig"], "backend/sqx-edge-tool/config/first_controlled_buyer_log.json")
        self.assertIn("first_controlled_buyer_log.py", product_manifest["upgrade"]["checkout"]["firstControlledBuyerLogTool"])
        self.assertIn("first_controlled_buyer_log", product_manifest["upgrade"]["checkout"]["firstControlledBuyerLogEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["firstControlledBuyerLogPolicy"],
            "record_first_controlled_buyer_activation_support_feedback_and_post_sale_decision_without_personal_data",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["postSaleImprovementLoopConfig"], "backend/sqx-edge-tool/config/post_sale_improvement_loop.json")
        self.assertIn("post_sale_improvement_loop.py", product_manifest["upgrade"]["checkout"]["postSaleImprovementLoopTool"])
        self.assertIn("post_sale_improvement_loop", product_manifest["upgrade"]["checkout"]["postSaleImprovementLoopEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["postSaleImprovementLoopPolicy"],
            "convert_first_controlled_buyer_feedback_into_onboarding_support_macro_public_copy_and_safe_claim_micro_updates",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["postSaleMicroUpdatesConfig"], "backend/sqx-edge-tool/config/post_sale_micro_updates.json")
        self.assertIn("post_sale_micro_updates.py", product_manifest["upgrade"]["checkout"]["postSaleMicroUpdatesTool"])
        self.assertIn("post_sale_micro_updates", product_manifest["upgrade"]["checkout"]["postSaleMicroUpdatesEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["postSaleMicroUpdatesPolicy"],
            "verify_applied_buyer_facing_micro_updates_and_next_controlled_buyer_readiness",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledBuyerReadinessConfig"],
            "backend/sqx-edge-tool/config/next_controlled_buyer_readiness.json",
        )
        self.assertIn("next_controlled_buyer_readiness.py", product_manifest["upgrade"]["checkout"]["nextControlledBuyerReadinessTool"])
        self.assertIn("next_controlled_buyer_readiness", product_manifest["upgrade"]["checkout"]["nextControlledBuyerReadinessEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledBuyerReadinessPolicy"],
            "confirm_single_private_buyer_slot_checkout_license_delivery_support_followup_safe_claims_and_pause_rule",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledBuyerOutcomeConfig"],
            "backend/sqx-edge-tool/config/next_controlled_buyer_outcome.json",
        )
        self.assertIn("next_controlled_buyer_outcome.py", product_manifest["upgrade"]["checkout"]["nextControlledBuyerOutcomeTool"])
        self.assertIn("next_controlled_buyer_outcome", product_manifest["upgrade"]["checkout"]["nextControlledBuyerOutcomeEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledBuyerOutcomePolicy"],
            "record_redacted_controlled_buyer_result_activation_first_value_support_refund_claims_and_next_distribution_decision",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledDistributionStepConfig"],
            "backend/sqx-edge-tool/config/controlled_distribution_step.json",
        )
        self.assertIn("controlled_distribution_step.py", product_manifest["upgrade"]["checkout"]["controlledDistributionStepTool"])
        self.assertIn("controlled_distribution_step", product_manifest["upgrade"]["checkout"]["controlledDistributionStepEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledDistributionStepPolicy"],
            "execute_selected_m71_decision_as_tiny_reversible_distribution_step",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledDistributionReviewConfig"],
            "backend/sqx-edge-tool/config/controlled_distribution_review.json",
        )
        self.assertIn("controlled_distribution_review.py", product_manifest["upgrade"]["checkout"]["controlledDistributionReviewTool"])
        self.assertIn("controlled_distribution_review", product_manifest["upgrade"]["checkout"]["controlledDistributionReviewEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledDistributionReviewPolicy"],
            "review_m72_evidence_before_repeating_holding_pausing_or_preparing_next_buyer_facing_asset",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextBuyerFacingAssetConfig"],
            "backend/sqx-edge-tool/config/next_buyer_facing_asset.json",
        )
        self.assertIn("next_buyer_facing_asset.py", product_manifest["upgrade"]["checkout"]["nextBuyerFacingAssetTool"])
        self.assertIn("next_buyer_facing_asset", product_manifest["upgrade"]["checkout"]["nextBuyerFacingAssetEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextBuyerFacingAssetPolicy"],
            "prepare_one_small_buyer_facing_asset_for_private_review_only_after_m73",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["privateAssetReviewConfig"],
            "backend/sqx-edge-tool/config/private_asset_review.json",
        )
        self.assertIn("private_asset_review.py", product_manifest["upgrade"]["checkout"]["privateAssetReviewTool"])
        self.assertIn("private_asset_review", product_manifest["upgrade"]["checkout"]["privateAssetReviewEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["privateAssetReviewPolicy"],
            "approve_asset_for_controlled_publication_only_after_private_review_safe_claims_support_release_notes_and_rollback",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledPublicationGateConfig"],
            "backend/sqx-edge-tool/config/controlled_publication_gate.json",
        )
        self.assertIn("controlled_publication_gate.py", product_manifest["upgrade"]["checkout"]["controlledPublicationGateTool"])
        self.assertIn("controlled_publication_gate", product_manifest["upgrade"]["checkout"]["controlledPublicationGateEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledPublicationGatePolicy"],
            "prepare_controlled_publication_only_after_private_asset_review_support_safe_claims_release_notes_rollback_and_pause_rule_are_ready",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["limitedPublicationDraftConfig"],
            "backend/sqx-edge-tool/config/limited_publication_draft.json",
        )
        self.assertIn("limited_publication_draft.py", product_manifest["upgrade"]["checkout"]["limitedPublicationDraftTool"])
        self.assertIn("limited_publication_draft", product_manifest["upgrade"]["checkout"]["limitedPublicationDraftEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["limitedPublicationDraftPolicy"],
            "prepare_limited_publication_copy_for_operator_review_only_after_m76_support_safe_claims_rollback_pause_rule_and_channel_limits_are_ready",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["operatorPublicationReviewConfig"],
            "backend/sqx-edge-tool/config/operator_publication_review.json",
        )
        self.assertIn("operator_publication_review.py", product_manifest["upgrade"]["checkout"]["operatorPublicationReviewTool"])
        self.assertIn("operator_publication_review", product_manifest["upgrade"]["checkout"]["operatorPublicationReviewEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["operatorPublicationReviewPolicy"],
            "approve_manual_limited_publication_only_after_human_review_safe_copy_support_rollback_pause_rule_channel_limit_and_basic_user_flow_are_ready",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["manualLimitedPublicationRecordConfig"],
            "backend/sqx-edge-tool/config/manual_limited_publication_record.json",
        )
        self.assertIn("manual_limited_publication_record.py", product_manifest["upgrade"]["checkout"]["manualLimitedPublicationRecordTool"])
        self.assertIn("manual_limited_publication_record", product_manifest["upgrade"]["checkout"]["manualLimitedPublicationRecordEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["manualLimitedPublicationRecordPolicy"],
            "record_manual_limited_publication_only_after_m78_approval_support_rollback_pause_rule_monitoring_and_redacted_channel_evidence_are_ready",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["manualPublicationMonitorConfig"],
            "backend/sqx-edge-tool/config/manual_publication_monitor.json",
        )
        self.assertIn("manual_publication_monitor.py", product_manifest["upgrade"]["checkout"]["manualPublicationMonitorTool"])
        self.assertIn("manual_publication_monitor", product_manifest["upgrade"]["checkout"]["manualPublicationMonitorEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["manualPublicationMonitorPolicy"],
            "monitor_manual_limited_publication_before_any_traffic_expansion_and_block_scaling_when_support_claims_refunds_or_incidents_are_unresolved",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionReviewConfig"],
            "backend/sqx-edge-tool/config/controlled_traffic_expansion_review.json",
        )
        self.assertIn("controlled_traffic_expansion_review.py", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionReviewTool"])
        self.assertIn("controlled_traffic_expansion_review", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionReviewEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionReviewPolicy"],
            "approve_only_tiny_controlled_traffic_expansion_after_m80_monitoring_support_claims_refunds_incidents_rollback_and_pause_rule_are_clean",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionStepConfig"],
            "backend/sqx-edge-tool/config/controlled_traffic_expansion_step.json",
        )
        self.assertIn("controlled_traffic_expansion_step.py", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionStepTool"])
        self.assertIn("controlled_traffic_expansion_step", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionStepEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionStepPolicy"],
            "execute_only_one_tiny_reversible_traffic_step_after_m81_go_with_support_rollback_pause_rule_and_safe_claims_confirmed",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionMonitorConfig"],
            "backend/sqx-edge-tool/config/controlled_traffic_expansion_monitor.json",
        )
        self.assertIn("controlled_traffic_expansion_monitor.py", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionMonitorTool"])
        self.assertIn(
            "controlled_traffic_expansion_monitor",
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionMonitorEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionMonitorPolicy"],
            "monitor_m82_tiny_step_before_repeating_pausing_or_widening_again",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionDecisionConfig"],
            "backend/sqx-edge-tool/config/controlled_traffic_expansion_decision.json",
        )
        self.assertIn("controlled_traffic_expansion_decision.py", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionDecisionTool"])
        self.assertIn(
            "controlled_traffic_expansion_decision",
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionDecisionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionDecisionPolicy"],
            "convert_m83_monitor_evidence_into_one_small_operator_decision_without_automatic_traffic_checkout_or_license_actions",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionExecutionConfig"],
            "backend/sqx-edge-tool/config/controlled_traffic_expansion_execution.json",
        )
        self.assertIn("controlled_traffic_expansion_execution.py", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionExecutionTool"])
        self.assertIn(
            "controlled_traffic_expansion_execution",
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionExecutionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionExecutionPolicy"],
            "record_only_the_manual_m84_approved_action_without_automatic_traffic_checkout_email_or_license_execution",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionExecutionMonitorConfig"],
            "backend/sqx-edge-tool/config/controlled_traffic_expansion_execution_monitor.json",
        )
        self.assertIn("controlled_traffic_expansion_execution_monitor.py", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionExecutionMonitorTool"])
        self.assertIn(
            "controlled_traffic_expansion_execution_monitor",
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionExecutionMonitorEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionExecutionMonitorPolicy"],
            "monitor_m85_execution_result_before_any_further_traffic_or_commercial_movement",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementConfig"],
            "backend/sqx-edge-tool/config/controlled_commercial_next_movement.json",
        )
        self.assertIn("controlled_commercial_next_movement.py", product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementTool"])
        self.assertIn(
            "controlled_commercial_next_movement",
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementPolicy"],
            "decide_next_controlled_commercial_movement_from_m86_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementExecutionConfig"],
            "backend/sqx-edge-tool/config/controlled_commercial_next_movement_execution.json",
        )
        self.assertIn("controlled_commercial_next_movement_execution.py", product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementExecutionTool"])
        self.assertIn(
            "controlled_commercial_next_movement_execution",
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementExecutionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementExecutionPolicy"],
            "record_only_the_manual_m87_approved_movement_without_automatic_traffic_checkout_email_or_license_execution",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementExecutionMonitorConfig"],
            "backend/sqx-edge-tool/config/controlled_commercial_next_movement_execution_monitor.json",
        )
        self.assertIn(
            "controlled_commercial_next_movement_execution_monitor.py",
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementExecutionMonitorTool"],
        )
        self.assertIn(
            "controlled_commercial_next_movement_execution_monitor",
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementExecutionMonitorEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledCommercialNextMovementExecutionMonitorPolicy"],
            "monitor_m88_execution_result_before_any_broader_commercial_movement",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementDecisionConfig"],
            "backend/sqx-edge-tool/config/next_controlled_commercial_movement_decision.json",
        )
        self.assertIn(
            "next_controlled_commercial_movement_decision.py",
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementDecisionTool"],
        )
        self.assertIn(
            "next_controlled_commercial_movement_decision",
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementDecisionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementDecisionPolicy"],
            "decide_next_controlled_commercial_movement_from_m89_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementExecutionConfig"],
            "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_execution.json",
        )
        self.assertIn(
            "approved_controlled_commercial_movement_execution.py",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementExecutionTool"],
        )
        self.assertIn(
            "approved_controlled_commercial_movement_execution",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementExecutionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementExecutionPolicy"],
            "record_only_the_manual_m90_approved_movement_without_automatic_traffic_checkout_email_or_license_execution",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementExecutionMonitorConfig"],
            "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_execution_monitor.json",
        )
        self.assertIn(
            "approved_controlled_commercial_movement_execution_monitor.py",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementExecutionMonitorTool"],
        )
        self.assertIn(
            "approved_controlled_commercial_movement_execution_monitor",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementExecutionMonitorEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementExecutionMonitorPolicy"],
            "monitor_m91_execution_result_before_any_additional_commercial_movement",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM92DecisionConfig"],
            "backend/sqx-edge-tool/config/next_controlled_commercial_movement_from_m92_decision.json",
        )
        self.assertIn(
            "next_controlled_commercial_movement_from_m92_decision.py",
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM92DecisionTool"],
        )
        self.assertIn(
            "next_controlled_commercial_movement_from_m92_decision",
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM92DecisionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM92DecisionPolicy"],
            "decide_next_controlled_commercial_movement_from_m92_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM93ExecutionConfig"],
            "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m93_execution.json",
        )
        self.assertIn(
            "approved_controlled_commercial_movement_from_m93_execution.py",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM93ExecutionTool"],
        )
        self.assertIn(
            "approved_controlled_commercial_movement_from_m93_execution",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM93ExecutionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM93ExecutionPolicy"],
            "record_only_the_manual_m93_approved_movement_without_automatic_traffic_checkout_email_or_license_execution",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM93ExecutionMonitorConfig"],
            "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m93_execution_monitor.json",
        )
        self.assertIn(
            "approved_controlled_commercial_movement_from_m93_execution_monitor.py",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM93ExecutionMonitorTool"],
        )
        self.assertIn(
            "approved_controlled_commercial_movement_from_m93_execution_monitor",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM93ExecutionMonitorEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM93ExecutionMonitorPolicy"],
            "monitor_m94_execution_result_before_any_additional_commercial_movement",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM95DecisionConfig"],
            "backend/sqx-edge-tool/config/next_controlled_commercial_movement_from_m95_decision.json",
        )
        self.assertIn(
            "next_controlled_commercial_movement_from_m95_decision.py",
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM95DecisionTool"],
        )
        self.assertIn(
            "next_controlled_commercial_movement_from_m95_decision",
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM95DecisionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM95DecisionPolicy"],
            "decide_next_controlled_commercial_movement_from_m95_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM96DecisionExecutionConfig"],
            "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m96_decision_execution.json",
        )
        self.assertIn(
            "approved_controlled_commercial_movement_from_m96_decision_execution.py",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM96DecisionExecutionTool"],
        )
        self.assertIn(
            "approved_controlled_commercial_movement_from_m96_decision_execution",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM96DecisionExecutionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM96DecisionExecutionPolicy"],
            "record_only_the_manual_m96_approved_movement_without_automatic_traffic_checkout_email_or_license_execution",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM96DecisionExecutionMonitorConfig"],
            "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.json",
        )
        self.assertIn(
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM96DecisionExecutionMonitorTool"],
        )
        self.assertIn(
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor",
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM96DecisionExecutionMonitorEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["approvedControlledCommercialMovementFromM96DecisionExecutionMonitorPolicy"],
            "monitor_m97_execution_result_before_any_additional_commercial_movement",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM98DecisionConfig"],
            "backend/sqx-edge-tool/config/next_controlled_commercial_movement_from_m98_decision.json",
        )
        self.assertIn(
            "next_controlled_commercial_movement_from_m98_decision.py",
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM98DecisionTool"],
        )
        self.assertIn(
            "next_controlled_commercial_movement_from_m98_decision",
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM98DecisionEvidenceDir"],
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledCommercialMovementFromM98DecisionPolicy"],
            "decide_next_controlled_commercial_movement_from_m98_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        )

    def test_dashboard_navigation_delegates_to_ui_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        ui_js = (APP_ROOT / "js" / "modules" / "ui.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "activateTabById",
            "bindButtonGroup",
            "bindChange",
            "bindClick",
            "bindHomeTabButtons",
            "bindInput",
            "bindTabs",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, ui_js)
                self.assertIn(f"SQX_UI_MODULE.{export}", dashboard_js)

    def test_workflow_shell_delegates_to_workflow_module(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "bindChecklist",
            "bindSubtabs",
            "init",
            "resolveChecklistKey",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, workflow_js)

        self.assertIn("window.SQX.workflow.init()", main_js)
        self.assertNotIn("CHECKLIST_STATE", main_js)
        self.assertNotIn("data-checklist-clear", main_js)

    def test_project_generator_onboarding_delegates_to_module(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        project_generator_main_js = (APP_ROOT / "js" / "project-generator-main.js").read_text(encoding="utf-8-sig")
        project_generator_files = [
            "project-generator-core.js",
            "project-generator-config.js",
            "project-generator-dom.js",
            "project-generator-bindings.js",
            "project-generator-renderers.js",
            "project-generator-status.js",
            "project-generator-cleaner.js",
            "project-generator.js",
        ]
        module_js = "\n".join(
            (APP_ROOT / "js" / "modules" / filename).read_text(encoding="utf-8-sig")
            for filename in project_generator_files
        )

        expected_exports = [
            "aliasTableHtml",
            "aliasAutoSuggestResult",
            "aliasAutoSuggestStartMessage",
            "aliasChoiceValue",
            "aliasProposedMessage",
            "aliasSuggestionEmptyMessage",
            "aliasSuggestionPrompt",
            "aliasTopSuggestions",
            "applyOnboardingState",
            "applyStatusBanner",
            "autodetectCandidatesHtml",
            "cleanerTableHtml",
            "cleanerConfirmMessage",
            "cleanerErrorStatus",
            "cleanerHasAction",
            "cleanerMissingDirStatus",
            "cleanerNoActionStatus",
            "cleanerNoSelectionStatus",
            "cleanerOptions",
            "cleanerPreviewHeader",
            "cleanerPreviewLines",
            "cleanerPreviewPattern",
            "cleanerProcessingStatus",
            "cleanerProcessErrorTrace",
            "cleanerResultLevel",
            "cleanerResultLines",
            "cleanerResultSummary",
            "cleanerResultTrace",
            "cleanerScanMessage",
            "cleanerScanningStatus",
            "cleanerSelectedLabel",
            "cleanerSelectedMap",
            "computeOnboardingState",
            "directionClass",
            "directionLabel",
            "escapeHtml",
            "fetchJson",
            "appendLog",
            "bindProjectGeneratorEvents",
            "bindProjectGeneratorPolling",
            "bindStrategyCleanerEvents",
            "readConfigInputs",
            "readCustomProjectInputs",
            "setCustomProjectStatus",
            "setSettingsOpen",
            "writeConfigInputs",
            "bulkGenerateLabel",
            "configSaveBody",
            "configSaveError",
            "configSaveStatus",
            "customPresetIdFromName",
            "customPresetPackageType",
            "customPresetPackageVersion",
            "customProfileFamilyCardsHtml",
            "customProfileFamilyCountLabel",
            "customProjectPresetImportPreview",
            "customProjectPresetImportPreviewFromText",
            "customProjectPresetImportPreviewHtml",
            "customProjectPresetImportPreviewSummary",
            "customProjectPresetCountLabel",
            "customProjectPresetOptionsHtml",
            "customStarterProfileCardsHtml",
            "customStarterProfileCountLabel",
            "customStarterProfileToPreset",
            "deleteCustomProjectPreset",
            "findCustomProjectPreset",
            "findCustomProfileFamily",
            "findCustomStarterProfile",
            "getCustomProfileFamilies",
            "getCustomProjectPresets",
            "getCustomStarterProfiles",
            "buildAllCustomProfileFamilyPack",
            "buildCustomProfileFamilyPack",
            "buildCustomProjectPresetPackage",
            "buildCustomStarterProfilePack",
            "importCustomProjectPresetPackage",
            "importCustomProjectPresetPackageFromText",
            "generateAllConfirmMessage",
            "generateAllResultLines",
            "generateAllResultSummary",
            "generateAllStartMessage",
            "generateAllTrace",
            "generateCustomMissingStatus",
            "generateCustomResult",
            "generateCustomStartMessage",
            "generateErrorResult",
            "generateOneResult",
            "generateOneStartMessage",
            "enrichMiningsWithSymbolInfo",
            "miningRowsHtml",
            "miningsCountLabel",
            "normalizeCustomPreset",
            "normalizeCustomProjectConfig",
            "outputCountLabel",
            "outputListHtml",
            "outputState",
            "openOutputDisconnectedStatus",
            "openOutputErrorStatus",
            "openOutputSuccessStatus",
            "prepareRequestOptions",
            "setCustomProjectPresets",
            "sqxCandidateFields",
            "sqxCandidateSelectedStatus",
            "sqxAppliedHtml",
            "sqxNotFoundHtml",
            "validateSqxMissingPathHtml",
            "validateSqxPathHtml",
            "validateSqxResolvedFields",
            "validateSqxShouldApply",
            "validateSqxTrace",
            "uniqueAssets",
            "upsertCustomProjectPreset",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, module_js)

        self.assertIn("SQX_PG_MODULE.computeOnboardingState", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.applyOnboardingState", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.applyStatusBanner", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.aliasSuggestionPrompt", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.aliasChoiceValue", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.aliasAutoSuggestResult", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.escapeHtml", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.fetchJson", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.generateOneResult", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.generateAllConfirmMessage", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.generateAllResultLines", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.configSaveBody", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.buildCustomStarterProfilePack", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.buildCustomProfileFamilyPack", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.buildAllCustomProfileFamilyPack", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.customStarterProfileCardsHtml", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.customProfileFamilyCardsHtml", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.customStarterProfileToPreset", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.buildCustomProjectPresetPackage", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.customProjectPresetImportPreviewFromText", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.customProjectPresetImportPreviewHtml", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.importCustomProjectPresetPackageFromText", project_generator_main_js)
        self.assertIn('id="pg-custom-starter-list"', self.html)
        self.assertIn('id="pg-custom-export-starter-profiles"', self.html)
        self.assertIn('id="pg-custom-family-list"', self.html)
        self.assertIn('id="pg-custom-export-family-profiles"', self.html)
        self.assertIn('id="pg-custom-export-presets"', self.html)
        self.assertIn('id="pg-custom-import-presets"', self.html)
        self.assertIn('id="pg-custom-import-presets-file"', self.html)
        self.assertIn('id="pg-custom-import-preview"', self.html)
        self.assertIn("SQX_PG_MODULE.configSaveStatus", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.sqxCandidateFields", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.validateSqxShouldApply", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.enrichMiningsWithSymbolInfo", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.outputState", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.openOutputSuccessStatus", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerNoSelectionStatus", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerResultTrace", project_generator_main_js)
        self.assertIn("const SQX_PG_DOM = SQX_PG_MODULE.dom", project_generator_main_js)
        self.assertIn("SQX_PG_DOM.readConfigInputs", project_generator_main_js)
        self.assertIn("SQX_PG_DOM.writeConfigInputs", project_generator_main_js)
        self.assertIn("SQX_PG_DOM.appendLog", project_generator_main_js)
        self.assertIn("const SQX_PG_BINDINGS = SQX_PG_MODULE.bindings", project_generator_main_js)
        self.assertIn("SQX_PG_BINDINGS.bindProjectGeneratorEvents", project_generator_main_js)
        self.assertIn("SQX_PG_BINDINGS.bindStrategyCleanerEvents", project_generator_main_js)
        self.assertIn("SQX_PG_BINDINGS.bindProjectGeneratorPolling", project_generator_main_js)
        self.assertIn("const PG_STATE = {", project_generator_main_js)
        self.assertIn("const CLN_STATE = {", project_generator_main_js)
        self.assertIn("PG_STATE.connected", project_generator_main_js)
        self.assertIn("CLN_STATE.selected", project_generator_main_js)
        self.assertNotIn("function bindProjectGeneratorEvents()", project_generator_main_js)
        self.assertNotIn("function bindStrategyCleanerEvents()", project_generator_main_js)
        self.assertNotIn("function bindProjectGeneratorPolling()", project_generator_main_js)
        self.assertNotIn("sqxPath: pgTrimmedInputValue('pg-sqx-path')", project_generator_main_js)
        self.assertNotIn("pgSetInputValue('pg-sqx-path', c.sqx_path)", project_generator_main_js)
        self.assertIn("function pgApplySqxCandidate(candidate, outputEl)", project_generator_main_js)
        self.assertIn("function pgApplyValidatedSqxPath(path, response)", project_generator_main_js)
        self.assertIn("function pgUpdateMiningSummary(count)", project_generator_main_js)
        self.assertIn("function pgRenderMiningsList(infos)", project_generator_main_js)
        self.assertIn("function pgRenderOutputState(output)", project_generator_main_js)
        self.assertNotIn("bindProjectGeneratorEvents();", project_generator_main_js)
        self.assertNotIn("bindStrategyCleanerEvents();", project_generator_main_js)
        self.assertNotIn("bindProjectGeneratorPolling();", project_generator_main_js)
        self.assertNotIn("SQX_PG_MODULE", main_js)
        self.assertNotIn("const PG_STATE = {", main_js)
        for old_state in [
            "let PG_CONNECTED",
            "let PG_HEALTH_TIMER",
            "let PG_PLAN_COUNT",
            "let PG_LAST_TRACE_STATE",
            "let PG_HEALTH_META",
            "let PG_CONFIG_STATE",
            "let PG_MININGS",
            "let PG_OUTPUT_FILES",
            "let PG_OUTPUT_DIR",
            "let PG_ALIASES",
            "let CLN_FILES",
            "let CLN_SELECTED",
        ]:
            with self.subTest(old_state=old_state):
                self.assertNotIn(old_state, project_generator_main_js)
        self.assertNotIn("const hasSqxInput = ", project_generator_main_js)
        self.assertNotIn("stepsEl.innerHTML = state.steps.map", project_generator_main_js)
        self.assertNotIn("await fetch(url, opts)", project_generator_main_js)
        self.assertNotIn("banner.classList.remove('pg-status-up'", project_generator_main_js)
        self.assertNotIn("function pgDirClass", project_generator_main_js)
        self.assertNotIn("function pgDirLabel", project_generator_main_js)
        self.assertNotIn("fetch(PG_API + '/minings'", project_generator_main_js)
        self.assertNotIn("const opts = top.map", project_generator_main_js)
        self.assertNotIn("const idx = parseInt(choice, 10)", project_generator_main_js)
        self.assertNotIn("Auto-suggest: ' + found", project_generator_main_js)
        self.assertNotIn("const countLabel = PG_PLAN_COUNT", project_generator_main_js)
        self.assertNotIn("String(x.mining).padStart", project_generator_main_js)
        self.assertNotIn("'OK: ' + r.ok_count", project_generator_main_js)
        self.assertNotIn("msg.textContent = '✓ Guardado: '", project_generator_main_js)
        self.assertNotIn("r.updated_keys.join(', ')", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-sqx-db').value = r.resolved.data_db", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-sqx-path').value = c.sqx_path", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-sqx-path').value.trim()", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-minings-count').textContent", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-output-count').textContent", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-minings-table').innerHTML", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-output-list').innerHTML", project_generator_main_js)
        self.assertNotIn("minings.length + ' minings'", project_generator_main_js)
        self.assertNotIn("r.files.length + ' archivos'", project_generator_main_js)
        self.assertNotIn("Promise.all(minings.map", project_generator_main_js)
        self.assertNotIn("info.textContent = 'Pon una carpeta primero.'", project_generator_main_js)
        self.assertNotIn("info.textContent = '🔍 Escaneando...'", project_generator_main_js)
        self.assertNotIn("'Procesando ' + CLN_SELECTED.size", project_generator_main_js)
        self.assertIn("openOutputFolder: pgOpenOutputFolder", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-open-output').addEventListener('click', async function", project_generator_main_js)
        self.assertNotIn("pgLog('📁 Abierta carpeta output'", project_generator_main_js)
        self.assertNotIn("pg-output-empty", project_generator_main_js)
        self.assertIn("autodetectSqx: pgAutodetectSqx", project_generator_main_js)
        self.assertIn("validateSqxPath: pgValidateSqxPath", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-autodetect').addEventListener('click', async function", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-validate').addEventListener('click', async function", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerTableHtml", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerOptions", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerConfirmMessage", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerPreviewLines", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerResultSummary", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerScanMessage", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerSelectedMap", project_generator_main_js)
        self.assertNotIn("CLN_FILES.map(f =>", project_generator_main_js)
        self.assertNotIn("Object.fromEntries([...CLN_SELECTED]", project_generator_main_js)
        self.assertNotIn("Preview rename para ' + r.previews.length", project_generator_main_js)
        self.assertNotIn("cln-row-check\" data-path=\"'+pgEsc", project_generator_main_js)
        self.assertNotIn("const msg = `", project_generator_main_js)
        self.assertNotIn("const fname = x.path.split", project_generator_main_js)

    def test_dashboard_dataset_loading_delegates_to_datasets_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        datasets_js = (APP_ROOT / "js" / "modules" / "datasets.js").read_text(encoding="utf-8-sig")

        self.assertIn("SQX_DATASETS", dashboard_js)
        self.assertIn("SQX_DATASETS.historical", dashboard_js)
        self.assertIn("SQX_DATASETS.scores", dashboard_js)
        self.assertIn("SQX_HISTORICAL_DATA", datasets_js)
        self.assertIn("SQX_SCORES_DATA", datasets_js)
        self.assertIn("readJsonScript", datasets_js)

    def test_dashboard_domain_logic_delegates_to_domain_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        domain_js = (APP_ROOT / "js" / "modules" / "domain.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "calcScore",
            "getSqxConfig",
            "scoreFromScores",
            "applyObjectiveRatings",
            "tfMatch",
            "sortRows",
            "assetMatchesSqxFilter",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, domain_js)
                self.assertIn(f"SQX_DOMAIN.{export}", dashboard_js)

    def test_runtime_config_delegates_through_config_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        storage_js = (APP_ROOT / "js" / "modules" / "storage.js").read_text(encoding="utf-8-sig")
        config_js = (APP_ROOT / "js" / "modules" / "config.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")

        self.assertIn("SQX_CONFIG_API", dashboard_js)
        self.assertIn("SQX_CONFIG_API.value", dashboard_js)
        self.assertIn("SQX_CONFIG_API.statusMeta", dashboard_js)
        self.assertIn("SQX_CONFIG_API.statusSequence", dashboard_js)
        self.assertIn("window.SQX.workflow.init()", main_js)
        self.assertIn("SQX.config", workflow_js)
        self.assertIn("SQX.config.storageKey", storage_js)
        self.assertIn("statusMeta", config_js)
        self.assertIn("statusSequence", config_js)

    def test_legacy_dashboard_helpers_delegate_to_formatter_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        formatters_js = (APP_ROOT / "js" / "modules" / "formatters.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "ratingLabel",
            "heatmapClass",
            "assetDirectionClass",
            "strategyDirectionClass",
            "tierClass",
            "tierLabel",
            "metricClass",
            "formatNumber",
            "formatInteger",
            "escapeHtml",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, formatters_js)
                self.assertIn(f"SQX_FORMATTERS.{export}", dashboard_js)

    def test_persistent_ui_state_delegates_to_storage_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        storage_js = (APP_ROOT / "js" / "modules" / "storage.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")

        self.assertIn("SQX_STORAGE = SQX_MODULES.storage", dashboard_js)
        self.assertIn("window.SQX.workflow.init()", main_js)
        self.assertIn("getJson", storage_js)
        self.assertIn("setJson", storage_js)

        expected_dashboard_calls = [
            "SQX_STORAGE.getJson(HOME_TRACE_KEY",
            "SQX_STORAGE.setJson(HOME_TRACE_KEY",
            "SQX_STORAGE.getJson(PRIORITY_STATE_KEY",
            "SQX_STORAGE.setJson(PRIORITY_STATE_KEY",
            "SQX_STORAGE.getJson(PLAN_USER_KEY",
            "SQX_STORAGE.setJson(PLAN_USER_KEY",
            "SQX_STORAGE.getJson(PIPELINE_STATE_KEY",
            "SQX_STORAGE.setJson(PIPELINE_STATE_KEY",
            "SQX_STORAGE.getJson(STRAT_USER_KEY",
            "SQX_STORAGE.setJson(STRAT_USER_KEY",
            "SQX_STORAGE.getJson(STRAT_DELETED_KEY",
            "SQX_STORAGE.setJson(STRAT_DELETED_KEY",
        ]
        for call in expected_dashboard_calls:
            with self.subTest(call=call):
                self.assertIn(call, dashboard_js)

        self.assertIn("storage.getJson(key", workflow_js)
        self.assertIn("storage.setJson(key", workflow_js)

    def test_license_module_and_product_manifest_are_wired(self):
        app_config_js = (APP_ROOT / "js" / "app-config.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        license_js = (APP_ROOT / "js" / "modules" / "license.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        license_py = (TOOL_ROOT / "core" / "license_manager.py").read_text(encoding="utf-8-sig")
        product_manifest = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))

        expected_dom_ids = [
            "license-panel",
            "license-plan-label",
            "license-state-badge",
            "license-status-detail",
            "license-commercial-copy",
            "license-upgrade-list",
            "license-plan-strip",
            "license-feature-list",
            "license-key-input",
            "license-checkout-link",
            "license-import-btn",
            "license-clear-btn",
            "license-upgrade-note",
            "license-feedback",
        ]
        for element_id in expected_dom_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        self.assertIn("const product = manifest.product", app_config_js)
        self.assertIn("window.SQX.license.init()", main_js)
        for export in [
            "currentStatus",
            "hasFeature",
            "importLicenseText",
            "renderPanel",
            "refreshBackendStatus",
            "storageKey",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, license_js)

        self.assertEqual(product_manifest["build"]["channel"], "internal")
        self.assertIn("project_generator.generate", product_manifest["features"])
        self.assertIn("strategy_cleaner.apply", product_manifest["features"])
        self.assertIn("*", product_manifest["accessLevels"]["internal"]["features"])
        self.assertEqual(product_manifest["upgrade"]["headline"], "SQX Edge Pro")
        self.assertIn("24 EUR/mes", json.dumps(product_manifest["upgrade"], ensure_ascii=False))
        self.assertEqual(product_manifest["upgrade"]["checkout"]["primaryProvider"], "Lemon Squeezy")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["fallbackProvider"], "Gumroad")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["fulfillmentMode"], "manual_signed_license")
        self.assertIn("license_issue.py", product_manifest["upgrade"]["checkout"]["licenseIssuerTool"])
        self.assertIn("prepare_customer_delivery.ps1", product_manifest["upgrade"]["checkout"]["deliveryTool"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["status"], "next_controlled_commercial_movement_from_m98_decision_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["rollbackPolicy"], "disable_checkout_pause_webhook_pause_worker_manual_fulfillment")
        self.assertIn("checkout_live_readiness.py", product_manifest["upgrade"]["checkout"]["liveReadinessTool"])
        self.assertIn("checkout_live_readiness", product_manifest["upgrade"]["checkout"]["liveReadinessEvidenceDir"])
        self.assertIn("commercial_release_candidate.py", product_manifest["upgrade"]["checkout"]["commercialReleaseCandidateTool"])
        self.assertIn("commercial_release_candidate", product_manifest["upgrade"]["checkout"]["commercialReleaseCandidateEvidenceDir"])
        self.assertIn("pilot_purchase_kit.py", product_manifest["upgrade"]["checkout"]["pilotPurchaseKitTool"])
        self.assertIn("pilot_purchase_kit", product_manifest["upgrade"]["checkout"]["pilotPurchaseKitEvidenceDir"])
        self.assertIn("limited_public_launch.py", product_manifest["upgrade"]["checkout"]["limitedPublicLaunchTool"])
        self.assertIn("limited_public_launch", product_manifest["upgrade"]["checkout"]["limitedPublicLaunchEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["limitedPublicLaunchPolicy"], "soft_launch_first_5_sales_then_review")
        self.assertIn("post_launch_control.py", product_manifest["upgrade"]["checkout"]["postLaunchControlTool"])
        self.assertIn("post_launch_control", product_manifest["upgrade"]["checkout"]["postLaunchControlEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["postLaunchControlPolicy"], "review_first_sales_before_scaling")
        self.assertIn("commercial_feedback_loop.py", product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopTool"])
        self.assertIn("commercial_feedback_loop", product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopPolicy"], "classify_feedback_before_offer_changes")
        self.assertIn("public_offer_pack.py", product_manifest["upgrade"]["checkout"]["publicOfferPackTool"])
        self.assertIn("public_offer_pack", product_manifest["upgrade"]["checkout"]["publicOfferPackEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["publicOfferPackPolicy"], "review_copy_faq_release_notes_before_public_page")
        self.assertIn("launch_assets_kit.py", product_manifest["upgrade"]["checkout"]["launchAssetsKitTool"])
        self.assertIn("launch_assets_kit", product_manifest["upgrade"]["checkout"]["launchAssetsKitEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["launchAssetsKitPolicy"], "prepare_assets_release_draft_and_publication_checklist")
        self.assertIn("public_release_gate.py", product_manifest["upgrade"]["checkout"]["publicReleaseGateTool"])
        self.assertIn("public_release_gate", product_manifest["upgrade"]["checkout"]["publicReleaseGateEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["publicReleaseGatePolicy"], "confirm_tag_release_zip_checksum_support_and_rollback")
        self.assertIn("backend/sqx-edge-tool/tools/public_release_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("release_publication_record.py", product_manifest["upgrade"]["checkout"]["releasePublicationRecordTool"])
        self.assertIn("release_publication_record", product_manifest["upgrade"]["checkout"]["releasePublicationRecordEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["releasePublicationRecordPolicy"], "record_tag_release_asset_checksum_support_and_rollback_publication")
        self.assertIn("backend/sqx-edge-tool/tools/release_publication_record.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("post_release_monitor.py", product_manifest["upgrade"]["checkout"]["postReleaseMonitorTool"])
        self.assertIn("post_release_monitor", product_manifest["upgrade"]["checkout"]["postReleaseMonitorEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["postReleaseMonitorPolicy"], "monitor_incidents_activation_support_refunds_and_scale_decision")
        self.assertIn("backend/sqx-edge-tool/tools/post_release_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("hotfix_rollback_release.py", product_manifest["upgrade"]["checkout"]["hotfixRollbackReleaseTool"])
        self.assertIn("hotfix_rollback_release", product_manifest["upgrade"]["checkout"]["hotfixRollbackReleaseEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["hotfixRollbackReleasePolicy"], "prepare_hotfix_or_rollback_release_notes_comms_and_closure_evidence")
        self.assertIn("backend/sqx-edge-tool/tools/hotfix_rollback_release.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("customer_success_renewal.py", product_manifest["upgrade"]["checkout"]["customerSuccessRenewalTool"])
        self.assertIn("customer_success_renewal", product_manifest["upgrade"]["checkout"]["customerSuccessRenewalEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerSuccessRenewalPolicy"], "track_onboarding_activation_support_renewal_and_safe_expansion")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerCockpitEndpoint"], "/api/customer-cockpit")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerCockpitConfig"], "backend/sqx-edge-tool/config/customer_cockpit.json")
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["customerCockpitPolicy"],
            "render_redacted_operator_summary_without_license_payloads_or_raw_events",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["proBuyerPackConfig"], "backend/sqx-edge-tool/config/pro_buyer_pack.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["proBuyerPackResourceDir"], "resources/pro-buyer-pack")
        self.assertIn("pro_buyer_pack.py", product_manifest["upgrade"]["checkout"]["proBuyerPackValidationTool"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["proBuyerPackPolicy"],
            "ship_safe_buyer_material_without_license_payloads_private_keys_or_financial_promises",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateConfig"],
            "backend/sqx-edge-tool/config/buyer_onboarding_support_gate.json",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["buyerOnboardingResourceDir"], "resources/pro-buyer-pack/onboarding")
        self.assertIn("buyer_onboarding_support_gate.py", product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateTool"])
        self.assertIn("buyer_onboarding_support_gate", product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1Config"], "backend/sqx-edge-tool/config/template_pack_1.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1ResourceDir"], "resources/pro-template-pack-1")
        self.assertIn("template_pack_1_delivery.py", product_manifest["upgrade"]["checkout"]["templatePack1DeliveryTool"])
        self.assertIn("template_pack_1_delivery", product_manifest["upgrade"]["checkout"]["templatePack1EvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1OfferConfig"], "backend/sqx-edge-tool/config/template_pack_1_offer.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1OfferResourceDir"], "resources/pro-template-pack-1/offer")
        self.assertIn("template_pack_1_offer.py", product_manifest["upgrade"]["checkout"]["templatePack1OfferTool"])
        self.assertIn("template_pack_1_offer", product_manifest["upgrade"]["checkout"]["templatePack1OfferEvidenceDir"])
        self.assertIn("backend/sqx-edge-tool/tools/customer_success_renewal.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/customer_success_renewal", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/customer_cockpit", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/pro_buyer_pack", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/pro_buyer_pack.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/buyer_onboarding_support_gate", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_delivery", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_delivery.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_offer", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_offer.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_publication", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_publication.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_purchase_drill", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_handoff", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_handoff.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_sales_register", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_sales_register.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_feedback_cohort", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_feedback_cohort.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_action_plan", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_action_plan.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_specs", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_specs.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_assets", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_assets.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_offer_pack", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_offer_pack.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_publication", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_publication.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_purchase_drill", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_purchase_drill.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_handoff", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_handoff.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_sales_register", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_sales_register.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_feedback_cohort", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_feedback_cohort.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/buyer_ready_checkout_closeout", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/buyer_ready_checkout_closeout.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/public_buyer_page_cadence", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/public_buyer_page_cadence.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/first_controlled_buyer_log", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/first_controlled_buyer_log.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/post_sale_improvement_loop", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/post_sale_improvement_loop.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/post_sale_micro_updates", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/post_sale_micro_updates.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_readiness", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_buyer_readiness.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_outcome", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_buyer_outcome.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_step", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_distribution_step.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_distribution_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_buyer_facing_asset", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_buyer_facing_asset.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/private_asset_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/private_asset_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_publication_gate", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_publication_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/limited_publication_draft", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/limited_publication_draft.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/operator_publication_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/operator_publication_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/manual_limited_publication_record", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/manual_limited_publication_record.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/manual_publication_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/manual_publication_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_step", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_step.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_decision", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_decision.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_execution", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_execution.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_execution_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_execution_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_commercial_next_movement", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_commercial_next_movement.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_commercial_next_movement_execution", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_commercial_next_movement_execution.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_commercial_next_movement_execution_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_commercial_next_movement_execution_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_commercial_movement_decision", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_commercial_movement_decision.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_execution", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_execution.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_execution_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_execution_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m92_decision", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m92_decision.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m93_execution", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m93_execution.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m93_execution_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m93_execution_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m95_decision", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m95_decision.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m98_decision", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m98_decision.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/private_commercial_split.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("resources/pro-template-pack-1", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("resources/pro-template-pack-2", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["status"], "next_controlled_commercial_movement_from_m98_decision_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["webhookSignatureHeader"], "X-Signature")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["webhookSigningAlgorithm"], "hmac_sha256_hex")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["webhookSecretEnv"], "SQX_LEMON_WEBHOOK_SECRET")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["receiverEndpoint"], "/api/fulfillment/webhook/lemon")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayIngestEndpoint"], "/api/fulfillment/relay-ingest")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relaySignatureHeader"], "X-SQX-Relay-Signature")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relaySecretEnv"], "SQX_FULFILLMENT_RELAY_SECRET")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayServiceProject"], "backend/sqx-edge-relay")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayHealthEndpoint"], "/relay/health")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayConfigCheckEndpoint"], "/relay/config-check")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayObservabilityEndpoint"], "/relay/observability")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relaySnapshotEndpoint"], "/relay/observability/snapshot")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayWebhookEndpoint"], "/relay/webhook/lemon")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayQueueEndpoint"], "/relay/queue")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayDispatchEndpoint"], "/relay/dispatch")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayRequeueEndpoint"], "/relay/requeue")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayOperatorTokenEnv"], "SQX_RELAY_OPERATOR_TOKEN")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayWorkerMode"], "supervised_dispatch_loop")
        self.assertIn("dispatch_worker.py", product_manifest["upgrade"]["checkout"]["automation"]["relayWorkerScript"])
        self.assertIn("simulate_purchase_flow.py", product_manifest["upgrade"]["checkout"]["automation"]["relaySimulationTool"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayObservabilityMode"], "jsonl_events_and_queue_snapshots")
        self.assertIn("deployment_check.py", product_manifest["upgrade"]["checkout"]["automation"]["relayDeploymentCheckTool"])
        self.assertIn("staging_smoke.py", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingSmokeTool"])
        self.assertIn("staging_evidence.py", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingEvidenceTool"])
        self.assertIn("render_api_preflight.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderApiPreflightTool"])
        self.assertIn("Dockerfile", product_manifest["upgrade"]["checkout"]["automation"]["relayDockerfile"])
        self.assertIn("docker", product_manifest["upgrade"]["checkout"]["automation"]["relayDeploymentTargets"])
        self.assertIn("/relay/webhook/lemon", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingChecks"])
        self.assertIn("SQX_RELAY_OPERATOR_TOKEN", product_manifest["upgrade"]["checkout"]["automation"]["relayRequiredProductionSecrets"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["queueListEndpoint"], "/api/fulfillment/requests")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["processEndpoint"], "/api/fulfillment/process")
        self.assertIn("fulfillment_request.py", product_manifest["upgrade"]["checkout"]["automation"]["normalizerTool"])
        self.assertIn("fulfill_from_request.ps1", product_manifest["upgrade"]["checkout"]["automation"]["fulfillmentTool"])
        self.assertIn("relay_bundle.py", product_manifest["upgrade"]["checkout"]["automation"]["relayBundleTool"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["deduplicationKey"], "provider_event_id")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayRetryPolicy"], "exponential_backoff_remote_queue")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["variants"][0]["plan"], "pro_monthly")
        self.assertIn("No promete rentabilidad", product_manifest["upgrade"]["disclaimer"])
        self.assertIn("De idea a pipeline operativo SQX", product_manifest["marketing"]["tagline"])
        self.assertEqual(product_manifest["security"]["apiBoundary"], "local_only")
        self.assertIn("config/license.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertEqual(product_manifest["licensing"]["signatureMode"], "rsa_sha256_pkcs1_v1_5")
        self.assertEqual(product_manifest["licensing"]["signatureAlgorithm"], "RS256")
        self.assertIn("publicKey", product_manifest["licensing"])
        self.assertTrue(product_manifest["licensing"]["keyManagement"]["productionKeyRequired"])
        self.assertTrue(product_manifest["licensing"]["keyManagement"]["publicKeyReplacementRequiredBeforePublicSale"])
        self.assertEqual(product_manifest["licensing"]["keyManagement"]["privateKeyPolicy"], "never_commit_never_ship")
        self.assertIn("license_keypair.ps1", product_manifest["licensing"]["keyManagement"]["keypairTool"])
        self.assertIn("license_signer.py", product_manifest["licensing"]["keyManagement"]["signerTool"])
        self.assertIn("license_issue.py", product_manifest["licensing"]["keyManagement"]["issuerTool"])
        self.assertIn("license_keys", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("*_private_key.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/license_keypair.ps1", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/license_issue.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/checkout_live_readiness.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/commercial_release_candidate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/pilot_purchase_kit.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/limited_public_launch.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/post_launch_control.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/commercial_feedback_loop.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/public_offer_pack.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/launch_assets_kit.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_readiness", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_buyer_readiness.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_outcome", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_buyer_outcome.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_step", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_distribution_step.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_distribution_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_buyer_facing_asset", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_buyer_facing_asset.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/private_asset_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/private_asset_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_publication_gate", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_publication_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/limited_publication_draft", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/limited_publication_draft.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/operator_publication_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/operator_publication_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/manual_limited_publication_record", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/manual_limited_publication_record.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/manual_publication_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/manual_publication_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_step", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_step.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/private_commercial_split.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/customer_success_renewal", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/customer_cockpit", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/pro_buyer_pack", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/pro_buyer_pack.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/buyer_onboarding_support_gate", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_delivery", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_delivery.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_offer", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_offer.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_publication", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_publication.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_purchase_drill", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_handoff", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_handoff.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("resources/pro-template-pack-1", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/fulfillment_request.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/fulfill_from_request.ps1", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/relay_bundle.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/dukas_mt5_ohlc_download.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/mt5_ipc_diagnostic.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/config/dukas_mt5_download.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("data/ohlc", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("analysis_output", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("analysis_output/dukas_mt5_download", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("analysis_output/mt5_ipc_diagnostic", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("analysis_output/real_mtf_pipeline_run", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("fulfillment_request_*.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("webhook_event_*.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("relay_event_*.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("/api/license/status", server_py)
        self.assertIn("/api/license/check", server_py)
        self.assertIn("/api/license/import", server_py)
        self.assertIn("/api/license/clear", server_py)
        self.assertIn("store_relay_bundle", server_py)
        self.assertIn("def require_feature", server_py)
        self.assertIn('require_feature("project_generator.generate")', server_py)
        self.assertIn('require_feature("strategy_cleaner.apply")', server_py)
        self.assertIn("def check_feature", license_py)
        self.assertIn("verify_license_signature", license_py)
        self.assertIn("rsa_sha256_pkcs1_v1_5", license_py)
        self.assertIn("pro_active", license_py)

    def test_pipeline_mobile_layout_has_overflow_guards(self):
        css = (APP_ROOT / "css" / "dashboard.css").read_text(encoding="utf-8-sig")

        self.assertIn("#tab-pipeline .card-header", css)
        self.assertIn("flex-wrap:wrap", css)
        self.assertIn("#ps-plan-table", css)
        self.assertIn("overflow-x:auto", css)
        self.assertIn("#tab-pipeline .ps-funnel-step", css)
        self.assertIn("flex-wrap:wrap", css)

    def test_g6_institutional_dashboard_quick_actions_are_wired(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        css = (APP_ROOT / "css" / "dashboard.css").read_text(encoding="utf-8-sig")

        self.assertIn('id="ps-health-panel"', self.html)

        expected_js_patterns = [
            "window.quickAddToPlan",
            "window.quickToProjectGen",
            "catBase = String(cat || '').replace(/_S$/, '')",
            "window.promoteOrphanToPlan(key)",
            "writeCustomProjectInputs(document, config)",
            "renderPsHealth()",
            "ps-funnel-graph",
            "pf-count-big",
        ]
        for pattern in expected_js_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, dashboard_js)

        expected_css_patterns = [
            ".quick-actions",
            ".action-btn.btn-plan",
            ".action-btn.btn-pg",
            ".ps-health-panel",
            ".ps-h-item",
            ".ps-funnel-step-graph",
            ".pf-count-big",
        ]
        for pattern in expected_css_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, css)

    def test_pg7_project_generator_buyer_cfx_handoff_is_wired(self):
        pg_config = (APP_ROOT / "js" / "modules" / "project-generator-config.js").read_text(encoding="utf-8-sig")
        pg_bindings = (APP_ROOT / "js" / "modules" / "project-generator-bindings.js").read_text(encoding="utf-8-sig")
        pg_main = (APP_ROOT / "js" / "project-generator-main.js").read_text(encoding="utf-8-sig")
        css = (APP_ROOT / "css" / "dashboard.css").read_text(encoding="utf-8-sig")
        pg7_doc = PG7_PROJECT_GENERATOR_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")

        for element_id in [
            "pg-buyer-handoff-card",
            "pg-buyer-name",
            "pg-buyer-context",
            "pg-buyer-handoff-refresh",
            "pg-buyer-handoff-copy",
            "pg-buyer-handoff-download",
            "pg-buyer-handoff-summary",
            "pg-buyer-handoff-notes",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        for pattern in [
            "normalizeBuyerCfxHandoffInput",
            "buyerCfxHandoffSummary",
            "buyerCfxHandoffMarkdown",
            "buyerCfxHandoffFilename",
            "No promete rentabilidad",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, pg_config)

        for pattern in [
            "renderBuyerCfxHandoff",
            "copyBuyerCfxHandoff",
            "downloadBuyerCfxHandoff",
            "pg-buyer-handoff-refresh",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, pg_bindings)

        for pattern in [
            "pgRenderBuyerCfxHandoff",
            "pgCopyBuyerCfxHandoff",
            "pgDownloadBuyerCfxHandoff",
            "buyerCfxHandoffMarkdown",
            "buyerCfxHandoffFilename",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, pg_main)

        for pattern in [
            ".pg-buyer-handoff-card",
            ".pg-buyer-handoff-grid",
            ".pg-buyer-handoff-notes",
            ".pg-buyer-actions",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, css)

        for pattern in [
            "PG7 Project Generator Buyer .cfx Handoff",
            "No backend endpoint is added.",
            "No remote API call is made.",
            "No profitability or financial-result claim is made.",
            "Phase PG7: add buyer-specific `.cfx` handoff notes",
            "Project Generator buyer handoff track",
        ]:
            with self.subTest(pattern=pattern):
                self.assertTrue(pattern in pg7_doc or pattern in next_steps or pattern in governance, pattern)

    def test_t1_cloud_tester_architecture_contract_is_documented(self):
        t1 = T1_CLOUD_TESTER_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        operational_discipline = (PROJECT_ROOT / "DISCIPLINA_OPERATIVA.md").read_text(encoding="utf-8-sig")

        expected_t1_patterns = [
            "T1 Cloud Tester Architecture Contract",
            "controlled Vercel-hosted tester portal",
            "up to 10 invited testers",
            "15-day renewal cycles",
            "`SQX_Edge_Tester_Portal`",
            "`SQX_Edge_Access_Service`",
            "Deployment Protection",
            "Password Protection can protect preview/production URLs, but they are not sufficient",
            "Environment Variables hold secrets",
            "Cron Jobs may run a daily expiry/renewal scanner",
            "Edge Config can hold non-secret global switches",
            "status = active",
            "plan = tester_pro",
            "expires_at > now",
            "Renewal links are single-use",
            "visible watermark",
            "global kill switch",
            "Threat Model",
            "Shared tester password",
            "Vercel preview URL leaked",
            "Access/Security Gatekeeper",
            "No Vercel deployment.",
            "No tester account creation.",
        ]
        for pattern in expected_t1_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t1)

        expected_governance_patterns = [
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "Access/Security Gatekeeper",
            "`Txx`: cloud tester access",
            "Cloud Tester Access track",
            "Do not deploy tester access",
            "publish Vercel URLs",
        ]
        for pattern in expected_governance_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in [
            "Phase T1: define the Vercel-hosted tester architecture contract",
            "Phase T2: create/private-bootstrap `SQX_Edge_Tester_Portal`",
            "Phase T12: monitor abuse",
            "tester portal actions as external/security-sensitive",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in [
            "Portal tester Pro previsto",
            "`SQX_Edge_Tester_Portal`",
            "ciclo de renovacion de 15 dias",
            "Access/Security Gatekeeper",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in [
            "Access/Security Gatekeeper (Agente)",
            "Ecosistema Cloud y Tester Portal (Vercel)",
            "SQX_Edge_Tester_Portal",
            "Caducidad de testers",
            "ciclos de 15 días",
            "Deployment Protection",
            "Acciones externas bloqueadas por defecto",
            "no se despliega en Vercel",
            "no se crean cuentas tester",
            "no se publican URLs",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, operational_discipline)

    def test_t2_tester_portal_bootstrap_is_documented_and_safe(self):
        t2 = T2_TESTER_PORTAL_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")

        expected_files = [
            "README.md",
            ".gitignore",
            ".env.example",
            "package.json",
            "next-env.d.ts",
            "next.config.mjs",
            "tsconfig.json",
            "vercel.json",
            "scripts/vercel-preview-preflight.mjs",
            "scripts/vercel-protection-audit.mjs",
            "src/app/globals.css",
            "src/app/layout.tsx",
            "src/app/page.tsx",
            "src/app/login/page.tsx",
            "src/app/portal/page.tsx",
            "src/app/admin/testers/page.tsx",
            "src/app/expired/page.tsx",
            "src/app/renewal/page.tsx",
            "src/app/api/health/route.ts",
            "src/app/api/auth/login/route.ts",
            "src/app/api/auth/logout/route.ts",
            "src/app/api/tester/features/route.ts",
            "src/app/api/tester/renewal/route.ts",
            "src/app/api/admin/testers/route.ts",
            "src/app/api/cron/expire-testers/route.ts",
            "src/lib/access-contract.ts",
            "src/lib/auth-data-contract.ts",
            "src/lib/session-prototype.ts",
            "src/lib/entitlement-gates.ts",
            "src/lib/renewal-flow.ts",
            "src/lib/admin-console.ts",
            "src/lib/security-hardening.ts",
            "src/lib/deployment-protection.ts",
            "src/lib/security-headers.ts",
            "src/middleware.ts",
        ]
        for rel_path in expected_files:
            with self.subTest(rel_path=rel_path):
                self.assertTrue((TESTER_PORTAL_TEMPLATE_ROOT / rel_path).is_file(), rel_path)

        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        self.assertTrue(package["private"])
        self.assertEqual(package["dependencies"]["next"], "latest")
        self.assertEqual(package["dependencies"]["react"], "latest")
        self.assertIn("typecheck", package["scripts"])
        self.assertEqual(package["scripts"]["audit:vercel-protection"], "node scripts/vercel-protection-audit.mjs")

        env_example = (TESTER_PORTAL_TEMPLATE_ROOT / ".env.example").read_text(encoding="utf-8-sig")
        for pattern in (
            "AUTH_SECRET=\"replace-with-random-32-byte-secret\"",
            "TESTER_DB_URL=\"replace-with-private-database-url\"",
            "CRON_SECRET=\"replace-with-random-cron-secret\"",
            "EDGE_CONFIG=\"replace-with-vercel-edge-config-connection-string\"",
            "WATERMARK_SALT=\"replace-with-random-watermark-salt\"",
            "PASSWORD_PEPPER=\"replace-with-random-password-pepper-if-enabled\"",
            "T4_DEMO_LOGIN_ENABLED=\"false\"",
            "T4_DEMO_TESTER_EMAIL=\"tester@example.invalid\"",
            "T4_DEMO_ACCESS_CODE=\"replace-with-local-demo-access-code\"",
            "T5_DEMO_TESTER_PRO_ENABLED=\"false\"",
            "T6_DEMO_RENEWAL_STATE=\"pending_renewal\"",
            "T7_DEMO_ADMIN_CONSOLE_ENABLED=\"false\"",
            "T8_GLOBAL_KILL_SWITCH_ENABLED=\"false\"",
            "T8_RATE_LIMIT_ENABLED=\"false\"",
            "T8_RATE_LIMIT_MAX_REQUESTS=\"30\"",
            "T8_RATE_LIMIT_WINDOW_SECONDS=\"60\"",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, env_example)

        gitignore = (TESTER_PORTAL_TEMPLATE_ROOT / ".gitignore").read_text(encoding="utf-8-sig")
        self.assertIn(".env.*", gitignore)
        self.assertIn("!.env.example", gitignore)
        self.assertIn(".vercel/", gitignore)

        access_contract = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "access-contract.ts").read_text(encoding="utf-8-sig")
        for pattern in (
            "TESTER_RENEWAL_CYCLE_DAYS = 15",
            "\"pending_renewal\"",
            "\"blocked\"",
            "TesterPlan = \"tester_pro\"",
            "canAccessTesterPro",
            "buildTesterWatermark",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, access_contract)

        middleware = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "middleware.ts").read_text(encoding="utf-8-sig")
        session_prototype = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "session-prototype.ts").read_text(encoding="utf-8-sig")
        for pattern in (
            "SECURITY_HEADERS",
            "isProtectedPath",
            "hasPrototypeSession",
            "buildLoginUrl",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, middleware)
        for pattern in (
            "PROTECTED_PREFIXES",
            "\"/portal\"",
            "\"/admin\"",
            "\"/api/tester\"",
            "\"/api/admin\"",
            "SESSION_COOKIE_CONTRACT.name",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, session_prototype)

        cron_route = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "cron" / "expire-testers" / "route.ts").read_text(encoding="utf-8-sig")
        self.assertIn("process.env.CRON_SECRET", cron_route)
        self.assertIn("dry-run", cron_route)
        self.assertIn("T6 owns real renewal state changes", cron_route)

        security_headers = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "security-headers.ts").read_text(encoding="utf-8-sig")
        for pattern in (
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Referrer-Policy",
            "X-Robots-Tag",
            "Content-Security-Policy",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, security_headers)

        combined_template_text = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in TESTER_PORTAL_TEMPLATE_ROOT.rglob("*")
            if path.is_file() and "node_modules" not in path.parts and ".next" not in path.parts
        )
        forbidden_patterns = [
            SENSITIVE_LITERAL_FORBIDDEN,
            "vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ]
        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_template_text)

        for pattern in (
            "T2 Tester Portal Bootstrap",
            "public-safe bootstrap template",
            "templates/SQX_Edge_Tester_Portal/",
            "No Vercel deployment",
            "No tester accounts",
            "No production database",
            "T3 should define the auth data contract",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t2)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("T10m - manual/API Vercel correction or alternative no-deploy route proof", governance)
        self.assertIn("Current completed phase: T10l - Vercel Route Investigation.", next_steps)
        self.assertIn("Phase T2: create/private-bootstrap `SQX_Edge_Tester_Portal`", next_steps)
        self.assertIn("Phase T3: define tester auth data contract", next_steps)
        self.assertIn("T9c anade `audit:vercel-protection`", readme)
        self.assertIn("templates/SQX_Edge_Tester_Portal/", readme)

    def test_t3_tester_auth_data_contract_is_documented_and_safe(self):
        t3 = T3_TESTER_AUTH_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        auth_contract_path = TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "auth-data-contract.ts"
        auth_contract = auth_contract_path.read_text(encoding="utf-8-sig")

        self.assertTrue(auth_contract_path.is_file())

        for pattern in (
            "T3 Tester Auth Data Contract",
            "T3 is contract-only",
            "Required Records",
            "`testers`",
            "`tester_sessions`",
            "`tester_renewal_tokens`",
            "`tester_audit_events`",
            "Preferred algorithm: `argon2id`",
            "memory `19456 KiB`",
            "iterations `2`",
            "Cookie name: `__Host-sqx_tester_session`",
            "HttpOnly = true",
            "Secure = true",
            "SameSite = Strict",
            "do not store session IDs, JWTs, refresh tokens or credentials in `localStorage`",
            "Store only token hashes",
            "Default max age: 24 hours",
            "OWASP Password Storage Cheat Sheet",
            "OWASP Session Management Cheat Sheet",
            "OWASP Forgot Password Cheat Sheet",
            "OWASP Logging Cheat Sheet",
            "T4 can implement a login/session prototype",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t3)

        for pattern in (
            "PASSWORD_HASH_POLICY",
            "algorithm: \"argon2id\"",
            "minimumMemoryKiB: 19456",
            "minimumIterations: 2",
            "parallelism: 1",
            "pepperEnvName: \"PASSWORD_PEPPER\"",
            "plaintextPasswordStorageAllowed: false",
            "fastHashAlgorithmsAllowed: false",
            "SESSION_COOKIE_CONTRACT",
            "name: \"__Host-sqx_tester_session\"",
            "httpOnly: true",
            "secure: true",
            "sameSite: \"strict\"",
            "localStorageAllowed: false",
            "RENEWAL_TOKEN_CONTRACT",
            "oneUseOnly: true",
            "storeOnlyHash: true",
            "maxAgeHours: 24",
            "AUDIT_EVENT_TYPES",
            "\"login_failed\"",
            "\"renewal_approved\"",
            "\"tester_blocked\"",
            "TESTER_AUTH_REQUIRED_TABLES",
            "\"tester_audit_events\"",
            "TesterAuthRecord",
            "TesterSessionRecord",
            "RenewalTokenRecord",
            "TesterAuditEvent",
            "isActiveTesterRecord",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, auth_contract)

        combined_contract_text = t3 + "\n" + auth_contract
        forbidden_patterns = [
            SENSITIVE_LITERAL_FORBIDDEN,
            "vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
            "plainTextPassword",
        ]
        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_contract_text)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("T10m - manual/API Vercel correction or alternative no-deploy route proof", governance)
        self.assertIn("Current completed phase: T10l - Vercel Route Investigation.", next_steps)
        self.assertIn("Phase T3: define tester auth data contract", next_steps)
        self.assertIn("Phase T4: implement login/session prototype", next_steps)
        self.assertIn("T9c anade `audit:vercel-protection`", readme)
        self.assertIn("password hashing Argon2id", readme)

    def test_t4_login_session_prototype_is_documented_and_safe(self):
        t4 = T4_LOGIN_SESSION_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        login_page = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "login" / "page.tsx").read_text(encoding="utf-8-sig")
        login_route = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "auth" / "login" / "route.ts").read_text(encoding="utf-8-sig")
        logout_route = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "auth" / "logout" / "route.ts").read_text(encoding="utf-8-sig")
        middleware = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "middleware.ts").read_text(encoding="utf-8-sig")
        session_prototype_path = TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "session-prototype.ts"
        session_prototype = session_prototype_path.read_text(encoding="utf-8-sig")

        for rel_path in (
            "src/app/login/page.tsx",
            "src/app/api/auth/login/route.ts",
            "src/app/api/auth/logout/route.ts",
            "src/lib/session-prototype.ts",
        ):
            with self.subTest(rel_path=rel_path):
                self.assertTrue((TESTER_PORTAL_TEMPLATE_ROOT / rel_path).is_file(), rel_path)

        for pattern in (
            "T4 Login Session Prototype",
            "disabled-by-default demo flow",
            "does not deploy Vercel",
            "does not deploy Vercel, create tester accounts",
            "`src/app/api/auth/login/route.ts`",
            "`src/app/api/auth/logout/route.ts`",
            "`src/lib/session-prototype.ts`",
            "T4_DEMO_LOGIN_ENABLED=\"false\"",
            "cookie name: `__Host-sqx_tester_session`",
            "HttpOnly = true",
            "Secure = true",
            "SameSite = Strict",
            "Blocked requests redirect to `/login?next=<path>`",
            "T5 should add `tester_pro` entitlement gates",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t4)

        for pattern in (
            "DEMO_LOGIN_FLAG = \"T4_DEMO_LOGIN_ENABLED\"",
            "DEMO_TESTER_EMAIL_ENV = \"T4_DEMO_TESTER_EMAIL\"",
            "DEMO_ACCESS_CODE_ENV = \"T4_DEMO_ACCESS_CODE\"",
            "isDemoLoginEnabled",
            "process.env[DEMO_LOGIN_FLAG] === \"true\"",
            "PROTECTED_PREFIXES = [\"/portal\", \"/admin\", \"/api/tester\", \"/api/admin\"]",
            "SESSION_COOKIE_CONTRACT.name",
            "httpOnly: SESSION_COOKIE_CONTRACT.httpOnly",
            "secure: SESSION_COOKIE_CONTRACT.secure",
            "sameSite: SESSION_COOKIE_CONTRACT.sameSite",
            "path: SESSION_COOKIE_CONTRACT.path",
            "maxAge: SESSION_COOKIE_CONTRACT.maxAgeMinutes * 60",
            "crypto.randomUUID()",
            "demo_login_disabled",
            "invalid_demo_credential",
            "sanitizeRedirectTarget",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, session_prototype)

        for pattern in (
            "action=\"/api/auth/login\"",
            "method=\"post\"",
            "name=\"email\"",
            "name=\"accessCode\"",
            "autoComplete=\"one-time-code\"",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, login_page)

        self.assertIn("evaluatePrototypeLogin", login_route)
        self.assertIn("applySessionCookie", login_route)
        self.assertIn("NextResponse.redirect", login_route)
        self.assertIn("clearSessionCookie", logout_route)
        self.assertIn("buildLoginUrl", middleware)
        self.assertIn("hasPrototypeSession", middleware)
        self.assertIn("isProtectedPath", middleware)
        self.assertNotIn("new URL(\"/expired\"", middleware)

        combined_template_text = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in TESTER_PORTAL_TEMPLATE_ROOT.rglob("*")
            if path.is_file() and "node_modules" not in path.parts and ".next" not in path.parts
        )
        forbidden_patterns = [
            SENSITIVE_LITERAL_FORBIDDEN,
            "vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
            "localStorage.setItem",
            "sessionStorage.setItem",
        ]
        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_template_text)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("T10m - manual/API Vercel correction or alternative no-deploy route proof", governance)
        self.assertIn("Current completed phase: T10l - Vercel Route Investigation.", next_steps)
        self.assertIn("Phase T4: implement login/session prototype", next_steps)
        self.assertIn("Phase T5: add `tester_pro` entitlements", next_steps)
        self.assertIn("T9c anade `audit:vercel-protection`", readme)

    def test_t5_tester_pro_entitlement_gates_are_documented_and_safe(self):
        t5 = T5_TESTER_PRO_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        entitlement_path = TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "entitlement-gates.ts"
        entitlement_gates = entitlement_path.read_text(encoding="utf-8-sig")
        features_route = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "tester" / "features" / "route.ts").read_text(encoding="utf-8-sig")
        portal_page = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "portal" / "page.tsx").read_text(encoding="utf-8-sig")
        env_example = (TESTER_PORTAL_TEMPLATE_ROOT / ".env.example").read_text(encoding="utf-8-sig")

        self.assertTrue(entitlement_path.is_file())
        self.assertTrue((TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "tester" / "features" / "route.ts").is_file())

        for pattern in (
            "T5 Tester Pro Entitlement Gates",
            "server-side entitlement checks",
            "`src/lib/entitlement-gates.ts`",
            "`src/app/api/tester/features/route.ts`",
            "`sqx_dashboard_full`",
            "`strategy_builder`",
            "`project_generator`",
            "`views_creator`",
            "`buyer_handoff_exports`",
            "`support_case_bundle`",
            "T5_DEMO_TESTER_PRO_ENABLED=\"false\"",
            "`missing_session` with HTTP `401`",
            "`demo_entitlement_disabled` with HTTP `403`",
            "UI visibility is informational only.",
            "T6 should add 15-day expiry",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t5)

        for pattern in (
            "TESTER_PRO_FEATURES",
            "\"sqx_dashboard_full\"",
            "\"strategy_builder\"",
            "\"project_generator\"",
            "\"views_creator\"",
            "\"buyer_handoff_exports\"",
            "\"support_case_bundle\"",
            "DEMO_ENTITLEMENT_FLAG = \"T5_DEMO_TESTER_PRO_ENABLED\"",
            "isDemoTesterProEnabled",
            "hasPrototypeSession",
            "canAccessTesterPro",
            "missing_session",
            "demo_entitlement_disabled",
            "tester_pro_inactive",
            "status: \"active\"",
            "plan: \"tester_pro\"",
            "expiresAt",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, entitlement_gates)

        self.assertIn("evaluateTesterProGate", features_route)
        self.assertIn("NextResponse.json", features_route)
        self.assertIn("reasonCode: gate.reasonCode", features_route)
        self.assertIn("features: gate.features", features_route)
        self.assertIn("TESTER_PRO_FEATURES", portal_page)
        self.assertIn("/api/tester/features", portal_page)
        self.assertIn("T5_DEMO_TESTER_PRO_ENABLED=\"false\"", env_example)

        combined_template_text = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in TESTER_PORTAL_TEMPLATE_ROOT.rglob("*")
            if path.is_file() and "node_modules" not in path.parts and ".next" not in path.parts
        )
        for pattern in (
            SENSITIVE_LITERAL_FORBIDDEN,
            "vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
            "localStorage.setItem",
            "sessionStorage.setItem",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_template_text)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("T10m - manual/API Vercel correction or alternative no-deploy route proof", governance)
        self.assertIn("Current completed phase: T10l - Vercel Route Investigation.", next_steps)
        self.assertIn("Phase T5: add `tester_pro` entitlements", next_steps)
        self.assertIn("Phase T6: add 15-day expiry", next_steps)
        self.assertIn("T9c anade `audit:vercel-protection`", readme)

    def test_t6_15_day_expiry_renewal_flow_is_documented_and_safe(self):
        t6 = T6_RENEWAL_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        env_example = (TESTER_PORTAL_TEMPLATE_ROOT / ".env.example").read_text(encoding="utf-8-sig")
        renewal_flow_path = TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "renewal-flow.ts"
        renewal_flow = renewal_flow_path.read_text(encoding="utf-8-sig")
        renewal_route = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "tester" / "renewal" / "route.ts").read_text(encoding="utf-8-sig")
        renewal_page = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "renewal" / "page.tsx").read_text(encoding="utf-8-sig")
        portal_page = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "portal" / "page.tsx").read_text(encoding="utf-8-sig")

        self.assertTrue(renewal_flow_path.is_file())
        self.assertTrue((TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "tester" / "renewal" / "route.ts").is_file())

        for pattern in (
            "T6 15-Day Expiry Renewal Flow",
            "15 days",
            "manual approve/deny flow",
            "`src/lib/renewal-flow.ts`",
            "`src/app/api/tester/renewal/route.ts`",
            "`pending_renewal`",
            "`expired`",
            "`denied`",
            "`blocked`",
            "`approve_15_days`",
            "`deny`",
            "`block`",
            "`mode = manual-preview`",
            "`noMutation = true`",
            "`persistence = not_applied_in_template`",
            "No automatic renewal.",
            "No renewal email is sent.",
            "T7 should add an admin tester console",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t6)

        for pattern in (
            "DEMO_RENEWAL_STATE_ENV = \"T6_DEMO_RENEWAL_STATE\"",
            "RENEWAL_STATES",
            "\"pending_renewal\"",
            "\"expired\"",
            "\"denied\"",
            "\"blocked\"",
            "MANUAL_RENEWAL_DECISIONS",
            "\"approve_15_days\"",
            "addRenewalDays",
            "TESTER_RENEWAL_CYCLE_DAYS",
            "readDemoRenewalState",
            "buildDemoRenewalEntitlement",
            "classifyRenewalState",
            "evaluateRenewalGate",
            "buildRenewalDecisionPreview",
            "renewal_pending_operator_approval",
            "tester_expired",
            "renewal_denied",
            "tester_blocked",
            "manual-preview",
            "not_applied_in_template",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, renewal_flow)

        for pattern in (
            "hasPrototypeSession",
            "missing_session",
            "unsupported_decision",
            "GET(request: NextRequest)",
            "POST(request: NextRequest)",
            "buildRenewalDecisionPreview",
            "manual-review-only",
            "manual-preview",
            "noMutation: true",
            "operatorActionRequired",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, renewal_route)

        for pattern in (
            "TESTER_RENEWAL_CYCLE_DAYS",
            "MANUAL_RENEWAL_DECISIONS",
            "action=\"/api/tester/renewal\"",
            "method=\"post\"",
            "name=\"decision\"",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, renewal_page)

        self.assertIn("/renewal", portal_page)
        self.assertIn("MANUAL_RENEWAL_DECISIONS", portal_page)
        self.assertIn("T6_DEMO_RENEWAL_STATE=\"pending_renewal\"", env_example)
        self.assertIn("T6_DEMO_RENEWAL_STATE", template_readme)
        self.assertIn("src/lib/renewal-flow.ts", template_readme)
        self.assertIn("src/app/api/tester/renewal/route.ts", template_readme)
        self.assertIn("T10i must correct or replace the Vercel preview deployment route before another deployment attempt.", template_readme)

        combined_template_text = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in TESTER_PORTAL_TEMPLATE_ROOT.rglob("*")
            if path.is_file() and "node_modules" not in path.parts and ".next" not in path.parts
        )
        for pattern in (
            SENSITIVE_LITERAL_FORBIDDEN,
            "vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
            "localStorage.setItem",
            "sessionStorage.setItem",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_template_text)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("T10m - manual/API Vercel correction or alternative no-deploy route proof", governance)
        self.assertIn("docs/T6_15_DAY_EXPIRY_RENEWAL_FLOW.md", governance)
        self.assertIn("docs/T7_ADMIN_TESTER_CONSOLE.md", governance)
        self.assertIn("Current completed phase: T10l - Vercel Route Investigation.", next_steps)
        self.assertIn("Phase T6: add 15-day expiry", next_steps)
        self.assertIn("Phase T7: add admin tester console", next_steps)
        self.assertIn("T9c anade `audit:vercel-protection`", readme)
        self.assertIn("T10j para ejecutar una unica preview CLI default", readme)

    def test_t7_admin_tester_console_is_documented_and_safe(self):
        t7 = T7_ADMIN_CONSOLE_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        env_example = (TESTER_PORTAL_TEMPLATE_ROOT / ".env.example").read_text(encoding="utf-8-sig")
        admin_console_path = TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "admin-console.ts"
        admin_console = admin_console_path.read_text(encoding="utf-8-sig")
        admin_route = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "admin" / "testers" / "route.ts").read_text(encoding="utf-8-sig")
        admin_page = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "admin" / "testers" / "page.tsx").read_text(encoding="utf-8-sig")
        session_prototype = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "session-prototype.ts").read_text(encoding="utf-8-sig")
        portal_page = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "portal" / "page.tsx").read_text(encoding="utf-8-sig")
        css = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "globals.css").read_text(encoding="utf-8-sig")

        for rel_path in (
            "src/lib/admin-console.ts",
            "src/app/api/admin/testers/route.ts",
            "src/app/admin/testers/page.tsx",
        ):
            with self.subTest(rel_path=rel_path):
                self.assertTrue((TESTER_PORTAL_TEMPLATE_ROOT / rel_path).is_file(), rel_path)

        for pattern in (
            "T7 Admin Tester Console",
            "protected admin tester console",
            "`src/lib/admin-console.ts`",
            "`src/app/api/admin/testers/route.ts`",
            "`src/app/admin/testers/page.tsx`",
            "`create_tester`",
            "`renew_15_days`",
            "`deny_tester`",
            "`block_tester`",
            "`mode = operator-preview`",
            "`noMutation = true`",
            "`persistence = not_applied_in_template`",
            "T7_DEMO_ADMIN_CONSOLE_ENABLED=\"false\"",
            "`missing_session` with HTTP `401`",
            "`demo_admin_console_disabled` with HTTP `403`",
            "`unsupported_admin_action` with HTTP `400`",
            "No tester account is created.",
            "No renewal email is sent.",
            "`/api/admin` is protected",
            "T8 should harden rate limiting",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t7)

        for pattern in (
            "DEMO_ADMIN_CONSOLE_FLAG = \"T7_DEMO_ADMIN_CONSOLE_ENABLED\"",
            "ADMIN_TESTER_ACTIONS",
            "\"create_tester\"",
            "\"renew_15_days\"",
            "\"deny_tester\"",
            "\"block_tester\"",
            "isDemoAdminConsoleEnabled",
            "isAdminTesterAction",
            "buildDemoAdminTesterRows",
            "active.tester@example.invalid",
            "renewal.tester@example.invalid",
            "blocked.tester@example.invalid",
            "buildAdminActionPreview",
            "operator-preview",
            "tester_invited",
            "renewal_approved",
            "renewal_denied",
            "tester_blocked",
            "not_applied_in_template",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, admin_console)

        for pattern in (
            "hasPrototypeSession",
            "isDemoAdminConsoleEnabled",
            "missing_session",
            "demo_admin_console_disabled",
            "unsupported_admin_action",
            "GET(request: NextRequest)",
            "POST(request: NextRequest)",
            "buildAdminActionPreview",
            "noMutation: true",
            "operatorActionRequired",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, admin_route)

        for pattern in (
            "Admin tester console",
            "ADMIN_TESTER_ACTIONS",
            "buildDemoAdminTesterRows",
            "action=\"/api/admin/testers\"",
            "name=\"action\"",
            "name=\"testerId\"",
            "lastAuditEvent",
            "riskNote",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, admin_page)

        self.assertIn("\"/api/admin\"", session_prototype)
        self.assertIn("/admin/testers", portal_page)
        self.assertIn(".admin-table", css)
        self.assertIn(".status-blocked", css)
        self.assertIn("T7_DEMO_ADMIN_CONSOLE_ENABLED=\"false\"", env_example)
        self.assertIn("T7_DEMO_ADMIN_CONSOLE_ENABLED", template_readme)
        self.assertIn("src/lib/admin-console.ts", template_readme)
        self.assertIn("src/app/api/admin/testers/route.ts", template_readme)
        self.assertIn("src/app/admin/testers/page.tsx", template_readme)

        combined_template_text = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in TESTER_PORTAL_TEMPLATE_ROOT.rglob("*")
            if path.is_file() and "node_modules" not in path.parts and ".next" not in path.parts
        )
        for pattern in (
            SENSITIVE_LITERAL_FORBIDDEN,
            "vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
            "localStorage.setItem",
            "sessionStorage.setItem",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_template_text)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("T10m - manual/API Vercel correction or alternative no-deploy route proof", governance)
        self.assertIn("docs/T7_ADMIN_TESTER_CONSOLE.md", governance)
        self.assertIn("Current completed phase: T10l - Vercel Route Investigation.", next_steps)
        self.assertIn("Phase T7: add admin tester console", next_steps)
        self.assertIn("Phase T8: harden rate limiting", next_steps)
        self.assertIn("T9c anade `audit:vercel-protection`", readme)
        self.assertIn("T10j para ejecutar una unica preview CLI default", readme)

    def test_t8_tester_portal_security_hardening_is_documented_and_safe(self):
        t8 = T8_SECURITY_HARDENING_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        env_example = (TESTER_PORTAL_TEMPLATE_ROOT / ".env.example").read_text(encoding="utf-8-sig")
        security_hardening_path = TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "security-hardening.ts"
        deployment_protection_path = TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "deployment-protection.ts"
        security_hardening = security_hardening_path.read_text(encoding="utf-8-sig")
        deployment_protection = deployment_protection_path.read_text(encoding="utf-8-sig")
        middleware = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "middleware.ts").read_text(encoding="utf-8-sig")
        security_headers = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "lib" / "security-headers.ts").read_text(encoding="utf-8-sig")
        health_route = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "api" / "health" / "route.ts").read_text(encoding="utf-8-sig")
        portal_page = (TESTER_PORTAL_TEMPLATE_ROOT / "src" / "app" / "portal" / "page.tsx").read_text(encoding="utf-8-sig")

        for rel_path in (
            "src/lib/security-hardening.ts",
            "src/lib/deployment-protection.ts",
        ):
            with self.subTest(rel_path=rel_path):
                self.assertTrue((TESTER_PORTAL_TEMPLATE_ROOT / rel_path).is_file(), rel_path)

        for pattern in (
            "T8 Tester Portal Security Hardening",
            "rate-limit contracts",
            "stronger security headers",
            "visible tester watermark",
            "global kill switch",
            "`src/lib/security-hardening.ts`",
            "`src/lib/deployment-protection.ts`",
            "`T8_GLOBAL_KILL_SWITCH_ENABLED=\"false\"`",
            "`T8_RATE_LIMIT_ENABLED=\"false\"`",
            "`T8_RATE_LIMIT_MAX_REQUESTS=\"30\"`",
            "`T8_RATE_LIMIT_WINDOW_SECONDS=\"60\"`",
            "`X-RateLimit-Limit`",
            "`X-RateLimit-Remaining`",
            "`X-RateLimit-Reset`",
            "`Strict-Transport-Security = max-age=31536000; includeSubDomains; preload`",
            "`Cross-Origin-Opener-Policy = same-origin`",
            "`Cross-Origin-Resource-Policy = same-origin`",
            "`DEPLOYMENT_PROTECTION_CHECKLIST`",
            "No Vercel deployment.",
            "T9 can prepare a Vercel preview staging run",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t8)

        for pattern in (
            "HARDENING_ENV",
            "globalKillSwitch: \"T8_GLOBAL_KILL_SWITCH_ENABLED\"",
            "rateLimitEnabled: \"T8_RATE_LIMIT_ENABLED\"",
            "rateLimitMaxRequests: \"T8_RATE_LIMIT_MAX_REQUESTS\"",
            "rateLimitWindowSeconds: \"T8_RATE_LIMIT_WINDOW_SECONDS\"",
            "RATE_LIMIT_BUCKETS",
            "isGlobalKillSwitchEnabled",
            "isRateLimitEnabled",
            "readRateLimitMaxRequests",
            "readRateLimitWindowSeconds",
            "isKillSwitchExemptPath",
            "buildRateLimitKey",
            "evaluateRateLimit",
            "rate_limit_exceeded",
            "buildVisibleWatermark",
            "buildDemoVisibleWatermark",
            "demo-tester-local-only",
            "tester@example.invalid",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, security_hardening)

        for pattern in (
            "DEPLOYMENT_PROTECTION_CHECKLIST",
            "Vercel Deployment Protection enabled",
            "tester auth enabled before sharing any URL",
            "T8_GLOBAL_KILL_SWITCH_ENABLED tested before pilot",
            "T8_RATE_LIMIT_ENABLED tested before pilot",
            "no public indexing",
            "no tester invites or renewal emails",
            "no production database secrets committed",
            "watermark visible",
            "externalActionAllowed: false",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, deployment_protection)

        for pattern in (
            "isGlobalKillSwitchEnabled",
            "isKillSwitchExemptPath",
            "global_kill_switch_enabled",
            "evaluateRateLimit",
            "buildRateLimitKey",
            "rate_limit_exceeded",
            "Retry-After",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "applySecurityHeaders",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, middleware)

        for pattern in (
            "Strict-Transport-Security",
            "Cross-Origin-Opener-Policy",
            "Cross-Origin-Resource-Policy",
            "form-action 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "X-Robots-Tag",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, security_headers)

        for pattern in (
            "phase: \"T8\"",
            "containsTesterData: false",
            "hardening",
            "globalKillSwitchEnabled",
            "rateLimitEnabled",
            "deploymentProtection",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, health_route)

        for pattern in (
            "buildDemoVisibleWatermark",
            "buildDeploymentProtectionSummary",
            "watermark",
            "Hardening",
            "deployment-protection checks required before preview",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, portal_page)

        for pattern in (
            "T8_GLOBAL_KILL_SWITCH_ENABLED=\"false\"",
            "T8_RATE_LIMIT_ENABLED=\"false\"",
            "T8_RATE_LIMIT_MAX_REQUESTS=\"30\"",
            "T8_RATE_LIMIT_WINDOW_SECONDS=\"60\"",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, env_example)

        self.assertIn("src/lib/security-hardening.ts", template_readme)
        self.assertIn("src/lib/deployment-protection.ts", template_readme)
        self.assertIn("T10i must correct or replace the Vercel preview deployment route before another deployment attempt.", template_readme)

        combined_template_text = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in TESTER_PORTAL_TEMPLATE_ROOT.rglob("*")
            if path.is_file() and "node_modules" not in path.parts and ".next" not in path.parts
        )
        for pattern in (
            SENSITIVE_LITERAL_FORBIDDEN,
            "vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
            "localStorage.setItem",
            "sessionStorage.setItem",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_template_text)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("T10m - manual/API Vercel correction or alternative no-deploy route proof", governance)
        self.assertIn("docs/T8_TESTER_PORTAL_SECURITY_HARDENING.md", governance)
        self.assertIn("Current completed phase: T10l - Vercel Route Investigation.", next_steps)
        self.assertIn("Phase T8: harden rate limiting", next_steps)
        self.assertIn("Phase T9: run Vercel preview staging", next_steps)
        self.assertIn("T9c anade `audit:vercel-protection`", readme)
        self.assertIn("T10j para ejecutar una unica preview CLI default", readme)

    def test_t9_protected_vercel_preview_preflight_is_documented_and_safe(self):
        t9 = T9_VERCEL_PREFLIGHT_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        preflight_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-preview-preflight.mjs"
        preflight = preflight_path.read_text(encoding="utf-8-sig")

        self.assertTrue(preflight_path.is_file())
        self.assertEqual(package["scripts"]["preflight:vercel-preview"], "node scripts/vercel-preview-preflight.mjs")

        for pattern in (
            "T9 Protected Vercel Preview Preflight",
            "NO_GO_AUTH_BLOCKED",
            "The specified token is not valid",
            "Preview URL: not created",
            "Tester invites: not sent",
            "Renewal emails: not sent",
            "Real tester emails: not used",
            "templates/SQX_Edge_Tester_Portal/scripts/vercel-preview-preflight.mjs",
            "npm run preflight:vercel-preview",
            "npx vercel deploy --target=preview",
            "T9b should authenticate Vercel",
            "No preview URL is committed.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t9)

        for pattern in (
            "protected-preview-preflight",
            "T4_DEMO_LOGIN_ENABLED=\"false\"",
            "T5_DEMO_TESTER_PRO_ENABLED=\"false\"",
            "T7_DEMO_ADMIN_CONSOLE_ENABLED=\"false\"",
            "T8_GLOBAL_KILL_SWITCH_ENABLED=\"false\"",
            "T8_RATE_LIMIT_ENABLED=\"false\"",
            "DEPLOYMENT_PROTECTION_CHECKLIST",
            "Vercel Deployment Protection enabled",
            "global_kill_switch_enabled",
            "rate_limit_exceeded",
            "X-RateLimit-Limit",
            "vercel.json must keep framework=nextjs",
            ".vercel/project.json is local machine state",
            "recommendedDeployCommand",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, preflight)

        self.assertIn("scripts/vercel-preview-preflight.mjs", template_readme)
        self.assertIn("npm run preflight:vercel-preview", template_readme)
        self.assertIn("T10i must correct or replace the Vercel preview deployment route before another deployment attempt.", template_readme)

        combined_t9_text = t9 + "\n" + preflight + "\n" + template_readme
        for pattern in (
            SENSITIVE_LITERAL_FORBIDDEN,
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
            "https://",
            ".vercel.app",
            "@gmail.com",
            "@hotmail.com",
            "@outlook.com",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t9_text)

        self.assertIn("Current phase completed: T10l - Vercel Route Investigation.", governance)
        self.assertIn("T10m - manual/API Vercel correction or alternative no-deploy route proof", governance)
        self.assertIn("docs/T9_PROTECTED_VERCEL_PREVIEW_PREFLIGHT.md", governance)
        self.assertIn("docs/T9B_VERCEL_PREVIEW_DEPLOY_ROLLBACK.md", governance)
        self.assertIn("Current completed phase: T10l - Vercel Route Investigation.", next_steps)
        self.assertIn("Phase T9: run Vercel preview staging", next_steps)
        self.assertIn("Phase T9b: authenticate Vercel", next_steps)
        self.assertIn("Phase T9c: verify Vercel Deployment Protection", next_steps)
        self.assertIn("T9c anade `audit:vercel-protection`", readme)
        self.assertIn("T10j para ejecutar una unica preview CLI default", readme)

    def test_t9b_vercel_preview_deploy_rollback_is_documented_and_safe(self):
        t9b = T9B_VERCEL_ROLLBACK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        preflight = (TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-preview-preflight.mjs").read_text(encoding="utf-8-sig")
        gitignore = (TESTER_PORTAL_TEMPLATE_ROOT / ".gitignore").read_text(encoding="utf-8-sig")

        for pattern in (
            "T9b Vercel Preview Deploy Rollback",
            "target = production",
            "production aliases",
            "deployment was no longer inspectable",
            "public alias returned `404`",
            "Project exists: `sqx-edge-tester-portal`",
            "Active deployment: none",
            "Latest production URL: none",
            "Real tester emails: not committed.",
            "Public preview/prod URL in git: none.",
            "Do not commit raw emails.",
            "T9c should verify Deployment Protection",
            "No tester invite or email send",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t9b)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T9B_VERCEL_PREVIEW_DEPLOY_ROLLBACK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T9b: authenticate Vercel, verify Deployment Protection and execute protected preview deploy. Attempted; rolled back because CLI created production aliases",
            "Phase T9c: verify Vercel Deployment Protection before retrying preview deploy.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T9c anade `audit:vercel-protection`",
            "T9b autentico Vercel, intento deploy y lo elimino al detectar alias de produccion",
            "T10j para ejecutar una unica preview CLI default",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        self.assertIn("T9b Vercel Preview Deploy Rollback", changelog)
        self.assertIn("commits no tester emails", changelog)
        self.assertIn(".vercel/", gitignore)
        self.assertIn(".vercel", gitignore)

        for pattern in (
            ".vercel/project.json is local machine state",
            "gitignore.includes(\".vercel\")",
            "phase: \"T9b\"",
            "preview command verified not to alias production",
            "manual dashboard/API preview after Deployment Protection verification",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, preflight)

        combined_t9b_text = "\n".join([t9b, governance, next_steps, readme, changelog, preflight])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t9b_text)

    def test_t9c_vercel_deployment_protection_gate_is_documented_and_safe(self):
        t9c = T9C_VERCEL_PROTECTION_GATE_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        audit_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-protection-audit.mjs"
        audit = audit_path.read_text(encoding="utf-8-sig")

        self.assertTrue(audit_path.is_file())
        self.assertEqual(package["scripts"]["audit:vercel-protection"], "node scripts/vercel-protection-audit.mjs")

        for pattern in (
            "T9c Vercel Deployment Protection Gate",
            "does not deploy, publish a URL, invite testers, send emails",
            "Project name: `sqx-edge-tester-portal`",
            "Live deployment: false",
            "Latest deployment: none",
            "Domains: none",
            "Deployment Protection verdict: `NO_GO_PROTECTION_NOT_VERIFIED`",
            "External deploy allowed: false",
            "Standard Protection protects generated deployment URLs and previews",
            "All Deployments protects every URL",
            "Vercel Authentication can be managed on the project with `ssoProtection.deploymentType`",
            "Password Protection can be managed on the project with `passwordProtection.deploymentType`",
            "`audit:vercel-protection` exists and returns a safe NO-GO without `VERCEL_TOKEN`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t9c)

        for pattern in (
            "NO_GO_PROJECT_NOT_LINKED",
            "NO_GO_PROTECTION_NOT_VERIFIED",
            "GO_PROTECTION_VERIFIED",
            "VERCEL_TOKEN",
            "ssoProtection",
            "passwordProtection",
            "prod_deployment_urls_and_all_previews",
            "externalDeployAllowed: protectionVerified",
            "process.exit(protectionVerified ? 0 : 4)",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, audit)

        for pattern in (
            "scripts/vercel-protection-audit.mjs",
            "npm run audit:vercel-protection",
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
            "GO_PROTECTION_VERIFIED",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T9C_VERCEL_DEPLOYMENT_PROTECTION_GATE.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T9c: verify Vercel Deployment Protection before retrying preview deploy. Done as safe NO-GO gate",
            "Phase T9d: enable or verify Vercel Authentication/Password Protection privately",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T9e reintento preview con proteccion activa",
            "T10j para ejecutar una unica preview CLI default",
            "T9c anade `audit:vercel-protection`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        self.assertIn("T9c Vercel Deployment Protection Gate", changelog)
        self.assertIn("NO_GO_PROTECTION_NOT_VERIFIED", changelog)

        combined_t9c_text = "\n".join([t9c, governance, next_steps, readme, changelog, template_readme, audit])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t9c_text)

    def test_t9d_vercel_auth_protection_is_documented_and_safe(self):
        t9d = T9D_VERCEL_AUTH_PROTECTION_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")

        for pattern in (
            "T9d Vercel Authentication Protection Verified",
            "does not deploy, publish a URL, invite testers",
            "ssoProtection.deploymentType = prod_deployment_urls_and_all_previews",
            "Vercel Authentication with Standard Protection",
            "No token value was printed, committed or stored in the repository.",
            "status = GO_PROTECTION_VERIFIED",
            "ssoProtectionEnabled = true",
            "ssoDeploymentType = prod_deployment_urls_and_all_previews",
            "latestDeployment = none",
            "domains = 0",
            "externalDeployAllowed = true",
            "No deploy was executed in T9d.",
            "T9e should perform a preview-only deploy retry with strict inspection",
            "rollback immediately if Vercel reports production target or production aliases",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t9d)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T9D_VERCEL_AUTH_PROTECTION_VERIFIED.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T9d: enable or verify Vercel Authentication/Password Protection privately, then retry preview only after `GO_PROTECTION_VERIFIED`. Done",
            "Phase T9e: retry preview-only deploy with target and alias inspection",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T9e reintento preview con proteccion activa",
            "T10j para ejecutar una unica preview CLI default",
            "T9d activa/verifica Vercel Authentication Standard Protection",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "After T9d, the expected result is `GO_PROTECTION_VERIFIED`",
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        self.assertIn("T9d Vercel Authentication Protection Verified", changelog)
        self.assertIn("GO_PROTECTION_VERIFIED", changelog)

        combined_t9d_text = "\n".join([t9d, governance, next_steps, readme, changelog, template_readme])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t9d_text)

    def test_t9e_protected_preview_deploy_rollback_is_documented_and_safe(self):
        t9e = T9E_PROTECTED_PREVIEW_ROLLBACK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")

        for pattern in (
            "T9e Protected Preview Deploy Rollback",
            "T9e retries a protected preview deploy",
            "npm run preflight:vercel-preview` returned OK",
            "npm run audit:vercel-protection` returned `GO_PROTECTION_VERIFIED`",
            "The command was run without `--prod`",
            "target = production",
            "production alias created = true",
            "Deployment is no longer inspectable.",
            "Project list shows latest production URL: none.",
            "Public alias check returned `404`.",
            "successful safety rollback",
            "local CLI deploys are not safe enough for tester rollout",
            "The next attempt must not use the same local CLI deploy path",
            "T9f should prepare a preview-only deployment path",
            "Git/PR-based preview or API deployment proof",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t9e)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T9E_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T9e: retry preview-only deploy with target and alias inspection before sharing any URL; rollback immediately if target or aliases are production. Attempted and rolled back",
            "Phase T9f: prepare Git/PR-based preview or API deployment proof",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T9e reintento preview con proteccion activa",
            "T10j para ejecutar una unica preview CLI default",
            "T9e reintenta deploy sin `--prod`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        self.assertIn("T9e Protected Preview Deploy Rollback", changelog)
        self.assertIn("T9f as the safer path", changelog)
        self.assertIn("T10i must correct or replace the Vercel preview deployment route before another deployment attempt.", template_readme)

        combined_t9e_text = "\n".join([t9e, governance, next_steps, readme, changelog, template_readme])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t9e_text)

    def test_t9f_preview_path_proof_is_documented_and_safe(self):
        t9f = T9F_PREVIEW_PATH_PROOF_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_script = (TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-preview-path-proof.mjs").read_text(encoding="utf-8-sig")

        self.assertEqual(
            package["scripts"]["proof:vercel-preview-path"],
            "node scripts/vercel-preview-path-proof.mjs",
        )

        for pattern in (
            "T9f Preview Path Proof Gate",
            "does not deploy",
            "does not create repositories",
            "does not invite testers",
            "does not send emails",
            "does not publish or commit any Vercel URL",
            "NO_GO_GIT_PREVIEW_NOT_CONFIGURED",
            "GO_GIT_PREVIEW_PATH_READY",
            "T9g should connect or prepare a private Git preview source",
            "Contributor access is not required for local work right now",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t9f)

        for pattern in (
            "T9F_PREVIEW_BRANCH",
            "tester-preview",
            "reservedBranches",
            "NO_GO_PROJECT_NOT_LINKED",
            "NO_GO_TOKEN_NOT_AVAILABLE",
            "NO_GO_PREVIEW_BRANCH_RESERVED",
            "NO_GO_API_PROJECT_AUDIT_FAILED",
            "NO_GO_PROTECTION_NOT_VERIFIED",
            "NO_GO_GIT_PREVIEW_NOT_CONFIGURED",
            "NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION",
            "GO_GIT_PREVIEW_PATH_READY",
            "externalDeployAttempted: false",
            "git.linked",
            "project.link",
            "source: gitRepository ?",
            "previewBranchIsProduction",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof_script)

        for forbidden in (
            "vercel deploy",
            "--prod",
            "process.env.VERCEL_TOKEN)",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, proof_script)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T9F_PREVIEW_PATH_PROOF.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T9f: prepare Git/PR-based preview or API deployment proof that cannot auto-alias production before any URL is shared. Done",
            "Phase T9g: connect private Git/PR preview source before any tester URL is shared",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10j para ejecutar una unica preview CLI default",
            "T9f anade `proof:vercel-preview-path`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T9f Preview Path Proof Gate",
            "proof:vercel-preview-path",
            "T9g as the next safe step",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-preview-path-proof.mjs",
            "npm run proof:vercel-preview-path",
            "GO_GIT_PREVIEW_PATH_READY",
            "NO_GO_GIT_PREVIEW_NOT_CONFIGURED",
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t9f_text = "\n".join([
            t9f,
            governance,
            next_steps,
            readme,
            changelog,
            template_readme,
            proof_script,
        ])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t9f_text)

    def test_t9g_private_git_preview_source_is_documented_and_safe(self):
        t9g = T9G_PRIVATE_GIT_PREVIEW_SOURCE_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        proof_script = (TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-preview-path-proof.mjs").read_text(encoding="utf-8-sig")

        for pattern in (
            "T9g Private Git Preview Source",
            "private GitHub repository `CryptoLeon78/SQX_Edge_Tester_Portal`",
            "Pushed `main` and `tester-preview` before connecting Vercel",
            "No manual Vercel deploy command was run.",
            "GitHub repository privacy: private.",
            "Preview branch prepared: `tester-preview`.",
            "Vercel Git source: linked through the Vercel Project API `link` object.",
            "Preview proof gate: `GO_GIT_PREVIEW_PATH_READY`.",
            "Latest deployment after the connection: none.",
            "No post-connect push was made to trigger an automatic Vercel deployment.",
            "T10 should run one internal tester pilot before inviting external testers.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t9g)

        for pattern in (
            "const link = project.link ?? null",
            "source: gitRepository ? \"gitRepository\" : link ? \"link\" : null",
            "productionBranch",
            "previewBranchIsProduction",
            "GO_GIT_PREVIEW_PATH_READY",
            "externalDeployAttempted: false",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof_script)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T9G_PRIVATE_GIT_PREVIEW_SOURCE.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T9g: connect private Git/PR preview source before any tester URL is shared. Done",
            "Phase T10: run one internal tester pilot before inviting external testers.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10j para ejecutar una unica preview CLI default",
            "T9g crea el repo privado `SQX_Edge_Tester_Portal`",
            "GO_GIT_PREVIEW_PATH_READY",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T9g Private Git Preview Source",
            "Vercel Project API `link` connections",
            "GO_GIT_PREVIEW_PATH_READY",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "The proof accepts Vercel Project API Git connections exposed either as `gitRepository` or as `link`.",
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
            "T10 proved that a Git deployment from `tester-preview` can still report `target=production`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t9g_text = "\n".join([
            t9g,
            governance,
            next_steps,
            readme,
            changelog,
            template_readme,
            proof_script,
        ])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t9g_text)

    def test_t10_internal_preview_rollback_is_documented_and_safe(self):
        t10 = T10_INTERNAL_PREVIEW_ROLLBACK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")

        for pattern in (
            "T10 Internal Preview Target Rollback",
            "safety rollback, not as a successful internal pilot",
            "private-only marker commit",
            "Pushed `tester-preview` to trigger the first Git-based Vercel deployment",
            "Removed the deployment immediately after Vercel reported a production target",
            "target = production",
            "githubCommitRef = tester-preview",
            "githubRepoVisibility = private",
            "The deployment is no longer inspectable.",
            "The Vercel project reports no latest deployment.",
            "The Vercel project reports no domains.",
            "The public project alias returns `404`.",
            "T10b must fix the Vercel preview target mapping before any tester URL is shared.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10_INTERNAL_PREVIEW_ROLLBACK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10: run one internal tester pilot before inviting external testers. Attempted and rolled back",
            "Phase T10b: fix Vercel preview target mapping before any tester URL is shared.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10 intento preview interno desde `tester-preview`",
            "T10j para ejecutar una unica preview CLI default",
            "T10 dispara el primer piloto interno desde `tester-preview`",
            "elimina el deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10 Internal Preview Target Rollback",
            "Vercel reports `target = production`",
            "no latest deployment, no domains",
            "T10b as the next required step",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
            "T10 proved that a Git deployment from `tester-preview` can still report `target=production`",
            "Do not create another deployment on the current project ID.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10_text = "\n".join([t10, governance, next_steps, readme, changelog, template_readme])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10_text)

    def test_t10b_vercel_target_guard_is_documented_and_safe(self):
        t10b = T10B_VERCEL_TARGET_GUARD_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        guard = (TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-target-guard.mjs").read_text(encoding="utf-8-sig")

        self.assertEqual(package["scripts"]["prebuild"], "node scripts/vercel-target-guard.mjs")

        for pattern in (
            "T10b Vercel Target Guard",
            "containment fix, not as a successful tester preview",
            "Added `scripts/vercel-target-guard.mjs`",
            "Added `prebuild` so Vercel runs the guard before `next build`",
            "NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH",
            "The guard exited with code `43`.",
            "The deployment ended in `ERROR`, not `READY`.",
            "The failed deployment was removed.",
            "The project now reports no latest deployment.",
            "The project now reports no domains.",
            "T10c should resolve the underlying Vercel mapping",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10b)

        for pattern in (
            "VERCEL_ENV",
            "VERCEL_GIT_COMMIT_REF",
            "SQX_ALLOWED_PRODUCTION_BRANCHES",
            "NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH",
            "process.exit(43)",
            "GO_TARGET_GUARD_PASSED",
            "allowedProductionBranches",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, guard)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10B_VERCEL_TARGET_GUARD.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10b: fix Vercel preview target mapping before any tester URL is shared. Contained with a build-time guard",
            "Phase T10c: correct Vercel Git/preview mapping or define an explicit API preview path before any tester URL is shared.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10c define una ruta API preview explicita sin desplegar",
            "T10j para ejecutar una unica preview CLI default",
            "T10b anade `vercel-target-guard.mjs` al `prebuild`",
            "codigo 43",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10b Vercel Target Guard",
            "NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH",
            "no latest deployment, no domains and no shared URL",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-target-guard.mjs",
            "T10b build-time guard",
            "T10i must correct or replace the Vercel preview deployment route",
            "`production/tester-preview` fails before publication",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10b_text = "\n".join([t10b, governance, next_steps, readme, changelog, template_readme, guard])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10b_text)

    def test_t10c_explicit_api_preview_path_is_documented_and_safe(self):
        t10c = T10C_EXPLICIT_API_PREVIEW_PATH_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof = (TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-explicit-preview-proof.mjs").read_text(encoding="utf-8-sig")

        self.assertEqual(
            package["scripts"]["proof:vercel-explicit-preview"],
            "node scripts/vercel-explicit-preview-proof.mjs",
        )

        for pattern in (
            "T10c Explicit API Preview Path",
            "no-deploy proof",
            "productionBranch = main",
            "target = production",
            "Added `scripts/vercel-explicit-preview-proof.mjs`",
            "target: \"preview\"",
            "does not call the deployment endpoint",
            "GO_EXPLICIT_API_PREVIEW_PATH_READY",
            "No deployment was created in T10c",
            "private tester portal repo was not pushed in T10c",
            "T10d may execute one explicit API preview deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10c)

        for pattern in (
            "T10C_PREVIEW_BRANCH",
            "T10C_EXPECTED_PRODUCTION_BRANCH",
            "GO_EXPLICIT_API_PREVIEW_PATH_READY",
            "target: \"preview\"",
            "externalDeployAttempted: false",
            "NO_GO_PRODUCTION_BRANCH_UNEXPECTED",
            "NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION",
            "fetchProject",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10C_EXPLICIT_API_PREVIEW_PATH.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10c: correct Vercel Git/preview mapping or define an explicit API preview path before any tester URL is shared. Done as no-deploy explicit API preview proof",
            "Phase T10d: execute one explicit API preview deployment with target inspection before any tester URL is shared.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10c define una ruta API preview explicita sin desplegar",
            "T10j para ejecutar una unica preview CLI default",
            "T10c anade `proof:vercel-explicit-preview`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10c Explicit API Preview Path",
            "proof:vercel-explicit-preview",
            "target: \"preview\"",
            "private tester repo unpushed in T10c",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-explicit-preview-proof.mjs",
            "npm run proof:vercel-explicit-preview",
            "GO_EXPLICIT_API_PREVIEW_PATH_READY",
            "T10i must correct or replace the Vercel preview deployment route",
            "without creating a deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10c_text = "\n".join([t10c, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
            "/v13/deployments",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10c_text)

    def test_t10d_explicit_api_preview_rollback_is_documented_and_safe(self):
        t10d = T10D_EXPLICIT_API_PREVIEW_ROLLBACK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")

        for pattern in (
            "T10d Explicit API Preview Rollback",
            "rollback, not as a successful tester preview",
            "Sent an explicit request with `target: \"preview\"`",
            "Removed the deployment immediately after Vercel reported `target = production`",
            "NO_GO_TARGET_NOT_PREVIEW_ROLLED_BACK",
            "The deployment was created only for inspection.",
            "The API returned `target = production`.",
            "The deployment was removed immediately.",
            "No tester URL was shared.",
            "The Vercel project now reports no latest deployment.",
            "The Vercel project now reports no domains.",
            "T10e must fix or recreate the Vercel preview deployment path",
            "Do not push another trigger commit and do not create another deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10d)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10D_EXPLICIT_API_PREVIEW_ROLLBACK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10d: execute one explicit API preview deployment with target inspection before any tester URL is shared. Attempted and rolled back",
            "Phase T10e: attempted an omitted-target API preview deployment and rolled it back",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10j para ejecutar una unica preview CLI default",
            "T10d ejecuta una unica preview API explicita",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10d Explicit API Preview Rollback",
            "target = production",
            "no latest deployment, no domains and no shared URL",
            "T10e as the required project/path correction",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
            "explicit API request with `target: \"preview\"` can return `target=production`",
            "Do not create another deployment on the current project ID.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10d_text = "\n".join([t10d, governance, next_steps, readme, changelog, template_readme])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10d_text)

    def test_t10e_omitted_target_preview_rollback_is_documented_and_safe(self):
        t10e = T10E_OMITTED_TARGET_PREVIEW_ROLLBACK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-omitted-target-preview-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-omitted-target-preview"],
            "node scripts/vercel-omitted-target-preview-proof.mjs",
        )

        for pattern in (
            "T10e Omitted Target Preview Rollback",
            "omit `target` so the deployment should default to preview",
            "rollback, not as a successful tester preview",
            "Added `scripts/vercel-omitted-target-preview-proof.mjs`",
            "GO_OMITTED_TARGET_PREVIEW_PATH_READY",
            "NO_GO_TARGET_NOT_PREVIEW_ROLLED_BACK",
            "The API request omitted `target`.",
            "The API still returned `target = production`.",
            "The deployment was removed immediately.",
            "The Vercel project now reports no latest deployment.",
            "The Vercel project now reports no domains.",
            "Do not create another deployment on the current project ID.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10e)

        for pattern in (
            "T10E_PREVIEW_BRANCH",
            "GO_OMITTED_TARGET_PREVIEW_PATH_READY",
            "omittedTargetForPreview: true",
            "externalDeployAttempted: false",
            "NO_GO_PRODUCTION_BRANCH_UNEXPECTED",
            "NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION",
            "fetchProject",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("target: \"preview\"", proof)
        self.assertNotIn("/v13/deployments", proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10E_OMITTED_TARGET_PREVIEW_ROLLBACK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10e: attempted an omitted-target API preview deployment and rolled it back",
            "Phase T10f: recreate or separate the Vercel preview project before any tester URL is shared.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10e intento preview API con `target` omitido",
            "T10j para ejecutar una unica preview CLI default",
            "T10e anade `proof:vercel-omitted-target-preview`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10e Omitted Target Preview Rollback",
            "proof:vercel-omitted-target-preview",
            "target = production",
            "no latest deployment, no domains and no shared URL",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-omitted-target-preview-proof.mjs",
            "npm run proof:vercel-omitted-target-preview",
            "GO_OMITTED_TARGET_PREVIEW_PATH_READY",
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
            "Do not create another deployment on the current project ID.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10e_text = "\n".join([t10e, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10e_text)

    def test_t10f_separated_preview_project_is_documented_and_safe(self):
        t10f = T10F_SEPARATED_PREVIEW_PROJECT_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-preview-project-separation-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-preview-project-separation"],
            "node scripts/vercel-preview-project-separation-proof.mjs",
        )

        for pattern in (
            "T10f Separated Preview Project",
            "safe separation step, not as a deployment or tester rollout",
            "Created a new Vercel project named `sqx-edge-tester-preview`",
            "Did not deploy the tester portal.",
            "Did not link or publish a tester URL.",
            "GO_PREVIEW_PROJECT_SEPARATED",
            "Project separation: preview project and legacy project are different projects.",
            "Live deployment: false.",
            "Latest deployment: none.",
            "Domains: none.",
            "Git connection: not linked yet.",
            "T10g must link the private tester portal repository",
            "Do not deploy from the separated project until T10g proves",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10f)

        for pattern in (
            "T10F_PREVIEW_PROJECT_NAME",
            "T10F_LEGACY_PROJECT_NAME",
            "T10F_VERCEL_TEAM_ID",
            "GO_PREVIEW_PROJECT_SEPARATED",
            "NO_GO_PREVIEW_PROJECT_MISSING",
            "NO_GO_PROJECT_NOT_SEPARATED",
            "NO_GO_PROJECT_HAS_PUBLIC_SURFACE",
            "externalDeployAttempted: false",
            "gitLinked",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("vercel deploy", proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10F_SEPARATED_PREVIEW_PROJECT.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10f: recreate or separate the Vercel preview project before any tester URL is shared. Done as separated, undeployed preview project",
            "Phase T10g: link the private tester portal repository to the separated preview project and prove Git/protection settings without deploying.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10f separo un proyecto preview Vercel nuevo",
            "T10j para ejecutar una unica preview CLI default",
            "T10f anade `proof:vercel-preview-project-separation`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10f Separated Preview Project",
            "proof:vercel-preview-project-separation",
            "without deploying, linking Git, adding domains or sharing any URL",
            "T10g as the required private Git linking",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-preview-project-separation-proof.mjs",
            "npm run proof:vercel-preview-project-separation",
            "GO_PREVIEW_PROJECT_SEPARATED",
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10f_text = "\n".join([t10f, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10f_text)

    def test_t10g_linked_preview_project_is_documented_and_safe(self):
        t10g = T10G_LINKED_PREVIEW_PROJECT_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-linked-preview-project-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-linked-preview-project"],
            "node scripts/vercel-linked-preview-project-proof.mjs",
        )

        for pattern in (
            "T10g Linked Preview Project Proof",
            "no-deploy Git-link proof, not as a tester rollout",
            "Connected the GitHub repository `CryptoLeon78/SQX_Edge_Tester_Portal`",
            "Did not run `vercel deploy`.",
            "Did not push a post-connect trigger commit",
            "GO_LINKED_PREVIEW_PROJECT_READY",
            "Project name: `sqx-edge-tester-preview`.",
            "Git provider: GitHub.",
            "Production branch: `main`.",
            "Intended preview branch: `tester-preview`.",
            "Deployment Protection: Vercel SSO protection is enabled.",
            "Latest deployment: none.",
            "Domains: none.",
            "T10h must execute exactly one protected preview deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10g)

        for pattern in (
            "T10G_PREVIEW_PROJECT_NAME",
            "T10G_GIT_ORG",
            "T10G_GIT_REPO",
            "T10G_EXPECTED_PRODUCTION_BRANCH",
            "T10G_PREVIEW_BRANCH",
            "GO_LINKED_PREVIEW_PROJECT_READY",
            "NO_GO_GIT_LINK_NOT_PRIVATE_TESTER_PORTAL",
            "NO_GO_PRODUCTION_BRANCH_UNEXPECTED",
            "NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION",
            "NO_GO_DEPLOYMENT_PROTECTION_NOT_VERIFIED",
            "deploymentProtectionVerified",
            "externalDeployAttempted: false",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("vercel deploy", proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10G_LINKED_PREVIEW_PROJECT_PROOF.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10g: link the private tester portal repository to the separated preview project and prove Git/protection settings without deploying. Done as linked no-deploy proof",
            "Phase T10h: execute exactly one protected preview deployment from the separated project with immediate target inspection before any tester URL is shared. Attempted and rolled back",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10g linko el repo privado del portal tester al proyecto preview separado",
            "T10j para ejecutar una unica preview CLI default",
            "T10g anade `proof:vercel-linked-preview-project`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10g Linked Preview Project Proof",
            "proof:vercel-linked-preview-project",
            "without deploying or sharing a URL",
            "T10h as the single protected preview deployment inspection phase",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-linked-preview-project-proof.mjs",
            "npm run proof:vercel-linked-preview-project",
            "GO_LINKED_PREVIEW_PROJECT_READY",
            "T10i must correct or replace the Vercel preview deployment route",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10g_text = "\n".join([t10g, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10g_text)

    def test_t10h_protected_preview_deploy_rollback_is_documented_and_safe(self):
        t10h = T10H_PROTECTED_PREVIEW_ROLLBACK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-protected-preview-rollback-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-protected-preview-rollback"],
            "node scripts/vercel-protected-preview-rollback-proof.mjs",
        )

        for pattern in (
            "T10h Protected Preview Deploy Rollback",
            "rollback, not as a successful tester preview",
            "Requested `target=preview`",
            "Used the separated project `sqx-edge-tester-preview`",
            "NO_GO_TARGET_NOT_PREVIEW_GUARD_ROLLBACK",
            "The requested target was preview.",
            "Vercel returned `target = production`.",
            "The T10b guard blocked the build with exit code 43.",
            "The deployment was removed immediately.",
            "The separated Vercel project now reports no latest deployment.",
            "The separated Vercel project now reports no domains.",
            "T10i must correct or replace the Vercel preview deployment route",
            "Do not share any tester URL until a deployment returns `target = preview`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10h)

        for pattern in (
            "T10H_PREVIEW_PROJECT_NAME",
            "GO_PROTECTED_PREVIEW_ROLLBACK_CLEAN",
            "NO_GO_ROLLBACK_NOT_CLEAN",
            "requestedTarget: \"preview\"",
            "observedTarget: \"production\"",
            "NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH",
            "rollbackStatus: \"removed\"",
            "externalDeployAttempted: false",
            "T10i must correct or replace the Vercel preview deployment route",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("vercel deploy", proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10H_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10h: execute exactly one protected preview deployment from the separated project with immediate target inspection before any tester URL is shared. Attempted and rolled back",
            "Phase T10i: correct or replace the Vercel preview deployment route before another deployment attempt.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10h intento una preview protegida desde el proyecto separado",
            "T10j para ejecutar una unica preview CLI default",
            "T10h anade `proof:vercel-protected-preview-rollback`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10h Protected Preview Deploy Rollback",
            "proof:vercel-protected-preview-rollback",
            "target = production",
            "exit code 43",
            "T10i as the required preview-route correction phase",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-protected-preview-rollback-proof.mjs",
            "npm run proof:vercel-protected-preview-rollback",
            "GO_PROTECTED_PREVIEW_ROLLBACK_CLEAN",
            "T10i must correct or replace the Vercel preview deployment route before another deployment attempt.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10h_text = "\n".join([t10h, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10h_text)

    def test_t10i_cli_default_preview_route_is_documented_and_safe(self):
        t10i = T10I_CLI_DEFAULT_PREVIEW_ROUTE_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-cli-default-preview-route-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-cli-default-preview-route"],
            "node scripts/vercel-cli-default-preview-route-proof.mjs",
        )

        for pattern in (
            "T10i CLI Default Preview Route Proof",
            "no-deploy route proof, not as a tester rollout",
            "vercel deploy --force --yes --format json --skip-domain",
            "No `--prod`.",
            "No `--target`.",
            "GO_CLI_DEFAULT_PREVIEW_ROUTE_READY",
            "separated project has no latest deployment",
            "separated project has no domains",
            "approved command shape omits `--prod` and `--target`",
            "T10j may execute exactly one CLI default preview deployment",
            "Do not push a trigger commit to the private tester portal repo",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10i)

        for pattern in (
            "T10I_PREVIEW_PROJECT_NAME",
            "T10I_EXPECTED_PRODUCTION_BRANCH",
            "T10I_PREVIEW_BRANCH",
            "GO_CLI_DEFAULT_PREVIEW_ROUTE_READY",
            "NO_GO_PROJECT_HAS_PUBLIC_SURFACE",
            "NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION",
            "NO_GO_DEPLOYMENT_PROTECTION_NOT_VERIFIED",
            "vercel deploy --force --yes --format json --skip-domain",
            "requiredAbsentFlags: [\"--prod\", \"--target\"]",
            "externalDeployAttempted: false",
            "T10j may execute exactly one CLI default preview deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10I_CLI_DEFAULT_PREVIEW_ROUTE.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10i: correct or replace the Vercel preview deployment route before another deployment attempt. Done as CLI default preview route proof",
            "Phase T10j: execute exactly one CLI default preview deployment with immediate target inspection and rollback on mismatch.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10i corrigio la siguiente ruta preview hacia `vercel deploy` por defecto",
            "T10j para ejecutar una unica preview CLI default",
            "T10i anade `proof:vercel-cli-default-preview-route`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10i CLI Default Preview Route Proof",
            "proof:vercel-cli-default-preview-route",
            "forbidding `--prod` and `--target`",
            "T10j as the single deployment inspection phase",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-cli-default-preview-route-proof.mjs",
            "npm run proof:vercel-cli-default-preview-route",
            "GO_CLI_DEFAULT_PREVIEW_ROUTE_READY",
            "T10j may execute exactly one CLI default preview deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10i_text = "\n".join([t10i, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10i_text)

    def test_t10j_cli_default_preview_command_rollback_is_documented_and_safe(self):
        t10j = T10J_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-cli-default-preview-command-rollback-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-cli-default-preview-command-rollback"],
            "node scripts/vercel-cli-default-preview-command-rollback-proof.mjs",
        )

        for pattern in (
            "T10j CLI Default Preview Command Rollback",
            "command rollback, not as a tester rollout",
            "NO_GO_CLI_DEFAULT_PREVIEW_COMMAND_INVALID",
            "Vercel rejected the command before creating a deployment.",
            "Deployment id: missing.",
            "Rollback was not needed because no deployment existed.",
            "The --skip-domain option can only be used with production deployments.",
            "vercel deploy --force --yes --format json",
            "No `--skip-domain`.",
            "T10k may execute exactly one CLI default preview deployment",
            "Do not push a trigger commit to the private tester portal repo",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10j)

        for pattern in (
            "T10J_PREVIEW_PROJECT_NAME",
            "GO_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK_CLEAN",
            "NO_GO_PROJECT_HAS_PUBLIC_SURFACE",
            "NO_GO_DEPLOYMENT_PROTECTION_NOT_VERIFIED",
            "--skip-domain option can only be used with production deployments",
            "deploymentId: \"missing\"",
            "rollbackStatus: \"not_needed\"",
            "vercel deploy --force --yes --format json",
            "requiredAbsentFlags: [\"--prod\", \"--target\", \"--skip-domain\"]",
            "T10k may execute exactly one CLI default preview deployment without --skip-domain",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10J_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10j: execute exactly one CLI default preview deployment with immediate target inspection and rollback on mismatch. Attempted command was rejected before deployment",
            "Phase T10k: execute exactly one CLI default preview deployment without `--skip-domain`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10j ejecuto el comando CLI default aprobado",
            "T10m para correccion manual/API o ruta alternativa",
            "T10j anade `proof:vercel-cli-default-preview-command-rollback`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10j CLI Default Preview Command Rollback",
            "proof:vercel-cli-default-preview-command-rollback",
            "rejects `--skip-domain` before creating a preview deployment",
            "T10k as the corrected inspection phase",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-cli-default-preview-command-rollback-proof.mjs",
            "npm run proof:vercel-cli-default-preview-command-rollback",
            "GO_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK_CLEAN",
            "T10k may execute exactly one CLI default preview deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10j_text = "\n".join([t10j, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10j_text)

    def test_t10k_cli_default_preview_rollback_is_documented_and_safe(self):
        t10k = T10K_CLI_DEFAULT_PREVIEW_ROLLBACK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-cli-default-preview-rollback-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-cli-default-preview-rollback"],
            "node scripts/vercel-cli-default-preview-rollback-proof.mjs",
        )

        for pattern in (
            "T10k CLI Default Preview Rollback",
            "rollback, not as a successful tester preview",
            "Used no `--prod`.",
            "Used no `--target`.",
            "Used no `--skip-domain`.",
            "NO_GO_CLI_DEFAULT_PREVIEW_TARGET_PRODUCTION_ROLLBACK",
            "Vercel returned `target = production`.",
            "The T10b guard blocked the build with exit code 43.",
            "Alias surface was observed before removal.",
            "The deployment was removed immediately.",
            "The separated Vercel project now reports no latest deployment.",
            "T10l must investigate or replace the Vercel route without another deployment attempt.",
            "Do not run another deployment until T10l produces a no-deploy GO.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10k)

        for pattern in (
            "T10K_PREVIEW_PROJECT_NAME",
            "GO_CLI_DEFAULT_PREVIEW_ROLLBACK_CLEAN",
            "NO_GO_ROLLBACK_NOT_CLEAN",
            "observedTarget: \"production\"",
            "readyState: \"ERROR\"",
            "NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH",
            "aliasSurfaceObservedBeforeRemoval: true",
            "rollbackStatus: \"removed\"",
            "T10l must investigate or replace the Vercel route without another deployment attempt",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10K_CLI_DEFAULT_PREVIEW_ROLLBACK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10k: execute exactly one CLI default preview deployment without `--skip-domain`, with immediate target inspection and rollback on mismatch. Attempted and rolled back",
            "Phase T10l: investigate or replace the Vercel route without another deployment attempt.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10k ejecuto una preview CLI default corregida",
            "T10m para correccion manual/API o ruta alternativa",
            "T10k anade `proof:vercel-cli-default-preview-rollback`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10k CLI Default Preview Rollback",
            "proof:vercel-cli-default-preview-rollback",
            "Vercel still returns `target = production`",
            "T10l as a no-deploy Vercel route investigation/replacement phase",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-cli-default-preview-rollback-proof.mjs",
            "npm run proof:vercel-cli-default-preview-rollback",
            "GO_CLI_DEFAULT_PREVIEW_ROLLBACK_CLEAN",
            "T10l must investigate or replace the Vercel route without another deployment attempt",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10k_text = "\n".join([t10k, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10k_text)

    def test_t10l_vercel_route_investigation_is_documented_and_safe(self):
        t10l = T10L_VERCEL_ROUTE_INVESTIGATION_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-route-investigation-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-route-investigation"],
            "node scripts/vercel-route-investigation-proof.mjs",
        )

        for pattern in (
            "T10l Vercel Route Investigation",
            "no-deploy investigation, not as a tester rollout",
            "NO_GO_VERCEL_ROUTE_REQUIRES_MANUAL_TARGET_FIX_OR_REPLACEMENT",
            "Did not run `vercel deploy`.",
            "project.productionBranch` is missing while `link.productionBranch` is `main`",
            "`project.targets` is empty.",
            "`autoAssignCustomDomains` is enabled.",
            "`productionDeploymentsFastLane` is enabled.",
            "T10m must perform manual dashboard/API correction",
            "Do not run another deployment until T10m produces a no-deploy GO.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10l)

        for pattern in (
            "T10L_PREVIEW_PROJECT_NAME",
            "NO_GO_VERCEL_ROUTE_REQUIRES_MANUAL_TARGET_FIX_OR_REPLACEMENT",
            "project.productionBranch is missing while link.productionBranch is main",
            "project.targets is empty",
            "autoAssignCustomDomains is enabled",
            "productionDeploymentsFastLane is enabled",
            "officialCliPreviewRouteExpected",
            "externalDeployAttempted: false",
            "T10m must perform manual dashboard/API correction or define an alternative no-deploy route proof",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("vercel deploy --force", proof)

        for pattern in (
            "Current phase completed: T10l - Vercel Route Investigation.",
            "T10m - manual/API Vercel correction or alternative no-deploy route proof",
            "docs/T10L_VERCEL_ROUTE_INVESTIGATION.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10l - Vercel Route Investigation.",
            "Phase T10l: investigate or replace the Vercel route without another deployment attempt. Done as no-deploy investigation",
            "Phase T10m: manual/API Vercel correction or alternative no-deploy route proof before any further deployment.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10l investigo Vercel sin deploy",
            "T10m para correccion manual/API o ruta alternativa",
            "T10l anade `proof:vercel-route-investigation`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10l Vercel Route Investigation",
            "proof:vercel-route-investigation",
            "missing top-level production branch",
            "T10m as manual/API correction or alternative no-deploy route proof",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-route-investigation-proof.mjs",
            "npm run proof:vercel-route-investigation",
            "NO_GO_VERCEL_ROUTE_REQUIRES_MANUAL_TARGET_FIX_OR_REPLACEMENT",
            "T10m must perform manual dashboard/API correction",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10l_text = "\n".join([t10l, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10l_text)

    def test_t10m_vercel_config_hardening_is_documented_and_safe(self):
        t10m = T10M_VERCEL_CONFIG_HARDENING_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        vercel_config = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "vercel.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-config-hardening-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-config-hardening"],
            "node scripts/vercel-config-hardening-proof.mjs",
        )
        self.assertFalse(vercel_config["github"]["autoAlias"])

        for pattern in (
            "T10m Vercel Config Hardening",
            "configuration hardening, not as a tester rollout",
            "autoAssignCustomDomains = false",
            "previewDeploymentsDisabled = false",
            "Did not run `vercel deploy`.",
            "Did not call the Vercel deployments creation API.",
            "GO_CONFIG_HARDENED_NO_DEPLOY_TARGET_STILL_UNPROVEN",
            "T10n must perform one of these before any deployment",
            "Do not run another deployment until T10n produces a no-deploy GO",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10m)

        for pattern in (
            "T10M_APPLY",
            "DRY_RUN_VERCEL_CONFIG_HARDENING_READY",
            "GO_CONFIG_HARDENED_NO_DEPLOY_TARGET_STILL_UNPROVEN",
            "autoAssignCustomDomains: false",
            "previewDeploymentsDisabled: false",
            "externalDeployAttempted: false",
            "externalConfigMutationAttempted",
            "PATCH",
            "T10n must prove or replace the preview route",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("vercel deploy", proof)

        for pattern in (
            "Current phase completed: T10m - Vercel Config Hardening.",
            "T10n - no-deploy preview target proof or Vercel route replacement",
            "docs/T10M_VERCEL_CONFIG_HARDENING.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10m - Vercel Config Hardening.",
            "Phase T10m: manual/API Vercel correction or alternative no-deploy route proof before any further deployment. Done as Vercel Project API hardening without deployment",
            "Phase T10n: no-deploy preview target proof or Vercel route replacement before any further deployment.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10m endurecio la configuracion Vercel por API sin deploy",
            "T10n para proof no-deploy de target/ruta",
            "T10m anade `proof:vercel-config-hardening`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10m Vercel Config Hardening",
            "proof:vercel-config-hardening",
            "autoAssignCustomDomains = false",
            "T10n as the next no-deploy route proof/replacement phase",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-config-hardening-proof.mjs",
            "npm run proof:vercel-config-hardening",
            "T10M_APPLY=1",
            "GO_CONFIG_HARDENED_NO_DEPLOY_TARGET_STILL_UNPROVEN",
            "T10n must prove or replace the Vercel preview route",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10m_text = "\n".join([t10m, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10m_text)

    def test_t10n_vercel_route_decision_is_documented_and_safe(self):
        t10n = T10N_VERCEL_ROUTE_DECISION_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "vercel-route-decision-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:vercel-route-decision"],
            "node scripts/vercel-route-decision-proof.mjs",
        )

        for pattern in (
            "T10n Vercel Route Decision",
            "no-deploy decision gate",
            "NO_GO_CURRENT_VERCEL_ROUTE_REPLACEMENT_REQUIRED",
            "Did not run `vercel deploy`.",
            "Did not call the Vercel deployments creation API.",
            "Did not patch project settings.",
            "Vercel still reports `productionDeploymentsFastLane`.",
            "No documented no-deploy API field proves the future deployment target.",
            "T10o must prepare one of these options",
            "Do not run another deployment until T10o produces a no-deploy GO",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10n)

        for pattern in (
            "T10N_PREVIEW_PROJECT_NAME",
            "NO_GO_CURRENT_VERCEL_ROUTE_REPLACEMENT_REQUIRED",
            "currentRouteApprovedForDeployment: false",
            "replacementRequired: true",
            "noDeployGoForCurrentRoute: false",
            "productionDeploymentsFastLane remains reported by the Project API",
            "future deployment target cannot be proven without creating a deployment",
            "externalDeployAttempted: false",
            "externalConfigMutationAttempted: false",
            "T10o must prepare a replacement route or manual provider-level proof before any deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("PATCH", proof)

        for pattern in (
            "Current phase completed: T10n - Vercel Route Decision.",
            "T10o - replacement route or provider-level no-deploy proof before any deployment",
            "docs/T10N_VERCEL_ROUTE_DECISION.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10n - Vercel Route Decision.",
            "Phase T10n: no-deploy preview target proof or Vercel route replacement before any further deployment. Done as route decision NO-GO",
            "Phase T10o: replacement route or provider-level no-deploy proof before any deployment.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10n rechaza la ruta Vercel actual",
            "T10o para ruta alternativa o proof manual/provider-level",
            "T10n anade `proof:vercel-route-decision`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10n Vercel Route Decision",
            "proof:vercel-route-decision",
            "current Vercel route remains rejected for rollout",
            "T10o as replacement route or provider-level proof",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/vercel-route-decision-proof.mjs",
            "npm run proof:vercel-route-decision",
            "NO_GO_CURRENT_VERCEL_ROUTE_REPLACEMENT_REQUIRED",
            "T10o must prepare a replacement route or manual provider-level proof",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10n_text = "\n".join([t10n, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10n_text)

    def test_t10o_replacement_route_contract_is_documented_and_safe(self):
        t10o = T10O_REPLACEMENT_ROUTE_CONTRACT_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "replacement-route-contract-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:replacement-route-contract"],
            "node scripts/replacement-route-contract-proof.mjs",
        )

        for pattern in (
            "T10o Replacement Route Contract",
            "no-deploy replacement-route contract",
            "GO_REPLACEMENT_ROUTE_CONTRACT_READY_NO_DEPLOY",
            "fresh_staging_route_with_no_deploy_preflight",
            "current_vercel_route",
            "Did not run `vercel deploy`.",
            "Did not call any deployment creation endpoint.",
            "Did not mutate Vercel project settings.",
            "Did not create a new external project.",
            "T10p may start only after explicit approval",
            "Deployment Protection must be enabled before any URL exists.",
            "No tester emails, tester accounts, passwords, tokens or secrets.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10o)

        for pattern in (
            'phase: "T10o"',
            'result: "GO_REPLACEMENT_ROUTE_CONTRACT_READY_NO_DEPLOY"',
            'selectedRoute: "fresh_staging_route_with_no_deploy_preflight"',
            'rejectedRoute: "current_vercel_route"',
            "currentRouteApprovedForDeployment: false",
            "replacementRequired: true",
            "externalDeployAttempted: false",
            "externalConfigMutationAttempted: false",
            "externalProjectCreationAttempted: false",
            "testerUrlPublished: false",
            "testerEmailsCommitted: false",
            "no deployment until replacement preflight returns GO",
            "verify project settings without deployment after explicit approval",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("PATCH", proof)
        self.assertNotIn("fetch(", proof)

        for pattern in (
            "Current phase completed: T10o - Replacement Route Contract.",
            "T10p - create or verify a fresh staging route only after explicit approval",
            "docs/T10O_REPLACEMENT_ROUTE_CONTRACT.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10o - Replacement Route Contract.",
            "Phase T10o: replacement route or provider-level no-deploy proof before any deployment. Done as no-deploy replacement-route contract",
            "Phase T10p: create or verify a fresh staging route only after explicit approval",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10o deja lista una ruta alternativa contractual sin deploy",
            "T10p para crear/verificar una ruta staging nueva",
            "T10o anade `proof:replacement-route-contract`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10o Replacement Route Contract",
            "proof:replacement-route-contract",
            "fresh_staging_route_with_no_deploy_preflight",
            "T10p as the explicitly approved fresh staging route preflight",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/replacement-route-contract-proof.mjs",
            "npm run proof:replacement-route-contract",
            "GO_REPLACEMENT_ROUTE_CONTRACT_READY_NO_DEPLOY",
            "T10p must create or verify the fresh staging route only with explicit approval",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10o_text = "\n".join([t10o, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10o_text)

    def test_t10p_fresh_staging_route_preflight_is_documented_and_safe(self):
        t10p = T10P_FRESH_STAGING_ROUTE_PREFLIGHT_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "fresh-staging-route-preflight-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:fresh-staging-route-preflight"],
            "node scripts/fresh-staging-route-preflight-proof.mjs",
        )

        for pattern in (
            "T10p Fresh Staging Route Preflight",
            "does not create or verify an external project",
            "GO_FRESH_STAGING_ROUTE_PREFLIGHT_READY_NO_EXTERNAL_ACTION",
            "fresh_staging_route_with_no_deploy_preflight",
            "current_vercel_route_rejected",
            "Did not run `vercel deploy`.",
            "Did not call any deployment creation endpoint.",
            "Did not call any provider API.",
            "Did not create a Vercel project or any alternative provider project.",
            "Did not link GitHub to a new provider project.",
            "A broad \"continue\" is not enough",
            "No tester email in git.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10p)

        for pattern in (
            'phase: "T10p"',
            'result: "GO_FRESH_STAGING_ROUTE_PREFLIGHT_READY_NO_EXTERNAL_ACTION"',
            'selectedRoute: "fresh_staging_route_with_no_deploy_preflight"',
            'currentRouteStatus: "current_vercel_route_rejected"',
            "externalApiCalled: false",
            "externalDeployAttempted: false",
            "externalProjectCreated: false",
            "externalProjectLinked: false",
            "testerUrlPublished: false",
            "testerEmailsCommitted: false",
            "provider-level or dashboard/API proof before first deployment",
            "create a fresh protected Vercel staging project without deployment",
            "verify an already-created fresh staging project without deployment",
            "select a non-Vercel protected staging provider route without deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("PATCH", proof)
        self.assertNotIn("fetch(", proof)

        for pattern in (
            "Current phase completed: T10p - Fresh Staging Route Preflight.",
            "T10q - request exact approval to create or verify a fresh protected staging route without deployment",
            "docs/T10P_FRESH_STAGING_ROUTE_PREFLIGHT.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10p - Fresh Staging Route Preflight.",
            "Phase T10p: create or verify a fresh staging route only after explicit approval, with no-deploy preflight before any deployment. Done as local no-external-action preflight",
            "Phase T10q: request exact approval to create or verify a fresh protected staging route without deployment.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10p deja listo el preflight local de ruta staging fresca",
            "T10q para pedir aprobacion exacta",
            "T10p anade `proof:fresh-staging-route-preflight`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10p Fresh Staging Route Preflight",
            "proof:fresh-staging-route-preflight",
            "GO_FRESH_STAGING_ROUTE_PREFLIGHT_READY_NO_EXTERNAL_ACTION",
            "T10q as the first exact external-action approval gate",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/fresh-staging-route-preflight-proof.mjs",
            "npm run proof:fresh-staging-route-preflight",
            "GO_FRESH_STAGING_ROUTE_PREFLIGHT_READY_NO_EXTERNAL_ACTION",
            "T10q must request exact approval before creating or verifying any provider route",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10p_text = "\n".join([t10p, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10p_text)

    def test_t10q_fresh_staging_route_access_check_is_documented_and_safe(self):
        t10q = T10Q_FRESH_STAGING_ROUTE_ACCESS_CHECK_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "fresh-staging-route-access-check-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:fresh-staging-route-access-check"],
            "node scripts/fresh-staging-route-access-check-proof.mjs",
        )

        for pattern in (
            "T10q Fresh Staging Route Access Check",
            "receives explicit approval",
            "NO_GO_FRESH_STAGING_ROUTE_CREATION_BLOCKED_BY_CLI_AUTH",
            "sqx-edge-tester-staging",
            "sqx-edge-tester-preview",
            "Did not run `vercel deploy`.",
            "Did not call any deployment creation endpoint.",
            "Did not create a Vercel project or any alternative provider project.",
            "Did not link GitHub to a new provider project.",
            "Approval for the intended action is now recorded.",
            "there is no `VERCEL_TOKEN`",
            "T10r must provide one exact write-capable path",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10q)

        for pattern in (
            'phase: "T10q"',
            'result: "NO_GO_FRESH_STAGING_ROUTE_CREATION_BLOCKED_BY_CLI_AUTH"',
            'requestedAction: "create_or_verify_fresh_protected_staging_route_without_deployment"',
            'preferredProjectName: "sqx-edge-tester-staging"',
            'currentRejectedProjectName: "sqx-edge-tester-preview"',
            "readOnlyVercelVisibility: true",
            "writeCapableCliSessionAvailable: false",
            "vercelTokenAvailableInEnvironment: false",
            "externalDeployAttempted: false",
            "deploymentCreationEndpointCalled: false",
            "externalProjectCreated: false",
            "externalProjectLinked: false",
            "testerUrlPublished: false",
            "testerEmailsCommitted: false",
            "Vercel CLI project listing timed out waiting for interactive authentication",
            "provide a scoped VERCEL_TOKEN through local environment only",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("PATCH", proof)
        self.assertNotIn("fetch(", proof)

        for pattern in (
            "Current phase completed: T10q - Fresh Staging Route Access Check.",
            "T10r - authenticate Vercel CLI or provide local `VERCEL_TOKEN`",
            "docs/T10Q_FRESH_STAGING_ROUTE_ACCESS_CHECK.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10q - Fresh Staging Route Access Check.",
            "Phase T10q: request exact approval to create or verify a fresh protected staging route without deployment. Done as access check",
            "Phase T10r: authenticate Vercel CLI or provide local `VERCEL_TOKEN`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10q registra aprobacion explicita",
            "T10r para autenticar Vercel CLI",
            "T10q anade `proof:fresh-staging-route-access-check`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10q Fresh Staging Route Access Check",
            "proof:fresh-staging-route-access-check",
            "NO_GO_FRESH_STAGING_ROUTE_CREATION_BLOCKED_BY_CLI_AUTH",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/fresh-staging-route-access-check-proof.mjs",
            "npm run proof:fresh-staging-route-access-check",
            "NO_GO_FRESH_STAGING_ROUTE_CREATION_BLOCKED_BY_CLI_AUTH",
            "T10r must authenticate Vercel CLI or provide a local `VERCEL_TOKEN`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10q_text = "\n".join([t10q, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10q_text)

    def test_t10r_fresh_staging_project_created_is_documented_and_safe(self):
        t10r = T10R_FRESH_STAGING_PROJECT_CREATED_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "fresh-staging-project-created-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:fresh-staging-project-created"],
            "node scripts/fresh-staging-project-created-proof.mjs",
        )

        for pattern in (
            "T10r Fresh Staging Project Created",
            "does not deploy, does not link Git",
            "GO_FRESH_STAGING_PROJECT_CREATED_NO_DEPLOY",
            "sqx-edge-tester-staging",
            "sqx-edge-tester-preview",
            "Verified no deployments exist for the new project.",
            "Verified the project has no domains.",
            "Did not run `vercel deploy`.",
            "Did not call any deployment creation endpoint.",
            "Did not link GitHub to the new project.",
            "latestDeployment = null",
            "domains = []",
            "Deployment count: `0`.",
            "T10s must verify or enable the protection/settings layer",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10r)

        for pattern in (
            'phase: "T10r"',
            'result: "GO_FRESH_STAGING_PROJECT_CREATED_NO_DEPLOY"',
            'freshProjectName: "sqx-edge-tester-staging"',
            'freshProjectId: "prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ"',
            'teamId: "team_43avYcdXjtKKE2GtwkOwbNKa"',
            'rejectedRouteProjectName: "sqx-edge-tester-preview"',
            "cliWritePathAvailable: true",
            "projectCreated: true",
            "projectSeparateFromRejectedRoute: true",
            "live: false",
            "latestDeployment: null",
            "domains: []",
            "deploymentCount: 0",
            "privatePortalRelinked: false",
            "gitLinkedToFreshProject: false",
            "externalDeployAttempted: false",
            "deploymentCreationEndpointCalled: false",
            "testerUrlPublished: false",
            "T10s_verify_or_enable_protection_settings_before_any_link_or_deploy",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("PATCH", proof)
        self.assertNotIn("fetch(", proof)

        for pattern in (
            "Current phase completed: T10r - Fresh Staging Project Created.",
            "T10s - verify or enable protection/settings for `sqx-edge-tester-staging`",
            "docs/T10R_FRESH_STAGING_PROJECT_CREATED.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10r - Fresh Staging Project Created.",
            "Phase T10r: authenticate Vercel CLI or provide local `VERCEL_TOKEN`, then create or verify `sqx-edge-tester-staging` without deployment. Done",
            "Phase T10s: verify or enable protection/settings for `sqx-edge-tester-staging` before any Git link or deployment.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10r anade `proof:fresh-staging-project-created`",
            "T10s anade `proof:staging-protection-verified`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10r Fresh Staging Project Created",
            "proof:fresh-staging-project-created",
            "GO_FRESH_STAGING_PROJECT_CREATED_NO_DEPLOY",
            "no deployments, no domains, no latest deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/fresh-staging-project-created-proof.mjs",
            "npm run proof:fresh-staging-project-created",
            "GO_FRESH_STAGING_PROJECT_CREATED_NO_DEPLOY",
            "T10s must verify or enable protection/settings",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10r_text = "\n".join([t10r, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10r_text)

    def test_t10s_staging_protection_verified_is_documented_and_safe(self):
        t10s = T10S_STAGING_PROTECTION_VERIFIED_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "staging-protection-verified-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:staging-protection-verified"],
            "node scripts/staging-protection-verified-proof.mjs",
        )

        for pattern in (
            "T10s Staging Protection Verified",
            "GO_STAGING_PROTECTION_VERIFIED_NO_DEPLOY",
            "sqx-edge-tester-staging",
            "all_except_custom_domains",
            "Git fork protection: enabled.",
            "Deployment count: `0`.",
            "Did not run `vercel deploy`.",
            "Did not call any deployment creation endpoint.",
            "Did not link GitHub to the staging project.",
            "T10t may link the private tester portal working tree",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10s)

        for pattern in (
            'phase: "T10s"',
            'result: "GO_STAGING_PROTECTION_VERIFIED_NO_DEPLOY"',
            'projectName: "sqx-edge-tester-staging"',
            'projectId: "prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ"',
            "ssoProtectionEnabled: true",
            'ssoDeploymentType: "all_except_custom_domains"',
            "gitForkProtectionEnabled: true",
            "live: false",
            "latestDeployment: null",
            "domains: []",
            "deploymentCount: 0",
            "projectSettingsChangedInT10s: false",
            "privatePortalRelinked: false",
            "gitLinkedToFreshProject: false",
            "externalDeployAttempted: false",
            "deploymentCreationEndpointCalled: false",
            "testerUrlPublished: false",
            "T10t_no_deploy_staging_link_or_setup_before_any_deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("PATCH", proof)
        self.assertNotIn("fetch(", proof)

        for pattern in (
            "Current phase completed: T10s - Staging Protection Verified.",
            "T10t - link or configure staging without deployment and without publishing a URL",
            "docs/T10S_STAGING_PROTECTION_VERIFIED.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10s - Staging Protection Verified.",
            "Phase T10s: verify or enable protection/settings for `sqx-edge-tester-staging` before any Git link or deployment. Done",
            "Phase T10t: link or configure staging without deployment and without publishing a URL.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10s anade `proof:staging-protection-verified`",
            "T10t anade `proof:staging-local-link`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10s Staging Protection Verified",
            "proof:staging-protection-verified",
            "GO_STAGING_PROTECTION_VERIFIED_NO_DEPLOY",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/staging-protection-verified-proof.mjs",
            "npm run proof:staging-protection-verified",
            "GO_STAGING_PROTECTION_VERIFIED_NO_DEPLOY",
            "T10t has linked the private tester portal working tree",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10s_text = "\n".join([t10s, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10s_text)

    def test_t10t_staging_local_link_configured_is_documented_and_safe(self):
        t10t = T10T_STAGING_LOCAL_LINK_CONFIGURED_DOC.read_text(encoding="utf-8-sig")
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        template_readme = (TESTER_PORTAL_TEMPLATE_ROOT / "README.md").read_text(encoding="utf-8-sig")
        package = json.loads((TESTER_PORTAL_TEMPLATE_ROOT / "package.json").read_text(encoding="utf-8-sig"))
        proof_path = TESTER_PORTAL_TEMPLATE_ROOT / "scripts" / "staging-local-link-proof.mjs"
        proof = proof_path.read_text(encoding="utf-8-sig")

        self.assertTrue(proof_path.is_file())
        self.assertEqual(
            package["scripts"]["proof:staging-local-link"],
            "node scripts/staging-local-link-proof.mjs",
        )

        for pattern in (
            "T10t Staging Local Link Configured",
            "GO_STAGING_LOCAL_LINK_CONFIGURED_NO_DEPLOY",
            "sqx-edge-tester-staging",
            "sqx-edge-tester-preview",
            "Updated the private working tree's ignored `.vercel/project.json`",
            "Verified `.vercel/` is ignored by git",
            "Deployment count: `0`.",
            "Domains count: `0`.",
            "Did not run `vercel deploy`.",
            "Did not call any deployment creation endpoint.",
            "Did not commit `.vercel/project.json`.",
            "T10u must prepare a no-deploy staging deployment readiness gate",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, t10t)

        for pattern in (
            'phase: "T10t"',
            'result: "GO_STAGING_LOCAL_LINK_CONFIGURED_NO_DEPLOY"',
            'projectName: "sqx-edge-tester-staging"',
            'projectId: "prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ"',
            'previousLocalProjectName: "sqx-edge-tester-preview"',
            'localPrivatePortalLinkedProjectName: "sqx-edge-tester-staging"',
            "privatePortalLocalLinkUpdated: true",
            "localVercelMetadataIgnored: true",
            "localProjectJsonCommitted: false",
            "gitProviderLinkedInT10t: false",
            "ssoProtectionEnabled: true",
            'ssoDeploymentType: "all_except_custom_domains"',
            "gitForkProtectionEnabled: true",
            "deploymentCount: 0",
            "domains: []",
            "domainsCount: 0",
            "externalDeployAttempted: false",
            "deploymentCreationEndpointCalled: false",
            "testerUrlPublished: false",
            "testerAccountsCreated: false",
            "testerEmailsCommitted: false",
            "productionDatabaseConnected: false",
            "T10u_no_deploy_staging_deployment_readiness_before_any_deployment",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, proof)
        self.assertNotIn("/v13/deployments", proof)
        self.assertNotIn("createDeployment", proof)
        self.assertNotIn("PATCH", proof)
        self.assertNotIn("fetch(", proof)

        for pattern in (
            "Current phase completed: T10t - Staging Local Link Configured.",
            "T10u - prepare a no-deploy staging deployment readiness gate before any deployment",
            "docs/T10T_STAGING_LOCAL_LINK_CONFIGURED.md",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "Current completed phase: T10t - Staging Local Link Configured.",
            "Phase T10t: link or configure staging without deployment and without publishing a URL. Done",
            "Phase T10u: prepare a no-deploy staging deployment readiness gate before any deployment.",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, next_steps)

        for pattern in (
            "T10t enlaza/configura localmente",
            "T10u para preparar un gate no-deploy de readiness",
            "T10t anade `proof:staging-local-link`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme)

        for pattern in (
            "T10t Staging Local Link Configured",
            "proof:staging-local-link",
            "GO_STAGING_LOCAL_LINK_CONFIGURED_NO_DEPLOY",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, changelog)

        for pattern in (
            "scripts/staging-local-link-proof.mjs",
            "npm run proof:staging-local-link",
            "GO_STAGING_LOCAL_LINK_CONFIGURED_NO_DEPLOY",
            "T10u must prepare a no-deploy staging deployment readiness gate",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, template_readme)

        combined_t10t_text = "\n".join([t10t, governance, next_steps, readme, changelog, template_readme, proof])
        for pattern in (
            "@gmail.com",
            "@hotmail.com",
            SENSITIVE_LITERAL_FORBIDDEN,
            "https://sqx-edge",
            ".vercel.app",
            "sk_live_",
            "pk_live_",
            "-----BEGIN PRIVATE KEY-----",
            "BEGIN RSA PRIVATE KEY",
        ):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, combined_t10t_text)

    def test_phase46_operational_visual_polish_is_present(self):
        css = (APP_ROOT / "css" / "dashboard.css").read_text(encoding="utf-8-sig")

        expected_patterns = [
            "Phase 46: operational visual polish",
            "--phase46-grid",
            ".pg-status-banner::after",
            ".pg-mining-row:nth-child(even)",
            "#pg-log",
            ".strat-summary-card::after",
            ".strat-card .sc-indicators",
            ".csv-preview-table tr:hover td",
            "@media (max-width: 980px)",
            "@media (max-width: 640px)",
        ]
        for pattern in expected_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, css)

    def test_public_commercial_docs_are_redacted_and_traceable(self):
        manifest = json.loads((PROJECT_ROOT / "docs" / "private_commercial_manifest.json").read_text(encoding="utf-8-sig"))
        pointer_index = (PROJECT_ROOT / "docs" / "PUBLIC_COMMERCIAL_POINTERS.md").read_text(encoding="utf-8-sig")
        private_repo = "https://github.com/CryptoLeon78/sqx-edge-commercial-private"
        private_commit = "ed79719"
        marker = "Public Redaction Pointer"
        allowed_redaction_phases = {
            "S5_public_commercial_redaction",
            "M71_next_controlled_buyer_outcome",
            "M72_controlled_distribution_step",
            "M73_controlled_distribution_review",
            "M74_next_buyer_facing_asset",
            "M75_private_asset_review",
            "M76_controlled_publication_gate",
            "M77_limited_publication_draft",
            "M78_operator_publication_review",
            "M79_manual_limited_publication_record",
            "M80_manual_publication_monitor",
            "M81_controlled_traffic_expansion_review",
            "M82_controlled_traffic_expansion_step",
            "M83_controlled_traffic_expansion_monitor",
            "M84_controlled_traffic_expansion_decision",
            "M85_controlled_traffic_expansion_execution",
            "M86_controlled_traffic_expansion_execution_monitor",
            "M87_controlled_commercial_next_movement",
            "M88_controlled_commercial_next_movement_execution",
            "M89_controlled_commercial_next_movement_execution_monitor",
            "M90_next_controlled_commercial_movement_decision",
            "M91_approved_controlled_commercial_movement_execution",
            "M92_approved_controlled_commercial_movement_execution_monitor",
            "M93_next_controlled_commercial_movement_from_m92_decision",
            "M94_approved_controlled_commercial_movement_from_m93_execution",
            "M95_approved_controlled_commercial_movement_from_m93_execution_monitor",
            "M96_next_controlled_commercial_movement_from_m95_decision",
            "M97_approved_controlled_commercial_movement_from_m96_decision_execution",
            "M98_approved_controlled_commercial_movement_from_m96_decision_execution_monitor",
            "M99_next_controlled_commercial_movement_from_m98_decision",
        }

        self.assertEqual(manifest["migrationStage"], "public_redacted_private_repo_published")
        self.assertEqual(manifest["phase"], "M99_next_controlled_commercial_movement_from_m98_decision")
        self.assertEqual(manifest["latestPrivateCommercialPhase"], "M99")
        self.assertEqual(manifest["privateRepositoryUrl"], private_repo)
        self.assertEqual(manifest["privateBaselineCommit"], private_commit)
        self.assertIn("public_repository_keeps_only_traceability_pointers", manifest["publicRedactionPolicy"])

        for pattern in (
            "docs/MONETIZATION_ROADMAP.md",
            "docs/MONETIZATION_M*.md",
            "docs/sales/",
            "resources/pro-buyer-pack/",
            "resources/pro-template-pack-1/",
            "resources/pro-template-pack-2/",
            private_repo,
            private_commit,
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, pointer_index)

        markdown_targets = [
            MONETIZATION_ROADMAP_DOC,
            *sorted((PROJECT_ROOT / "docs").glob("MONETIZATION_M*.md")),
            *sorted((PROJECT_ROOT / "docs" / "sales").glob("*.md")),
            *sorted((PROJECT_ROOT / "resources" / "pro-buyer-pack").rglob("*.md")),
            *sorted((PROJECT_ROOT / "resources" / "pro-template-pack-1").rglob("*.md")),
            *sorted((PROJECT_ROOT / "resources" / "pro-template-pack-2").rglob("*.md")),
        ]
        self.assertGreater(len(markdown_targets), 120)
        for path in markdown_targets:
            text = path.read_text(encoding="utf-8-sig")
            rel = path.relative_to(PROJECT_ROOT).as_posix()
            with self.subTest(path=rel):
                self.assertIn(marker, text)
                self.assertIn(f"Original path: {rel}", text)
                self.assertIn(private_repo, text)
                self.assertIn(private_commit, text)
                self.assertTrue(any(phase in text for phase in allowed_redaction_phases), text)

        for path in sorted((PROJECT_ROOT / "resources").glob("pro-*/**/*")):
            if not path.is_file() or path.suffix.lower() == ".md":
                continue
            text = path.read_text(encoding="utf-8-sig")
            rel = path.relative_to(PROJECT_ROOT).as_posix()
            with self.subTest(path=rel):
                lowered = text.lower()
                self.assertTrue("public_redaction" in lowered or "publicredaction" in lowered, text)
                self.assertIn(rel.lower(), lowered)
                self.assertIn(private_repo.lower(), lowered)
                self.assertIn(private_commit, text)
    def test_commercial_release_candidate_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "commercial_release_candidate.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "commercial_release_candidate_ready",
            "production_public_key_placeholder",
            "pilot_purchase_not_confirmed",
            "ZIP SHA256",
            "checkout_live_readiness_not_go",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_pilot_purchase_kit_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "pilot_purchase_kit.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "pilot_purchase_kit",
            "pilot_order_id_missing",
            "license_import_not_confirmed",
            "prepare_customer_delivery.ps1",
            "license_issue.py",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_limited_public_launch_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "limited_public_launch.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "limited_public_launch",
            "pilot_purchase_kit_not_go",
            "public_checkout_not_confirmed",
            "support_inbox_not_confirmed",
            "first_sale_cap_out_of_range",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_post_launch_control_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "post_launch_control.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "post_launch_control",
            "limited_public_launch_not_go",
            "no_paid_sales_recorded",
            "activations_below_paid_sales",
            "scale_public_not_supported_by_metrics",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_commercial_feedback_loop_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "commercial_feedback_loop.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "commercial_feedback_loop",
            "post_launch_control_not_go",
            "no_feedback_recorded",
            "pricing_objection_blocks_raise_price",
            "copy_confusion_blocks_keep_copy",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_public_offer_pack_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "public_offer_pack.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "public_offer_pack",
            "commercial_feedback_loop_not_go",
            "offer_headline_missing",
            "forbidden_claims_present",
            "buyer_steps_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_launch_assets_kit_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "launch_assets_kit.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "launch_assets_kit",
            "public_offer_pack_not_go",
            "github_release_draft_not_ready",
            "zip_sha256_not_confirmed",
            "publication_checklist_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_public_release_gate_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "public_release_gate.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "public_release_gate",
            "launch_assets_kit_not_go",
            "release_tag_missing",
            "sha256_not_published",
            "rollback_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_r45_controlled_publication_plan_tracks_verified_zip(self):
        text = R45_PUBLICATION_PLAN_DOC.read_text(encoding="utf-8-sig")
        for pattern in (
            "R45 - Controlled Publication Plan",
            "prepared_not_published",
            "SQX_Edge_Tool_Portable_20260508_201652.zip",
            "2725D2FC7CB9FD6E05AFDF1C7E20772B629BFBE8BE98532D4F5622A08628116E",
            "v0.2.0-r45",
            "public_release_gate.py",
            "release_publication_record.py",
            "No publication has been performed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_r47_controlled_commercial_release_tracks_verified_zip(self):
        text = R47_CONTROLLED_COMMERCIAL_RELEASE_DOC.read_text(encoding="utf-8-sig")
        for pattern in (
            "R47 - Controlled Commercial Release Candidate",
            "controlled_commercial_candidate_ready",
            "SQX_Edge_Tool_Portable_20260509_102131.zip",
            "18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D",
            "201 passed, 1 skipped",
            "No publication has been performed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_release_publication_record_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "release_publication_record.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "release_publication_record",
            "public_release_gate_not_go",
            "github_release_not_published",
            "sha256_mismatch",
            "rollback_window_not_open",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_post_release_monitor_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "post_release_monitor.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "post_release_monitor",
            "release_publication_record_not_go",
            "severe_incidents_open",
            "activation_error_rate_high",
            "rollback_not_available",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_hotfix_rollback_release_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "hotfix_rollback_release.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "hotfix_rollback_release",
            "post_release_monitor_not_go",
            "rollback_target_missing",
            "hotfix_notes_missing",
            "customer_comms_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_customer_success_renewal_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "customer_success_renewal.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "customer_success_renewal",
            "hotfix_rollback_release_not_go",
            "customer_reference_missing",
            "activation_not_confirmed",
            "support_tickets_open",
            "safe_claims_not_reviewed",
            "template_pack_offer_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_customer_cockpit_core_is_present_and_redacted(self):
        path = TOOL_ROOT / "core" / "customer_cockpit.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "customer_cockpit_ready",
            "redacted_operator_summary",
            "mask_email",
            "license payloads",
            "raw checkout events",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_pro_buyer_pack_resources_and_validator_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "pro_buyer_pack.py"
        config_path = TOOL_ROOT / "config" / "pro_buyer_pack.json"
        pack_root = PROJECT_ROOT / "resources" / "pro-buyer-pack"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "pro_buyer_pack_ready")
        self.assertTrue(config["includedInPortable"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for resource_path in pack_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "asset_universe_must_have_33_rows",
            "strategy_csv_missing_column",
            "forbidden_claim",
            "pro_buyer_pack_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_buyer_onboarding_support_gate_resources_and_validator_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "buyer_onboarding_support_gate.py"
        config_path = TOOL_ROOT / "config" / "buyer_onboarding_support_gate.json"
        onboarding_root = PROJECT_ROOT / "resources" / "pro-buyer-pack" / "onboarding"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "buyer_onboarding_support_gate_ready")
        self.assertTrue(config["includedInPortable"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for resource_path in onboarding_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "buyer_onboarding_support_gate_ready",
            "purchase_not_confirmed",
            "portable_zip_not_ready",
            "license_file_not_ready",
            "refund_or_pause_risk_unreviewed",
            "forbidden_claims_present",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_resources_and_packager_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_delivery.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1.json"
        pack_root = PROJECT_ROOT / "resources" / "pro-template-pack-1"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_delivery_ready")
        self.assertFalse(config["includedInPortable"])
        self.assertTrue(config["includedInAddOnDelivery"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        profiles = sorted((pack_root / "profiles").glob("*.json"))
        self.assertEqual(len(profiles), 3)
        for resource_path in pack_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "template_pack_1_delivery_ready",
            "buyer_onboarding_gate_not_go",
            "addon_order_not_confirmed",
            "pack_zip_not_ready",
            "template_pack_1_csv_missing_column",
            "forbidden_claims_present",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_offer_resources_and_gate_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_offer.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_offer.json"
        offer_root = PROJECT_ROOT / "resources" / "pro-template-pack-1" / "offer"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_public_offer_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertTrue(config["allowDraftCheckout"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for resource_path in offer_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "template_pack_1_public_offer_ready",
            "template_pack_delivery_not_ready",
            "checkout_draft_not_ready",
            "checkout_url_missing_or_not_https",
            "provider_variant_id_missing",
            "support_email_missing_or_invalid",
            "forbidden_claims_present",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_publication_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_publication.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_publication.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_live_checkout_gate_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["publicationMode"], "controlled_first_sales")
        self.assertEqual(config["firstSaleCap"], 5)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        self.assertEqual(config["env"]["checkoutUrl"], "SQX_TEMPLATE_PACK_1_CHECKOUT_URL")
        self.assertEqual(config["env"]["providerVariantId"], "SQX_TEMPLATE_PACK_1_PROVIDER_VARIANT_ID")
        self.assertEqual(config["env"]["supportEmail"], "SQX_TEMPLATE_PACK_1_SUPPORT_EMAIL")

        for pattern in (
            "checkout_url_missing_or_not_https",
            "checkout_url_looks_placeholder",
            "provider_variant_id_missing",
            "support_email_missing_or_invalid",
            "_not_confirmed",
            "template_pack_1_controlled_publication_live",
            "apply_publication_values",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_purchase_drill_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_purchase_drill.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_purchase_drill.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_purchase_drill_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["amount"], "49.00")
        self.assertEqual(config["currency"], "EUR")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_email_and_order_reference_only")
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "redact_email",
            "checkout_url_missing_or_not_https",
            "provider_order_id_missing",
            "payment_status_not_paid",
            "delivery_package_missing_entry",
            "delivery_package_content_not_verified",
            "buyer_email_redacted",
            "--require-delivery-package",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_handoff_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_handoff.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_handoff.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_handoff_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_reference_handoff_notes_and_scale_decision_only")
        self.assertIn("scale_limited", config["allowedDecisions"])
        self.assertIn("hold_review", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_purchase_drill_file",
            "buyer_email_redacted",
            "template_pack_1_purchase_drill_evidence_missing",
            "support_first_response_sla_missed",
            "scale_limited_not_supported_by_handoff",
            "refund_risk_requires_pause_sales",
            "--use-latest-purchase-drill",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_sales_register_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_sales_register.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_sales_register.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_sales_register_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_reference_order_status_support_metrics_and_scale_decision_only")
        self.assertIn("keep_tracking", config["allowedDecisions"])
        self.assertIn("scale_limited", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_handoff_file",
            "buyer_email_redacted",
            "template_pack_1_handoff_evidence_missing",
            "open_support_items_require_pause_or_review",
            "scale_limited_not_supported_by_register",
            "register_record",
            "--append-register",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_feedback_cohort_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_feedback_cohort.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_feedback_cohort.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_feedback_cohort_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["privacyPolicy"], "store_redacted_cohort_metrics_feedback_themes_support_counts_and_roadmap_decision_only")
        self.assertIn("expand_traffic", config["allowedDecisions"])
        self.assertIn("iterate_offer", config["allowedDecisions"])
        self.assertIn("build_template_pack_2", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_sales_register_file",
            "template_pack_1_sales_register_evidence_missing",
            "expand_traffic_needs_minimum_buyers",
            "open_support_blocks_expansion",
            "template_pack_2_needs_positive_signals",
            "--use-latest-sales-register",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_action_plan_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_action_plan.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_action_plan.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_action_plan_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["privacyPolicy"], "store_redacted_action_plan_owner_priority_support_claims_distribution_and_next_phase_only")
        self.assertIn("offer_iteration", config["allowedPlans"])
        self.assertIn("traffic_expansion", config["allowedPlans"])
        self.assertIn("template_pack_2", config["allowedPlans"])
        self.assertIn("pause_sales", config["allowedPlans"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_feedback_cohort_file",
            "template_pack_1_feedback_cohort_evidence_missing",
            "traffic_expansion_support_impact_too_high",
            "template_pack_2_next_phase_mismatch",
            "feedback_recommended_",
            "--use-latest-feedback-cohort",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_specs_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_specs.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_specs.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_specs_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["privacyPolicy"], "store_redacted_pack_2_scope_assets_support_delivery_and_next_phase_only")
        self.assertIn("draft_pack_2_assets", config["allowedSpecDecisions"])
        self.assertIn("iterate_pack_1_first", config["allowedSpecDecisions"])
        self.assertIn("pause_pack_2", config["allowedSpecDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_action_plan_file",
            "template_pack_1_action_plan_evidence_missing",
            "template_pack_1_action_plan_not_template_pack_2",
            "draft_pack_2_assets_needs_asset_families",
            "draft_pack_2_assets_next_phase_mismatch",
            "--use-latest-action-plan",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_assets_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_assets.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_assets.json"
        resource_dir = PROJECT_ROOT / "resources" / "pro-template-pack-2"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_assets_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["resourceDir"], "resources/pro-template-pack-2")
        self.assertFalse(config["includedInPortable"])
        self.assertTrue(config["includedInAddOnDelivery"])
        self.assertEqual(config["minimumPresetRows"], 8)
        self.assertEqual(config["dependsOn"]["requiredSpecDecision"], "draft_pack_2_assets")
        self.assertEqual(config["dependsOn"]["requiredNextPhase"], "M58_template_pack_2_assets")
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        profiles = sorted((resource_dir / "profiles").glob("*.json"))
        self.assertGreaterEqual(len(profiles), 3)
        for resource_path in resource_dir.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)

        for pattern in (
            "latest_specs_file",
            "template_pack_2_specs_evidence_missing",
            "template_pack_2_specs_decision_invalid",
            "template_pack_2_csv_needs_eight_rows",
            "template_pack_2_csv_needs_asset_families",
            "--use-latest-specs",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_offer_pack_resources_and_gate_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_offer_pack.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_offer_pack.json"
        offer_root = PROJECT_ROOT / "resources" / "pro-template-pack-2" / "offer"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_offer_pack_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["price"], "79 EUR")
        self.assertTrue(config["allowDraftCheckout"])
        self.assertEqual(config["dependsOn"]["templatePack2AssetsState"], "template_pack_2_assets_ready")
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for resource_path in offer_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "template_pack_2_offer_pack_ready",
            "template_pack_2_assets_state_invalid",
            "template_pack_2_variant_missing",
            "checkout_url_missing_or_not_https",
            "--confirm-template-pack-2-assets-ready",
            "--require-live-checkout",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_publication_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_publication.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_publication.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_controlled_publication_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["price"], "79 EUR")
        self.assertEqual(config["dependsOn"]["offerPackState"], "template_pack_2_offer_pack_ready")
        self.assertEqual(config["dependsOn"]["assetsState"], "template_pack_2_assets_ready")
        self.assertEqual(config["env"]["checkoutUrl"], "SQX_TEMPLATE_PACK_2_CHECKOUT_URL")
        self.assertIn("purchaseDrillChecklist", config)
        self.assertGreaterEqual(len(config["purchaseDrillChecklist"]), 4)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_controlled_publication_ready",
            "template_pack_2_offer_pack_state_invalid",
            "template_pack_2_assets_state_invalid",
            "checkout_url_missing_or_not_https",
            "provider_variant_id_looks_placeholder",
            "templatePack2LiveCheckout",
            "--confirm-purchase-drill-ready",
            "--apply",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_purchase_drill_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_purchase_drill.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_purchase_drill.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_purchase_drill_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["price"], "79 EUR")
        self.assertEqual(config["amount"], "79.00")
        self.assertEqual(config["currency"], "EUR")
        self.assertEqual(config["dependsOn"]["publicationState"], "template_pack_2_controlled_publication_ready")
        self.assertEqual(config["dependsOn"]["assetsState"], "template_pack_2_assets_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_email_and_order_reference_only")
        self.assertIn("paid", config["allowedPaymentStatuses"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_purchase_drill_ready",
            "template_pack_2_publication_state_invalid",
            "template_pack_2_assets_state_invalid",
            "checkout_url_missing_or_not_https",
            "buyer_email_missing_or_invalid",
            "delivery_package_missing_entry",
            "buyer_email_redacted",
            "--require-delivery-package",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_handoff_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_handoff.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_handoff.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_handoff_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["dependsOn"]["purchaseDrillState"], "template_pack_2_purchase_drill_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_reference_handoff_notes_and_scale_decision_only")
        self.assertIn("scale_limited", config["allowedDecisions"])
        self.assertIn("hold_review", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_handoff_ready",
            "template_pack_2_purchase_drill_state_invalid",
            "template_pack_2_purchase_drill_evidence_missing",
            "buyer_reference_missing_or_invalid",
            "support_first_response_sla_missed",
            "refund_risk_requires_pause_sales",
            "scale_limited_needs_buyer_acknowledgement_and_first_value",
            "buyer_email_redacted",
            "--use-latest-purchase-drill",
            "--scale-decision",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_sales_register_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_sales_register.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_sales_register.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_sales_register_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["dependsOn"]["handoffState"], "template_pack_2_handoff_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_reference_order_status_support_metrics_and_scale_decision_only")
        self.assertIn("keep_tracking", config["allowedDecisions"])
        self.assertIn("scale_limited", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_sales_register_ready",
            "template_pack_2_handoff_state_invalid",
            "template_pack_2_handoff_evidence_missing",
            "buyer_reference_missing_or_invalid",
            "non_paid_sale_requires_pause_sales",
            "delivery_not_confirmed_requires_pause_sales",
            "scale_limited_needs_minimum_sales",
            "template_pack_2_sales_register.jsonl",
            "--append-register",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_feedback_cohort_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_feedback_cohort.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_feedback_cohort.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_feedback_cohort_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["dependsOn"]["salesRegisterState"], "template_pack_2_sales_register_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_cohort_metrics_feedback_themes_support_counts_and_roadmap_decision_only")
        self.assertIn("expand_traffic", config["allowedDecisions"])
        self.assertIn("iterate_offer", config["allowedDecisions"])
        self.assertIn("prepare_pack_3", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_feedback_cohort_ready",
            "template_pack_2_sales_register_state_invalid",
            "template_pack_2_sales_register_evidence_missing",
            "feedback_cohort_metrics_invalid",
            "expand_traffic_needs_minimum_buyers",
            "pack_3_needs_positive_signals",
            "--use-latest-sales-register",
            "--roadmap-decision",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_buyer_ready_checkout_closeout_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "buyer_ready_checkout_closeout.py"
        config_path = TOOL_ROOT / "config" / "buyer_ready_checkout_closeout.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "buyer_ready_checkout_release_closeout_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_and_template_pack_2")
        self.assertEqual(config["dependsOn"]["feedbackCohortState"], "template_pack_2_feedback_cohort_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_checkout_release_support_and_delivery_readiness_only")
        self.assertIn("open_controlled_sales", config["allowedDecisions"])
        self.assertIn("keep_private_pilot", config["allowedDecisions"])
        self.assertIn("iterate_buyer_pack", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "buyer_ready_checkout_release_closeout_ready",
            "template_pack_2_feedback_cohort_state_invalid",
            "template_pack_2_feedback_cohort_evidence_missing",
            "buyer_steps_incomplete",
            "support_label_missing_or_unsafe",
            "open_sales_needs_positive_feedback_decision",
            "--use-latest-feedback-cohort",
            "--confirm-license-delivery-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_public_buyer_page_cadence_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "public_buyer_page_cadence.py"
        config_path = TOOL_ROOT / "config" / "public_buyer_page_cadence.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "public_buyer_page_cadence_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_public_buyer_page")
        self.assertEqual(config["dependsOn"]["buyerReadyCloseoutState"], "buyer_ready_checkout_release_closeout_ready")
        self.assertEqual(config["privacyPolicy"], "store_public_page_checklist_and_first_sale_cadence_without_customer_data")
        self.assertIn("publish_private_page", config["allowedDecisions"])
        self.assertIn("keep_draft", config["allowedDecisions"])
        self.assertIn("revise_copy", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "public_buyer_page_cadence_ready",
            "buyer_ready_checkout_closeout_state_invalid",
            "buyer_ready_checkout_closeout_evidence_missing",
            "public_page_sections_incomplete",
            "first_sale_cadence_incomplete",
            "publish_private_page_needs_private_link_ready",
            "--use-latest-buyer-ready-closeout",
            "--confirm-first-sale-cadence-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_first_controlled_buyer_log_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "first_controlled_buyer_log.py"
        config_path = TOOL_ROOT / "config" / "first_controlled_buyer_log.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "first_controlled_buyer_log_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_first_controlled_buyer")
        self.assertEqual(config["dependsOn"]["publicBuyerPageCadenceState"], "public_buyer_page_cadence_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_first_buyer_order_activation_support_feedback_and_decision_only")
        self.assertIn("continue_private_sales", config["allowedDecisions"])
        self.assertIn("iterate_onboarding", config["allowedDecisions"])
        self.assertIn("schedule_followup", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "first_controlled_buyer_log_ready",
            "public_buyer_page_cadence_state_invalid",
            "public_buyer_page_cadence_evidence_missing",
            "order_ref_missing_or_unsafe",
            "continue_private_sales_needs_first_value_confirmed",
            "fulfillment_failures_require_pause_sales",
            "--use-latest-public-page-cadence",
            "--confirm-license-activation-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_post_sale_improvement_loop_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "post_sale_improvement_loop.py"
        config_path = TOOL_ROOT / "config" / "post_sale_improvement_loop.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "post_sale_improvement_loop_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_post_sale_improvement")
        self.assertEqual(config["dependsOn"]["firstControlledBuyerLogState"], "first_controlled_buyer_log_ready")
        self.assertEqual(config["privacyPolicy"], "store_aggregated_post_sale_improvement_actions_without_personal_data_or_raw_buyer_messages")
        self.assertIn("ship_micro_updates", config["allowedDecisions"])
        self.assertIn("revise_onboarding", config["allowedDecisions"])
        self.assertIn("revise_support_macros", config["allowedDecisions"])
        self.assertIn("revise_public_copy", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "post_sale_improvement_loop_ready",
            "first_controlled_buyer_log_state_invalid",
            "first_controlled_buyer_log_evidence_missing",
            "post_sale_improvement_needs_minimum_updates",
            "ship_micro_updates_blocked_by_support_risk",
            "claims_risk_requires_pause_sales",
            "--use-latest-first-buyer-log",
            "--confirm-support-macros-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_post_sale_micro_updates_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "post_sale_micro_updates.py"
        config_path = TOOL_ROOT / "config" / "post_sale_micro_updates.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "post_sale_micro_updates_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_buyer")
        self.assertEqual(config["dependsOn"]["postSaleImprovementLoopState"], "post_sale_improvement_loop_ready")
        self.assertEqual(config["privacyPolicy"], "store_applied_micro_update_counts_and_next_buyer_readiness_without_personal_data")
        self.assertIn("next_controlled_buyer_ready", config["allowedDecisions"])
        self.assertIn("revise_more", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for rel_path, markers in config["requiredMarkers"].items():
            path = PROJECT_ROOT / rel_path
            text = path.read_text(encoding="utf-8-sig")
            lowered = text.lower()
            if "public redaction" in lowered or "public_redaction" in lowered or "publicredaction" in lowered:
                with self.subTest(required_marker_source=rel_path):
                    self.assert_public_redaction_pointer(path)
                continue
            for marker in markers:
                with self.subTest(marker=marker):
                    self.assertIn(marker, text)

        for pattern in (
            "post_sale_micro_updates_ready",
            "post_sale_improvement_loop_state_invalid",
            "post_sale_improvement_loop_evidence_missing",
            "missing_marker",
            "post_sale_micro_updates_need_minimum_applied_updates",
            "next_buyer_readiness_steps_incomplete",
            "claims_risk_requires_pause_sales",
            "--use-latest-improvement-loop",
            "--confirm-next-buyer-check-recorded",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_controlled_buyer_readiness_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_controlled_buyer_readiness.py"
        config_path = TOOL_ROOT / "config" / "next_controlled_buyer_readiness.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_controlled_buyer_readiness_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_private_buyer")
        self.assertEqual(config["dependsOn"]["postSaleMicroUpdatesState"], "post_sale_micro_updates_ready")
        self.assertEqual(config["privacyPolicy"], "store_next_buyer_readiness_counts_and_decision_without_personal_data_or_checkout_payloads")
        self.assertIn("share_private_link", config["allowedDecisions"])
        self.assertIn("hold_for_fix", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "next_controlled_buyer_readiness_ready",
            "post_sale_micro_updates_state_invalid",
            "post_sale_micro_updates_evidence_missing",
            "share_private_link_requires_ready_private_link",
            "share_private_link_requires_single_buyer_slot",
            "claims_risk_requires_pause_sales",
            "--use-latest-micro-updates",
            "--confirm-followup-window-recorded",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_controlled_buyer_outcome_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_controlled_buyer_outcome.py"
        config_path = TOOL_ROOT / "config" / "next_controlled_buyer_outcome.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "NEXT_CONTROLLED_BUYER_OUTCOME.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_controlled_buyer_outcome_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_private_buyer")
        self.assertEqual(config["dependsOn"]["nextControlledBuyerReadinessState"], "next_controlled_buyer_readiness_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_redacted_next_buyer_outcome_metrics_decision_and_actions_without_personal_data_checkout_payloads_or_license_files",
        )
        self.assertIn("repeat_private_slot", config["allowedDecisions"])
        self.assertIn("carefully_widen", config["allowedDecisions"])
        self.assertIn("hold_for_fix", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)

        for pattern in (
            "next_controlled_buyer_outcome_ready",
            "next_controlled_buyer_readiness_state_invalid",
            "next_controlled_buyer_readiness_evidence_missing",
            "carefully_widen_requires_completed_outcome",
            "repeat_private_slot_blocked_by_risk",
            "failed_or_refunded_outcome_requires_pause_sales",
            "--use-latest-readiness",
            "--confirm-next-decision-recorded",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_distribution_step_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_distribution_step.py"
        config_path = TOOL_ROOT / "config" / "controlled_distribution_step.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_DISTRIBUTION_STEP.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_distribution_step_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_distribution_step")
        self.assertEqual(config["dependsOn"]["nextControlledBuyerOutcomeState"], "next_controlled_buyer_outcome_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_distribution_action_metrics_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("repeat_private_slot", config["allowedSourceDecisions"])
        self.assertIn("carefully_widen", config["allowedSourceDecisions"])
        self.assertIn("hold_for_fix", config["allowedSourceDecisions"])
        self.assertIn("pause_sales", config["allowedSourceDecisions"])
        self.assertIn("prepare_single_private_slot", config["allowedActions"])
        self.assertIn("open_tiny_private_batch", config["allowedActions"])
        self.assertEqual(config["maximumTinyBatchSlots"], 3)
        self.assertEqual(config["maximumTinyAudienceInvites"], 5)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M72_DOC)

        for pattern in (
            "controlled_distribution_step_ready",
            "next_controlled_buyer_outcome_state_invalid",
            "next_controlled_buyer_outcome_evidence_missing",
            "controlled_distribution_action_mismatch",
            "carefully_widen_slot_limit_invalid",
            "pause_sales_requires_disabled_checkout",
            "--use-latest-outcome",
            "--confirm-selected-decision-matched",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_distribution_review_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_distribution_review.py"
        config_path = TOOL_ROOT / "config" / "controlled_distribution_review.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_DISTRIBUTION_REVIEW.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_distribution_review_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_distribution_review")
        self.assertEqual(config["dependsOn"]["controlledDistributionStepState"], "controlled_distribution_step_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_distribution_review_metrics_decision_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_single_private_slot", config["allowedSourceActions"])
        self.assertIn("open_tiny_private_batch", config["allowedSourceActions"])
        self.assertIn("prepare_buyer_facing_asset", config["allowedDecisions"])
        self.assertIn("repeat_distribution_step", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        self.assertEqual(config["minimumPositiveSignalsForAsset"], 2)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M73_DOC)

        for pattern in (
            "controlled_distribution_review_ready",
            "controlled_distribution_step_state_invalid",
            "controlled_distribution_step_evidence_missing",
            "controlled_distribution_review_source_action_not_m72_action",
            "prepare_buyer_facing_asset_requires_positive_signals",
            "paused_distribution_requires_pause_sales",
            "--use-latest-distribution",
            "--confirm-next-decision-recorded",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_buyer_facing_asset_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_buyer_facing_asset.py"
        config_path = TOOL_ROOT / "config" / "next_buyer_facing_asset.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "NEXT_BUYER_FACING_ASSET.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_buyer_facing_asset_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_buyer_facing_asset")
        self.assertEqual(config["dependsOn"]["controlledDistributionReviewState"], "controlled_distribution_review_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_asset_scope_status_decision_and_review_metadata_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_buyer_facing_asset", config["allowedReviewDecisions"])
        self.assertIn("public_offer_section", config["allowedAssetTypes"])
        self.assertIn("ready_private_review", config["allowedAssetStatuses"])
        self.assertIn("prepare_private_review", config["allowedDecisions"])
        self.assertEqual(config["maximumAssetScopeItems"], 5)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M74_DOC)

        for pattern in (
            "next_buyer_facing_asset_ready",
            "controlled_distribution_review_state_invalid",
            "controlled_distribution_review_evidence_missing",
            "m73_did_not_select_prepare_buyer_facing_asset",
            "prepare_private_review_requires_safe_claims",
            "blocked_asset_requires_hold_or_pause",
            "--use-latest-review",
            "--confirm-private-review-owner",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_private_asset_review_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "private_asset_review.py"
        config_path = TOOL_ROOT / "config" / "private_asset_review.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "PRIVATE_ASSET_REVIEW.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "private_asset_review_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_private_asset_review")
        self.assertEqual(config["dependsOn"]["nextBuyerFacingAssetState"], "next_buyer_facing_asset_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_private_review_status_decision_and_risk_counts_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_private_review", config["allowedSourceDecisions"])
        self.assertIn("approved_private", config["allowedReviewStatuses"])
        self.assertIn("prepare_controlled_publication", config["allowedDecisions"])
        self.assertEqual(config["minimumReviewers"], 1)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M75_DOC)

        for pattern in (
            "private_asset_review_ready",
            "next_buyer_facing_asset_state_invalid",
            "next_buyer_facing_asset_evidence_missing",
            "m74_did_not_select_prepare_private_review",
            "prepare_controlled_publication_requires_safe_claims",
            "blocked_asset_review_requires_hold_or_pause",
            "--use-latest-asset",
            "--confirm-rollback-ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_publication_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_publication_gate.py"
        config_path = TOOL_ROOT / "config" / "controlled_publication_gate.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_PUBLICATION_GATE.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_publication_gate_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_publication_gate")
        self.assertEqual(config["dependsOn"]["privateAssetReviewState"], "private_asset_review_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_publication_channel_cap_decision_owner_and_risk_counts_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_controlled_publication", config["allowedSourceDecisions"])
        self.assertIn("private_link", config["allowedChannels"])
        self.assertIn("prepare_limited_publication", config["allowedDecisions"])
        self.assertEqual(config["maximumAudienceCap"], 10)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M76_DOC)

        for pattern in (
            "controlled_publication_gate_ready",
            "private_asset_review_state_invalid",
            "private_asset_review_evidence_missing",
            "m75_did_not_select_prepare_controlled_publication",
            "prepare_limited_publication_requires_pause_rule",
            "open_risks_block_limited_publication",
            "--use-latest-review",
            "--confirm-pause-rule-ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_limited_publication_draft_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "limited_publication_draft.py"
        config_path = TOOL_ROOT / "config" / "limited_publication_draft.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "LIMITED_PUBLICATION_DRAFT.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "limited_publication_draft_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_limited_publication_draft")
        self.assertEqual(config["dependsOn"]["controlledPublicationGateState"], "controlled_publication_gate_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_publication_draft_metadata_copy_checks_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_limited_publication", config["allowedSourceDecisions"])
        self.assertIn("private_link", config["allowedDraftChannels"])
        self.assertIn("ready_for_operator_review", config["allowedDecisions"])
        self.assertEqual(config["maximumAudienceCap"], 10)
        self.assertIn("rentabilidad asegurada", config["blockedClaimPatterns"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M77_DOC)

        for pattern in (
            "limited_publication_draft_ready",
            "controlled_publication_gate_state_invalid",
            "controlled_publication_gate_evidence_missing",
            "m76_did_not_select_prepare_limited_publication",
            "ready_for_operator_review_requires_basic_user_instructions",
            "blocked_claims_block_operator_review",
            "--use-latest-gate",
            "--confirm-safe-copy",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_operator_publication_review_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "operator_publication_review.py"
        config_path = TOOL_ROOT / "config" / "operator_publication_review.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "OPERATOR_PUBLICATION_REVIEW.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "operator_publication_review_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_operator_publication_review")
        self.assertEqual(config["dependsOn"]["limitedPublicationDraftState"], "limited_publication_draft_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_operator_review_status_decision_owner_and_risk_counts_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("ready_for_operator_review", config["allowedSourceDecisions"])
        self.assertIn("approved_manual_review", config["allowedReviewStatuses"])
        self.assertIn("approve_manual_limited_publication", config["allowedDecisions"])
        self.assertEqual(config["minimumReviewers"], 1)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M78_DOC)

        for pattern in (
            "operator_publication_review_ready",
            "limited_publication_draft_state_invalid",
            "limited_publication_draft_evidence_missing",
            "m77_did_not_select_ready_for_operator_review",
            "approve_manual_limited_publication_requires_basic_user_flow",
            "blocked_operator_review_requires_hold_or_pause",
            "--use-latest-draft",
            "--confirm-draft-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_manual_limited_publication_record_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "manual_limited_publication_record.py"
        config_path = TOOL_ROOT / "config" / "manual_limited_publication_record.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "MANUAL_LIMITED_PUBLICATION_RECORD.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "manual_limited_publication_record_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_manual_limited_publication_record")
        self.assertEqual(config["dependsOn"]["operatorPublicationReviewState"], "operator_publication_review_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_manual_publication_channel_url_owner_time_audience_counts_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("approve_manual_limited_publication", config["allowedSourceDecisions"])
        self.assertIn("private_link", config["allowedChannels"])
        self.assertIn("record_manual_publication", config["allowedDecisions"])
        self.assertEqual(config["maximumAudienceCap"], 10)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M79_DOC)

        for pattern in (
            "manual_limited_publication_record_ready",
            "operator_publication_review_state_invalid",
            "operator_publication_review_evidence_missing",
            "m78_did_not_select_approve_manual_limited_publication",
            "manual_limited_publication_redacted_url_missing_or_unsafe",
            "record_manual_publication_requires_monitoring",
            "--use-latest-review",
            "--confirm-redacted-url",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_manual_publication_monitor_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "manual_publication_monitor.py"
        config_path = TOOL_ROOT / "config" / "manual_publication_monitor.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "MANUAL_PUBLICATION_MONITOR.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "manual_publication_monitor_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_manual_publication_monitor")
        self.assertEqual(config["dependsOn"]["manualLimitedPublicationRecordState"], "manual_limited_publication_record_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_monitoring_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("record_manual_publication", config["allowedSourceDecisions"])
        self.assertIn("prepare_traffic_expansion_review", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M80_DOC)

        for pattern in (
            "manual_publication_monitor_ready",
            "manual_limited_publication_record_state_invalid",
            "manual_limited_publication_record_evidence_missing",
            "m79_did_not_select_record_manual_publication",
            "prepare_traffic_expansion_review_requires_observation_time",
            "risky_counts_block_traffic_expansion_review",
            "--use-latest-record",
            "--confirm-redacted-metrics",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_traffic_expansion_review_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_traffic_expansion_review.py"
        config_path = TOOL_ROOT / "config" / "controlled_traffic_expansion_review.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_TRAFFIC_EXPANSION_REVIEW.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_traffic_expansion_review_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_traffic_expansion_review")
        self.assertEqual(config["dependsOn"]["manualPublicationMonitorState"], "manual_publication_monitor_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_monitoring_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertEqual(
            config["reviewPolicy"],
            "approve_only_tiny_controlled_traffic_expansion_after_m80_monitoring_support_claims_refunds_incidents_rollback_and_pause_rule_are_clean",
        )
        self.assertIn("prepare_traffic_expansion_review", config["allowedSourceDecisions"])
        self.assertIn("approve_tiny_traffic_expansion", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["maximumIncidents"], 0)
        self.assertEqual(config["minimumPositiveSignalsForTinyExpansion"], 1)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M81_DOC)

        for pattern in (
            "controlled_traffic_expansion_review_ready",
            "manual_publication_monitor_state_invalid",
            "manual_publication_monitor_evidence_missing",
            "m80_did_not_select_prepare_traffic_expansion_review",
            "approve_tiny_traffic_expansion_requires_observation_time",
            "risky_counts_block_tiny_traffic_expansion",
            "--use-latest-record",
            "--confirm-redacted-metrics",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_traffic_expansion_step_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_traffic_expansion_step.py"
        config_path = TOOL_ROOT / "config" / "controlled_traffic_expansion_step.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_TRAFFIC_EXPANSION_STEP.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_traffic_expansion_step_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_traffic_expansion_step")
        self.assertEqual(config["dependsOn"]["controlledTrafficExpansionReviewState"], "controlled_traffic_expansion_review_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_tiny_traffic_action_counts_channel_owner_and_next_review_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("approve_tiny_traffic_expansion", config["allowedSourceDecisions"])
        self.assertIn("share_one_private_link", config["allowedActions"])
        self.assertIn("invite_tiny_watchlist", config["allowedActions"])
        self.assertEqual(config["maximumChannels"], 1)
        self.assertEqual(config["maximumPrivateLinks"], 1)
        self.assertEqual(config["maximumAudienceInvites"], 3)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M82_DOC)

        for pattern in (
            "controlled_traffic_expansion_step_ready",
            "controlled_traffic_expansion_review_state_invalid",
            "controlled_traffic_expansion_review_evidence_missing",
            "controlled_traffic_expansion_step_action_mismatch",
            "tiny_traffic_step_invite_limit_invalid",
            "share_one_private_link_requires_one_link_and_one_invite_max",
            "--use-latest-review",
            "--confirm-safe-claims-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_traffic_expansion_monitor_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_traffic_expansion_monitor.py"
        config_path = TOOL_ROOT / "config" / "controlled_traffic_expansion_monitor.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_TRAFFIC_EXPANSION_MONITOR.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_traffic_expansion_monitor_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_traffic_expansion_monitor")
        self.assertEqual(config["dependsOn"]["controlledTrafficExpansionStepState"], "controlled_traffic_expansion_step_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_monitor_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("share_one_private_link", config["allowedSourceActions"])
        self.assertIn("invite_tiny_watchlist", config["allowedSourceActions"])
        self.assertIn("repeat_tiny_step", config["allowedDecisions"])
        self.assertIn("prepare_next_private_review", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForRepeat"], 1)
        self.assertEqual(config["minimumPositiveSignalsForReview"], 2)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M83_DOC)

        for pattern in (
            "controlled_traffic_expansion_monitor_ready",
            "controlled_traffic_expansion_step_state_invalid",
            "controlled_traffic_expansion_step_evidence_missing",
            "controlled_traffic_expansion_monitor_source_action_not_m82_action",
            "repeat_tiny_step_requires_positive_signal",
            "prepare_next_private_review_requires_positive_signals",
            "--use-latest-step",
            "--confirm-redacted-metrics",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_traffic_expansion_decision_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_traffic_expansion_decision.py"
        config_path = TOOL_ROOT / "config" / "controlled_traffic_expansion_decision.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_TRAFFIC_EXPANSION_DECISION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_traffic_expansion_decision_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_traffic_expansion_decision")
        self.assertEqual(config["dependsOn"]["controlledTrafficExpansionMonitorState"], "controlled_traffic_expansion_monitor_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_decision_source_counts_owner_rationale_and_next_check_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("repeat_tiny_step", config["allowedSourceMonitorDecisions"])
        self.assertIn("prepare_next_private_review", config["allowedSourceMonitorDecisions"])
        self.assertIn("repeat_same_tiny_step", config["allowedFinalActions"])
        self.assertIn("prepare_private_review_packet", config["allowedFinalActions"])
        self.assertIn("continue_observation", config["allowedFinalActions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M84_DOC)

        for pattern in (
            "controlled_traffic_expansion_decision_ready",
            "controlled_traffic_expansion_monitor_state_invalid",
            "controlled_traffic_expansion_monitor_evidence_missing",
            "controlled_traffic_expansion_decision_source_not_m83_decision",
            "repeat_same_tiny_step_requires_m83_repeat_decision",
            "prepare_private_review_packet_requires_m83_review_decision",
            "--use-latest-monitor",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_traffic_expansion_execution_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_traffic_expansion_execution.py"
        config_path = TOOL_ROOT / "config" / "controlled_traffic_expansion_execution.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_TRAFFIC_EXPANSION_EXECUTION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_traffic_expansion_execution_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_traffic_expansion_execution")
        self.assertEqual(config["dependsOn"]["controlledTrafficExpansionDecisionState"], "controlled_traffic_expansion_decision_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_execution_result_owner_summary_and_next_monitor_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("repeat_same_tiny_step", config["allowedSourceFinalActions"])
        self.assertIn("prepare_private_review_packet", config["allowedSourceFinalActions"])
        self.assertIn("repeat_step_recorded", config["allowedExecutionResults"])
        self.assertIn("private_review_packet_prepared", config["allowedExecutionResults"])
        self.assertEqual(config["requiredResultByAction"]["repeat_same_tiny_step"], "repeat_step_recorded")
        self.assertEqual(config["maximumNewPrivateLinks"], 1)
        self.assertEqual(config["maximumNewInvites"], 3)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M85_DOC)

        for pattern in (
            "controlled_traffic_expansion_execution_ready",
            "controlled_traffic_expansion_decision_state_invalid",
            "controlled_traffic_expansion_decision_evidence_missing",
            "controlled_traffic_expansion_execution_source_not_m84_action",
            "controlled_traffic_expansion_execution_result_not_allowed_for_m84_action",
            "repeat_step_recorded_private_link_limit_exceeded",
            "--use-latest-decision",
            "--confirm-exact-action",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_traffic_expansion_execution_monitor_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_traffic_expansion_execution_monitor.py"
        config_path = TOOL_ROOT / "config" / "controlled_traffic_expansion_execution_monitor.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_TRAFFIC_EXPANSION_EXECUTION_MONITOR.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_traffic_expansion_execution_monitor_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_traffic_expansion_execution_monitor")
        self.assertEqual(config["dependsOn"]["controlledTrafficExpansionExecutionState"], "controlled_traffic_expansion_execution_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_execution_monitor_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("repeat_step_recorded", config["allowedSourceExecutionResults"])
        self.assertIn("private_review_packet_prepared", config["allowedSourceExecutionResults"])
        self.assertIn("prepare_new_decision", config["allowedDecisions"])
        self.assertIn("continue_observation", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForNewDecision"], 1)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M86_DOC)

        for pattern in (
            "controlled_traffic_expansion_execution_monitor_ready",
            "controlled_traffic_expansion_execution_state_invalid",
            "controlled_traffic_expansion_execution_evidence_missing",
            "controlled_traffic_expansion_execution_monitor_source_not_m85_result",
            "prepare_new_decision_requires_positive_signal",
            "prepare_new_decision_blocked_after_hold_or_pause",
            "--use-latest-execution",
            "--confirm-redacted-metrics",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_commercial_next_movement_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_commercial_next_movement.py"
        config_path = TOOL_ROOT / "config" / "controlled_commercial_next_movement.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_COMMERCIAL_NEXT_MOVEMENT.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_commercial_next_movement_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_commercial_next_movement")
        self.assertEqual(
            config["dependsOn"]["controlledTrafficExpansionExecutionMonitorState"],
            "controlled_traffic_expansion_execution_monitor_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_next_movement_decision_counts_owner_rationale_and_next_gate_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_new_decision", config["allowedSourceMonitorDecisions"])
        self.assertIn("prepare_next_micro_step", config["allowedNextMovements"])
        self.assertIn("prepare_private_review_packet", config["allowedNextMovements"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForMovement"], 1)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M87_DOC)

        for pattern in (
            "controlled_commercial_next_movement_ready",
            "controlled_traffic_expansion_execution_monitor_state_invalid",
            "controlled_traffic_expansion_execution_monitor_evidence_missing",
            "controlled_commercial_next_movement_source_not_m86_decision",
            "prepare_next_micro_step_requires_m86_prepare_new_decision",
            "prepare_private_review_packet_requires_completed_monitor",
            "--use-latest-monitor",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_commercial_next_movement_execution_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_commercial_next_movement_execution.py"
        config_path = TOOL_ROOT / "config" / "controlled_commercial_next_movement_execution.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_COMMERCIAL_NEXT_MOVEMENT_EXECUTION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_commercial_next_movement_execution_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_commercial_next_movement_execution")
        self.assertEqual(
            config["dependsOn"]["controlledCommercialNextMovementState"],
            "controlled_commercial_next_movement_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_next_movement_execution_result_owner_summary_and_next_monitor_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_next_micro_step", config["allowedSourceNextMovements"])
        self.assertIn("next_micro_step_prepared", config["allowedExecutionResults"])
        self.assertEqual(config["requiredResultByMovement"]["prepare_next_micro_step"], "next_micro_step_prepared")
        self.assertEqual(config["maximumNewPrivateLinks"], 1)
        self.assertEqual(config["maximumNewInvites"], 3)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M88_DOC)

        for pattern in (
            "controlled_commercial_next_movement_state_invalid",
            "controlled_commercial_next_movement_evidence_missing",
            "controlled_commercial_next_movement_execution_source_not_m87_movement",
            "controlled_commercial_next_movement_execution_result_not_allowed_for_m87_movement",
            "next_micro_step_prepared_private_link_limit_exceeded",
            "--use-latest-decision",
            "--confirm-exact-movement",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_commercial_next_movement_execution_monitor_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_commercial_next_movement_execution_monitor.py"
        config_path = TOOL_ROOT / "config" / "controlled_commercial_next_movement_execution_monitor.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_COMMERCIAL_NEXT_MOVEMENT_EXECUTION_MONITOR.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_commercial_next_movement_execution_monitor_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_commercial_next_movement_execution_monitor")
        self.assertEqual(
            config["dependsOn"]["controlledCommercialNextMovementExecutionState"],
            "controlled_commercial_next_movement_execution_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m88_execution_monitor_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("next_micro_step_prepared", config["allowedSourceExecutionResults"])
        self.assertIn("prepare_next_controlled_movement", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForNextMovement"], 1)
        self.assertEqual(config["maximumOpenSupportItems"], 0)
        self.assertEqual(config["maximumRefundRequests"], 0)
        self.assertEqual(config["maximumClaimsIssues"], 0)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M89_DOC)

        for pattern in (
            "controlled_commercial_next_movement_execution_monitor_ready",
            "controlled_commercial_next_movement_execution_state_invalid",
            "controlled_commercial_next_movement_execution_evidence_missing",
            "controlled_commercial_next_movement_execution_monitor_source_not_m88_result",
            "prepare_next_controlled_movement_requires_positive_signal",
            "prepare_next_controlled_movement_blocked_by_risk",
            "--use-latest-execution",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_controlled_commercial_movement_decision_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_controlled_commercial_movement_decision.py"
        config_path = TOOL_ROOT / "config" / "next_controlled_commercial_movement_decision.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "NEXT_CONTROLLED_COMMERCIAL_MOVEMENT_DECISION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_controlled_commercial_movement_decision_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_commercial_movement_decision")
        self.assertEqual(
            config["dependsOn"]["controlledCommercialNextMovementExecutionMonitorState"],
            "controlled_commercial_next_movement_execution_monitor_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m90_next_movement_decision_counts_owner_rationale_and_next_gate_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_next_controlled_movement", config["allowedSourceMonitorDecisions"])
        self.assertIn("prepare_next_micro_step", config["allowedNextMovements"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForMovement"], 1)
        self.assertEqual(config["maximumOpenSupportItems"], 0)
        self.assertEqual(config["maximumRefundRequests"], 0)
        self.assertEqual(config["maximumClaimsIssues"], 0)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M90_DOC)

        for pattern in (
            "next_controlled_commercial_movement_decision_ready",
            "controlled_commercial_next_movement_execution_monitor_state_invalid",
            "controlled_commercial_next_movement_execution_monitor_evidence_missing",
            "next_controlled_commercial_movement_source_not_m89_decision",
            "prepare_next_micro_step_requires_m89_prepare_next_controlled_movement",
            "prepare_next_micro_step_blocked_by_risk",
            "--use-latest-monitor",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_approved_controlled_commercial_movement_execution_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_execution.py"
        config_path = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_execution.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_EXECUTION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "approved_controlled_commercial_movement_execution_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_approved_controlled_commercial_movement_execution")
        self.assertEqual(
            config["dependsOn"]["nextControlledCommercialMovementDecisionState"],
            "next_controlled_commercial_movement_decision_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m91_execution_result_owner_summary_and_next_monitor_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_next_micro_step", config["allowedSourceNextMovements"])
        self.assertIn("next_micro_step_prepared", config["allowedExecutionResults"])
        self.assertEqual(config["requiredResultByMovement"]["prepare_next_micro_step"], "next_micro_step_prepared")
        self.assertEqual(config["maximumNewPrivateLinks"], 1)
        self.assertEqual(config["maximumNewInvites"], 3)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M91_DOC)

        for pattern in (
            "approved_controlled_commercial_movement_execution_ready",
            "next_controlled_commercial_movement_decision_state_invalid",
            "next_controlled_commercial_movement_decision_evidence_missing",
            "approved_controlled_commercial_movement_execution_source_not_m90_movement",
            "approved_controlled_commercial_movement_execution_result_not_allowed_for_m90_movement",
            "next_micro_step_prepared_private_link_limit_exceeded",
            "--use-latest-decision",
            "--confirm-exact-movement",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_approved_controlled_commercial_movement_execution_monitor_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_execution_monitor.py"
        config_path = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_execution_monitor.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_EXECUTION_MONITOR.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "approved_controlled_commercial_movement_execution_monitor_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_approved_controlled_commercial_movement_execution_monitor")
        self.assertEqual(
            config["dependsOn"]["approvedControlledCommercialMovementExecutionState"],
            "approved_controlled_commercial_movement_execution_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m91_execution_monitor_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("next_micro_step_prepared", config["allowedSourceExecutionResults"])
        self.assertIn("prepare_next_decision", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForNextDecision"], 1)
        self.assertEqual(config["maximumOpenSupportItems"], 0)
        self.assertEqual(config["maximumRefundRequests"], 0)
        self.assertEqual(config["maximumClaimsIssues"], 0)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M92_DOC)

        for pattern in (
            "approved_controlled_commercial_movement_execution_monitor_ready",
            "approved_controlled_commercial_movement_execution_state_invalid",
            "approved_controlled_commercial_movement_execution_evidence_missing",
            "approved_controlled_commercial_movement_execution_monitor_source_not_m91_result",
            "prepare_next_decision_requires_positive_signal",
            "prepare_next_decision_blocked_by_risk",
            "--use-latest-execution",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_controlled_commercial_movement_from_m92_decision_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_controlled_commercial_movement_from_m92_decision.py"
        config_path = TOOL_ROOT / "config" / "next_controlled_commercial_movement_from_m92_decision.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "NEXT_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M92_DECISION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_controlled_commercial_movement_from_m92_decision_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_commercial_movement_from_m92_decision")
        self.assertEqual(
            config["dependsOn"]["approvedControlledCommercialMovementExecutionMonitorState"],
            "approved_controlled_commercial_movement_execution_monitor_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m93_next_movement_decision_counts_owner_rationale_and_next_gate_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_next_decision", config["allowedSourceMonitorDecisions"])
        self.assertIn("prepare_next_micro_step", config["allowedNextMovements"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForMovement"], 1)
        self.assertEqual(config["maximumOpenSupportItems"], 0)
        self.assertEqual(config["maximumRefundRequests"], 0)
        self.assertEqual(config["maximumClaimsIssues"], 0)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M93_DOC)

        for pattern in (
            "next_controlled_commercial_movement_from_m92_decision_ready",
            "approved_controlled_commercial_movement_execution_monitor_state_invalid",
            "approved_controlled_commercial_movement_execution_monitor_evidence_missing",
            "next_controlled_commercial_movement_from_m92_source_not_m92_decision",
            "prepare_next_micro_step_requires_m92_prepare_next_decision",
            "prepare_next_micro_step_blocked_by_risk",
            "--use-latest-monitor",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_approved_controlled_commercial_movement_from_m93_execution_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_from_m93_execution.py"
        config_path = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_from_m93_execution.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M93_EXECUTION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "approved_controlled_commercial_movement_from_m93_execution_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_approved_controlled_commercial_movement_from_m93_execution")
        self.assertEqual(
            config["dependsOn"]["nextControlledCommercialMovementFromM92DecisionState"],
            "next_controlled_commercial_movement_from_m92_decision_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m94_execution_result_owner_summary_and_next_monitor_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_next_micro_step", config["allowedSourceNextMovements"])
        self.assertIn("next_micro_step_prepared", config["allowedExecutionResults"])
        self.assertEqual(config["requiredResultByMovement"]["prepare_next_micro_step"], "next_micro_step_prepared")
        self.assertEqual(config["maximumNewPrivateLinks"], 1)
        self.assertEqual(config["maximumNewInvites"], 3)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M94_DOC)

        for pattern in (
            "approved_controlled_commercial_movement_from_m93_execution_ready",
            "next_controlled_commercial_movement_from_m92_decision_state_invalid",
            "next_controlled_commercial_movement_from_m92_decision_evidence_missing",
            "approved_controlled_commercial_movement_from_m93_execution_source_not_m93_movement",
            "approved_controlled_commercial_movement_from_m93_execution_result_not_allowed_for_m93_movement",
            "next_micro_step_prepared_private_link_limit_exceeded",
            "--use-latest-decision",
            "--confirm-exact-movement",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_approved_controlled_commercial_movement_from_m93_execution_monitor_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_from_m93_execution_monitor.py"
        config_path = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_from_m93_execution_monitor.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M93_EXECUTION_MONITOR.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "approved_controlled_commercial_movement_from_m93_execution_monitor_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_approved_controlled_commercial_movement_from_m93_execution_monitor")
        self.assertEqual(
            config["dependsOn"]["approvedControlledCommercialMovementFromM93ExecutionState"],
            "approved_controlled_commercial_movement_from_m93_execution_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m95_execution_monitor_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("next_micro_step_prepared", config["allowedSourceExecutionResults"])
        self.assertIn("prepare_next_decision", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForNextDecision"], 1)
        self.assertEqual(config["maximumOpenSupportItems"], 0)
        self.assertEqual(config["maximumRefundRequests"], 0)
        self.assertEqual(config["maximumClaimsIssues"], 0)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M95_DOC)

        for pattern in (
            "approved_controlled_commercial_movement_from_m93_execution_monitor_ready",
            "approved_controlled_commercial_movement_from_m93_execution_state_invalid",
            "approved_controlled_commercial_movement_from_m93_execution_evidence_missing",
            "approved_controlled_commercial_movement_from_m93_execution_monitor_source_not_m94_result",
            "prepare_next_decision_requires_positive_signal",
            "prepare_next_decision_blocked_by_risk",
            "--use-latest-execution",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_controlled_commercial_movement_from_m95_decision_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_controlled_commercial_movement_from_m95_decision.py"
        config_path = TOOL_ROOT / "config" / "next_controlled_commercial_movement_from_m95_decision.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "NEXT_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M95_DECISION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_controlled_commercial_movement_from_m95_decision_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_commercial_movement_from_m95_decision")
        self.assertEqual(
            config["dependsOn"]["approvedControlledCommercialMovementFromM93ExecutionMonitorState"],
            "approved_controlled_commercial_movement_from_m93_execution_monitor_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m96_next_movement_decision_counts_owner_rationale_and_next_gate_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_next_decision", config["allowedSourceMonitorDecisions"])
        self.assertIn("prepare_next_micro_step", config["allowedNextMovements"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForMovement"], 1)
        self.assertEqual(config["maximumOpenSupportItems"], 0)
        self.assertEqual(config["maximumRefundRequests"], 0)
        self.assertEqual(config["maximumClaimsIssues"], 0)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M96_DOC)

        for pattern in (
            "next_controlled_commercial_movement_from_m95_decision_ready",
            "approved_controlled_commercial_movement_from_m93_execution_monitor_state_invalid",
            "approved_controlled_commercial_movement_from_m93_execution_monitor_evidence_missing",
            "next_controlled_commercial_movement_from_m95_source_not_m95_decision",
            "prepare_next_micro_step_requires_m95_prepare_next_decision",
            "prepare_next_micro_step_blocked_by_risk",
            "--use-latest-monitor",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_approved_controlled_commercial_movement_from_m96_decision_execution_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_from_m96_decision_execution.py"
        config_path = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_from_m96_decision_execution.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M96_DECISION_EXECUTION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "approved_controlled_commercial_movement_from_m96_decision_execution_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_approved_controlled_commercial_movement_from_m96_decision_execution")
        self.assertEqual(
            config["dependsOn"]["nextControlledCommercialMovementFromM95DecisionState"],
            "next_controlled_commercial_movement_from_m95_decision_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m97_execution_result_owner_summary_and_next_monitor_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_next_micro_step", config["allowedSourceNextMovements"])
        self.assertEqual(config["requiredResultByMovement"]["prepare_next_micro_step"], "next_micro_step_prepared")
        self.assertEqual(config["maximumNewPrivateLinks"], 1)
        self.assertEqual(config["maximumNewInvites"], 3)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M97_DOC)

        for pattern in (
            "approved_controlled_commercial_movement_from_m96_decision_execution_ready",
            "next_controlled_commercial_movement_from_m95_decision_state_invalid",
            "approved_controlled_commercial_movement_from_m96_decision_execution_source_not_m96_movement",
            "approved_controlled_commercial_movement_from_m96_decision_execution_result_not_allowed_for_m96_movement",
            "non_micro_step_execution_must_not_create_new_traffic",
            "--use-latest-decision",
            "--confirm-exact-movement",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_approved_controlled_commercial_movement_from_m96_decision_execution_monitor_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py"
        config_path = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_from_m96_decision_execution_monitor.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M96_DECISION_EXECUTION_MONITOR.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_approved_controlled_commercial_movement_from_m96_decision_execution_monitor")
        self.assertEqual(
            config["dependsOn"]["approvedControlledCommercialMovementFromM96DecisionExecutionState"],
            "approved_controlled_commercial_movement_from_m96_decision_execution_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m98_execution_monitor_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("next_micro_step_prepared", config["allowedSourceExecutionResults"])
        self.assertIn("prepare_next_decision", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForNextDecision"], 1)
        self.assertEqual(config["maximumOpenSupportItems"], 0)
        self.assertEqual(config["maximumRefundRequests"], 0)
        self.assertEqual(config["maximumClaimsIssues"], 0)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M98_DOC)

        for pattern in (
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_ready",
            "approved_controlled_commercial_movement_from_m96_decision_execution_state_invalid",
            "approved_controlled_commercial_movement_from_m96_decision_execution_evidence_missing",
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_source_not_m97_result",
            "prepare_next_decision_requires_positive_signal",
            "prepare_next_decision_blocked_by_risk",
            "--use-latest-execution",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_controlled_commercial_movement_from_m98_decision_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_controlled_commercial_movement_from_m98_decision.py"
        config_path = TOOL_ROOT / "config" / "next_controlled_commercial_movement_from_m98_decision.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "NEXT_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M98_DECISION.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_controlled_commercial_movement_from_m98_decision_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_commercial_movement_from_m98_decision")
        self.assertEqual(
            config["dependsOn"]["approvedControlledCommercialMovementFromM96DecisionExecutionMonitorState"],
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_ready",
        )
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_m99_next_movement_decision_counts_owner_rationale_and_next_gate_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_next_decision", config["allowedSourceMonitorDecisions"])
        self.assertIn("prepare_next_micro_step", config["allowedNextMovements"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["minimumPositiveSignalsForMovement"], 1)
        self.assertEqual(config["maximumOpenSupportItems"], 0)
        self.assertEqual(config["maximumRefundRequests"], 0)
        self.assertEqual(config["maximumClaimsIssues"], 0)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M99_DOC)

        for pattern in (
            "next_controlled_commercial_movement_from_m98_decision_ready",
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_state_invalid",
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_evidence_missing",
            "next_controlled_commercial_movement_from_m98_source_not_m98_decision",
            "prepare_next_micro_step_requires_m98_prepare_next_decision",
            "prepare_next_micro_step_blocked_by_risk",
            "--use-latest-monitor",
            "--confirm-no-automation",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)


if __name__ == "__main__":
    unittest.main()
