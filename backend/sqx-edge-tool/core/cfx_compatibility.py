from __future__ import annotations

import hashlib
import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


CFX_COMPATIBILITY_AUDIT_VERSION = "cfx-compatibility-audit-v1"

SOURCE_LABELS = {
    "-1": "unbound",
    "0": "sq_default",
    "2": "dukascopy",
    "4": "darwinex",
    "5": "sq_equity_data",
}

BROKER_LABELS = {
    "-1": "sq_default_no_broker",
    "3": "dukascopy",
    "4": "darwinex",
}


@dataclass
class CfxCompatibilityIssue:
    code: str
    severity: str
    file: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "file": self.file,
            "detail": self.detail,
        }


@dataclass
class CfxXmlSummary:
    file: str
    chart_symbols: set[str] = field(default_factory=set)
    resource_symbols: set[str] = field(default_factory=set)
    embedded_symbols: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)
    brokers: set[str] = field(default_factory=set)
    broker_table: set[str] = field(default_factory=set)
    precisions: set[str] = field(default_factory=set)
    timezones: set[str] = field(default_factory=set)
    market_open_sessions: set[str] = field(default_factory=set)
    resource_sessions: set[str] = field(default_factory=set)
    instrument_data_types: set[str] = field(default_factory=set)
    absolute_path_refs: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "chartSymbols": sorted(self.chart_symbols),
            "resourceSymbols": sorted(self.resource_symbols),
            "embeddedSymbols": sorted(self.embedded_symbols),
            "sources": sorted(self.sources),
            "sourceLabels": sorted({SOURCE_LABELS.get(value, f"unknown:{value}") for value in self.sources}),
            "brokers": sorted(self.brokers),
            "brokerLabels": sorted({BROKER_LABELS.get(value, f"unknown:{value}") for value in self.brokers}),
            "brokerTable": sorted(self.broker_table),
            "precisions": sorted(self.precisions),
            "timezones": sorted(self.timezones),
            "marketOpenSessions": sorted(self.market_open_sessions),
            "resourceSessions": sorted(self.resource_sessions),
            "instrumentDataTypes": sorted(self.instrument_data_types),
            "absolutePathRefs": self.absolute_path_refs,
        }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_abs_path(value: str) -> bool:
    return bool(re.search(r"[A-Za-z]:[\\/]", value or ""))


def _read_xml_roots(cfx_path: Path) -> list[tuple[str, ET.Element]]:
    roots: list[tuple[str, ET.Element]] = []
    with zipfile.ZipFile(cfx_path) as archive:
        for name in archive.namelist():
            if not name.endswith(".xml"):
                continue
            roots.append((name, ET.fromstring(archive.read(name))))
    return roots


def _safe_project_name(config_root: ET.Element | None, cfx_path: Path) -> str:
    if config_root is not None:
        return config_root.get("name") or cfx_path.stem
    return cfx_path.stem


def _summarize_xml(name: str, root: ET.Element) -> CfxXmlSummary:
    summary = CfxXmlSummary(file=name)
    for node in root.iter():
        for value in node.attrib.values():
            if _is_abs_path(str(value)):
                summary.absolute_path_refs += 1
    for chart in root.findall(".//Setup/Chart"):
        if chart.get("symbol"):
            summary.chart_symbols.add(str(chart.get("symbol")))
    for symbol in root.findall(".//Resources/Symbols/Symbol"):
        if symbol.get("name"):
            summary.resource_symbols.add(str(symbol.get("name")))
        if symbol.get("source"):
            summary.sources.add(str(symbol.get("source")))
        if symbol.get("broker"):
            summary.brokers.add(str(symbol.get("broker")))
        if symbol.get("precision"):
            summary.precisions.add(str(symbol.get("precision")))
        if symbol.get("timezone"):
            summary.timezones.add(str(symbol.get("timezone")))
        info = symbol.find("InstrumentInfo")
        if info is not None and info.get("dataType"):
            summary.instrument_data_types.add(str(info.get("dataType")))
    for broker in root.findall(".//Resources/Brokers/Broker"):
        if broker.get("id"):
            summary.broker_table.add(str(broker.get("id")))
    for session in root.findall(".//Resources/Sessions/Session"):
        summary.resource_sessions.add(str(session.get("name") or "unnamed"))
    for param in root.findall(".//BuildTradingOptions/Params/Param[@key='MarketOpenSession']"):
        summary.market_open_sessions.add(str(param.text or ""))
    for node in root.findall(".//BackupStrategyTemplate//symbol"):
        if node.text:
            summary.embedded_symbols.add(str(node.text))
    return summary


def _issue(issues: list[CfxCompatibilityIssue], code: str, severity: str, file: str, detail: str) -> None:
    issues.append(CfxCompatibilityIssue(code=code, severity=severity, file=file, detail=detail))


def _inspect_summary(summary: CfxXmlSummary, issues: list[CfxCompatibilityIssue]) -> None:
    file = summary.file
    for symbol in sorted(summary.resource_symbols):
        if symbol.startswith("[[") and symbol.endswith("]]"):
            _issue(issues, "placeholder_symbol", "fail", file, "resource symbol is an unresolved SQX placeholder")
    for source in sorted(summary.sources):
        if source == "5":
            _issue(issues, "sq_equity_data_dependency", "fail", file, "uses SQ Equity data; other hosts may need SQ Data subscription")
        elif source == "2":
            _issue(issues, "dukascopy_dependency", "warn", file, "uses Dukascopy data source for cross-broker OOS validation")
        elif source not in {"0", "4"}:
            _issue(issues, "unknown_data_source", "warn", file, f"uses source id {source}")
    for broker in sorted(summary.brokers):
        if broker == "-1":
            has_placeholder = any(symbol.startswith("[[") and symbol.endswith("]]") for symbol in summary.resource_symbols)
            if "0" not in summary.sources or has_placeholder:
                _issue(issues, "unbound_broker", "fail", file, "symbol broker is unbound (-1)")
        elif broker not in summary.broker_table:
            _issue(issues, "missing_broker_entry", "fail", file, f"symbol broker {broker} is not declared in Resources/Brokers")
    if summary.resource_sessions:
        _issue(issues, "stale_resource_session", "fail", file, "Resources/Sessions contains session resources")
    for session in sorted(summary.market_open_sessions):
        if session and session != "No Session":
            _issue(issues, "stale_market_open_session", "fail", file, "MarketOpenSession is not No Session")
    for chart in sorted(summary.chart_symbols):
        if chart not in summary.resource_symbols:
            _issue(issues, "chart_missing_resource_symbol", "fail", file, "chart symbol is missing from Resources/Symbols")
    for embedded in sorted(summary.embedded_symbols):
        if summary.chart_symbols and embedded not in summary.chart_symbols:
            _issue(issues, "embedded_symbol_mismatch", "fail", file, "BackupStrategyTemplate symbol does not match chart symbols")
    for precision in sorted(summary.precisions):
        if precision != "TICK":
            _issue(issues, "non_tick_precision", "warn", file, f"symbol precision is {precision}")
    for timezone in sorted(summary.timezones):
        if timezone != "EETUS":
            _issue(issues, "non_darwinex_timezone", "warn", file, f"symbol timezone is {timezone}")
    if summary.absolute_path_refs:
        _issue(issues, "absolute_xml_path", "warn", file, "XML keeps absolute paths from the source machine")
    if len(summary.chart_symbols) > 1:
        _issue(issues, "mixed_chart_symbols", "warn", file, "multiple chart symbols appear in one task")


def _host_profile(summaries: list[CfxXmlSummary]) -> str:
    sources = {source for summary in summaries for source in summary.sources}
    brokers = {broker for summary in summaries for broker in summary.brokers}
    resource_symbols = {symbol for summary in summaries for symbol in summary.resource_symbols}
    if sources == {"4"} and brokers == {"4"} and all(symbol.endswith("_darwinex") for symbol in resource_symbols if symbol):
        return "sqx142_darwinex"
    if "2" in sources and sources.issubset({"0", "2"}) and brokers.issubset({"-1", "3"}):
        return "sq_default_cross_broker_oos2"
    if "2" in sources and sources.issubset({"2", "4"}) and brokers.issubset({"3", "4"}):
        return "sqx_edge_cross_broker_oos2"
    if "5" in sources or any(symbol.startswith("[[") for symbol in resource_symbols):
        return "sq_equity_data_subscription_bound"
    if len(sources) > 1 or len(brokers) > 1:
        return "mixed_source_profile"
    if "2" in sources:
        return "dukascopy_or_legacy_profile"
    return "unknown_or_custom_profile"


def audit_cfx_compatibility(cfx_path: str | Path) -> dict[str, Any]:
    path = Path(cfx_path)
    roots = _read_xml_roots(path)
    config_root = next((root for name, root in roots if name == "config.xml"), None)
    summaries = [_summarize_xml(name, root) for name, root in roots if name != "config.xml"]
    issues: list[CfxCompatibilityIssue] = []
    for summary in summaries:
        _inspect_summary(summary, issues)
    severities = {issue.severity for issue in issues}
    verdict = "fail" if "fail" in severities else "warn" if "warn" in severities else "pass"
    return {
        "version": CFX_COMPATIBILITY_AUDIT_VERSION,
        "fileName": path.name,
        "sha256": _sha256(path),
        "projectName": _safe_project_name(config_root, path),
        "hostProfile": _host_profile(summaries),
        "verdict": verdict,
        "issueCount": len(issues),
        "failCount": sum(1 for issue in issues if issue.severity == "fail"),
        "warnCount": sum(1 for issue in issues if issue.severity == "warn"),
        "issues": [issue.as_dict() for issue in issues],
        "xml": [summary.as_dict() for summary in summaries],
    }


def audit_many(paths: list[str | Path]) -> dict[str, Any]:
    reports = [audit_cfx_compatibility(path) for path in paths]
    return {
        "version": CFX_COMPATIBILITY_AUDIT_VERSION,
        "count": len(reports),
        "passCount": sum(1 for report in reports if report["verdict"] == "pass"),
        "warnCount": sum(1 for report in reports if report["verdict"] == "warn"),
        "failCount": sum(1 for report in reports if report["verdict"] == "fail"),
        "reports": reports,
    }


def render_markdown(report: dict[str, Any]) -> str:
    reports = report.get("reports") or [report]
    lines = ["# CFX Compatibility Audit", ""]
    for item in reports:
        lines.extend([
            f"## {item['fileName']}",
            "",
            f"- Verdict: `{item['verdict']}`",
            f"- Host profile: `{item['hostProfile']}`",
            f"- Project: `{item['projectName']}`",
            f"- Issues: `{item['issueCount']}` (`{item['failCount']}` fail, `{item['warnCount']}` warn)",
        ])
        for issue in item.get("issues", [])[:20]:
            lines.append(f"- `{issue['severity']}` `{issue['code']}` in `{issue['file']}`: {issue['detail']}")
        if len(item.get("issues", [])) > 20:
            lines.append(f"- ... {len(item['issues']) - 20} more issues")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def to_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
