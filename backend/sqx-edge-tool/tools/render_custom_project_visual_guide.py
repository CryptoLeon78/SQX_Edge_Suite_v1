from __future__ import annotations

import argparse
import json
import os
import re
import struct
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL_ROOT = REPO_ROOT / "backend" / "sqx-edge-tool"
DEFAULT_MANIFEST = REPO_ROOT / "resources" / "pdf" / "custom_project_visual_guide" / "manifest.json"
DEFAULT_SCREENSHOTS_DIR = REPO_ROOT / "resources" / "pdf" / "custom_project_visual_guide" / "screenshots"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "pdf" / "sqx_custom_project_visual_check_guide.pdf"
DEFAULT_PROFILE = TOOL_ROOT / "config" / "generator_profiles.json"
MIN_SCREENSHOT_WIDTH = 900
MIN_SCREENSHOT_HEIGHT = 500


DEFAULT_EXTERNAL_SOURCES = [
    {
        "title": "StrategyQuant - Introduction to custom projects",
        "url": "https://strategyquant.com/doc/strategyquant/introduction-to-custom-projects/",
        "takeaway": (
            "Un custom project es una cadena de tareas que automatiza construccion, "
            "retests y almacenamiento final en databanks. La revision visual debe "
            "confirmar que la cadena de tareas existe y conserva su orden."
        ),
    },
    {
        "title": "StrategyQuant - Main concepts",
        "url": "https://strategyquant.com/doc/strategyquant/custom-projects-main-concepts/",
        "takeaway": (
            "Los databanks son puntos de entrada y salida entre tareas. Un custom "
            "aparentemente valido puede fallar metodologicamente si una tarea lee "
            "o escribe en el databank equivocado."
        ),
    },
    {
        "title": "StrategyQuant - Custom analysis",
        "url": "https://strategyquant.com/doc/strategyquant/custom-analysis/",
        "takeaway": (
            "Custom Analysis puede calcular, filtrar o transformar estrategias. "
            "La guia exige revisar metodo, filtro y databank para evitar filtros "
            "activos por error."
        ),
    },
    {
        "title": "StrategyQuant - Broker profiles",
        "url": "https://strategyquant.com/doc/strategyquant/broker-profiles/",
        "takeaway": (
            "Los broker profiles afectan datos, simbolos, sesiones y costes. Por "
            "eso el PDF separa el perfil destino del usuario y el Retest 1/OOS2 "
            "con Dukascopy."
        ),
    },
    {
        "title": "StrategyQuant Forum - Custom projects don't work",
        "url": "https://strategyquant.com/forum/topic/custom-projects-dont-work/",
        "takeaway": (
            "Usuarios reportaron consumo alto de RAM/CPU y bloqueos al abrir "
            "customs con muchos datos en databanks. La guia recomienda comprobar "
            "conteos y no usar databanks enormes como evidencia permanente."
        ),
    },
    {
        "title": "StrategyQuant Forum - Two mins run and crashing everytime",
        "url": "https://strategyquant.com/forum/topic/two-mins-run-and-crashing-everytime/",
        "takeaway": (
            "Los reportes apuntan a sensibilidad de heap, cores, GPU y version. "
            "El PDF lo trata como riesgo operativo, no como defecto garantizado "
            "del custom generado."
        ),
    },
    {
        "title": "StrategyQuant Forum - Performance decay in Build 143",
        "url": "https://strategyquant.com/forum/topic/performance-decay-in-build-143/",
        "takeaway": (
            "Soporte de SQX recomendo cuidar Java/GC, mantener databanks ligeros, "
            "reservar memoria para el sistema y ajustar threads a nucleos fisicos."
        ),
    },
]


@dataclass
class ScreenshotStatus:
    item: dict[str, Any]
    path: Path
    exists: bool
    width: int | None = None
    height: int | None = None
    problem: str | None = None

    @property
    def ok(self) -> bool:
        return self.exists and self.problem is None


def sanitize_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"(?<![A-Za-z])[A-Za-z]:[\\/][^\s,;\"')]+", "[ruta-local]", text)
    text = re.sub(r"[\w.\-+]+@[\w.\-]+\.\w+", "[email]", text)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[ip]", text)
    text = re.sub(r"\b[A-Fa-f0-9]{32,}\b", "[hash-o-token]", text)
    return text


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_external_sources(source_cache: Path | None) -> list[dict[str, str]]:
    if source_cache and source_cache.is_file():
        data = load_json(source_cache)
        raw_sources = data.get("sources", data if isinstance(data, list) else [])
    else:
        raw_sources = DEFAULT_EXTERNAL_SOURCES
    sources: list[dict[str, str]] = []
    for source in raw_sources:
        if not isinstance(source, dict):
            continue
        sources.append({
            "title": sanitize_text(source.get("title")),
            "url": sanitize_text(source.get("url")),
            "takeaway": sanitize_text(source.get("takeaway") or source.get("summary")),
        })
    return sources


def _png_size(header: bytes) -> tuple[int, int] | None:
    if len(header) >= 24 and header.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", header[16:24])
    return None


def _jpeg_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        if handle.read(2) != b"\xff\xd8":
            return None
        while True:
            marker_start = handle.read(1)
            if not marker_start:
                return None
            if marker_start != b"\xff":
                continue
            marker = handle.read(1)
            while marker == b"\xff":
                marker = handle.read(1)
            if marker in {b"\xc0", b"\xc1", b"\xc2", b"\xc3", b"\xc5", b"\xc6", b"\xc7", b"\xc9", b"\xca", b"\xcb", b"\xcd", b"\xce", b"\xcf"}:
                handle.read(3)
                height, width = struct.unpack(">HH", handle.read(4))
                return width, height
            if marker in {b"\xd8", b"\xd9"}:
                continue
            segment_length = struct.unpack(">H", handle.read(2))[0]
            handle.seek(segment_length - 2, os.SEEK_CUR)


def image_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(32)
    return _png_size(header) or _jpeg_size(path)


def validate_screenshots(manifest: dict[str, Any], screenshots_dir: Path) -> list[ScreenshotStatus]:
    statuses: list[ScreenshotStatus] = []
    for item in manifest.get("screenshots", []):
        file_name = str(item.get("file") or "")
        path = screenshots_dir / file_name
        if not file_name:
            statuses.append(ScreenshotStatus(item=item, path=path, exists=False, problem="sin nombre de archivo"))
            continue
        if not path.is_file():
            statuses.append(ScreenshotStatus(item=item, path=path, exists=False, problem="captura pendiente"))
            continue
        size = image_size(path)
        if not size:
            statuses.append(ScreenshotStatus(item=item, path=path, exists=True, problem="formato no legible"))
            continue
        width, height = size
        problem = None
        if width < MIN_SCREENSHOT_WIDTH or height < MIN_SCREENSHOT_HEIGHT:
            problem = f"resolucion baja {width}x{height}; minimo {MIN_SCREENSHOT_WIDTH}x{MIN_SCREENSHOT_HEIGHT}"
        statuses.append(ScreenshotStatus(item=item, path=path, exists=True, width=width, height=height, problem=problem))
    return statuses


def detect_sqx_process() -> str:
    if os.name != "nt":
        return "no comprobado: deteccion de proceso SQX solo implementada para Windows"
    command = (
        "Get-Process | Where-Object { "
        "$_.ProcessName -match 'StrategyQuant|SQX|javaw|java' -or "
        "$_.MainWindowTitle -match 'StrategyQuant|SQX' } | "
        "Select-Object ProcessName,Id,MainWindowTitle | ConvertTo-Json -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:
        return f"no comprobado: {exc}"
    text = (result.stdout or "").strip()
    if not text:
        return "no detectado"
    return sanitize_text(text)


def strict_failures(statuses: list[ScreenshotStatus]) -> list[str]:
    failures: list[str] = []
    for status in statuses:
        if not status.item.get("required", True):
            continue
        if not status.ok:
            failures.append(f"{status.item.get('id')}: {status.problem} ({status.path})")
    return failures


def expected_period_rows(profile: dict[str, Any]) -> list[list[str]]:
    rows = [["Clave", "Desde", "Hasta"]]
    for key, value in sorted((profile.get("retestPeriods") or {}).items()):
        if isinstance(value, list) and len(value) >= 2:
            rows.append([key, str(value[0]), str(value[1])])
    return rows


def target_profile_rows(profile: dict[str, Any]) -> list[list[str]]:
    rows = [["Perfil", "Modo", "Source", "Broker", "Precision", "Timezone"]]
    broker_profiles = profile.get("brokerProfiles") or {}
    for key, value in sorted((profile.get("targetProfiles") or {}).items()):
        broker_profile = broker_profiles.get(value.get("brokerProfile"), {})
        if value.get("mode") == "custom_override":
            source_id = value.get("sourceId", "manual")
            broker_id = value.get("brokerId", "manual")
            precision = value.get("precision", "manual")
            timezone = value.get("timezone", "manual")
        else:
            source_id = value.get("sourceId", broker_profile.get("sourceId", ""))
            broker_id = value.get("brokerId", broker_profile.get("brokerId", ""))
            precision = value.get("precision", broker_profile.get("precision", ""))
            timezone = value.get("timezone", broker_profile.get("timezone", ""))
        rows.append([
            key,
            str(value.get("mode", "")),
            str(source_id),
            str(broker_id),
            str(precision),
            str(timezone),
        ])
    return rows


def cross_broker_rows(profile: dict[str, Any]) -> list[list[str]]:
    rows = [["Capa", "Tarea XML", "Periodo", "Broker profile", "Cobertura minima"]]
    for capa, tasks in sorted((profile.get("crossBrokerRetests") or {}).items()):
        for task_xml, value in sorted((tasks or {}).items()):
            rows.append([
                str(capa),
                str(task_xml),
                str(value.get("period", "")),
                str(value.get("brokerProfile", "")),
                f"{value.get('minCoverageDays', '')} dias",
            ])
    return rows


def add_table(elements: list[Any], rows: list[list[str]], col_widths: list[float] | None = None) -> None:
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph
    from reportlab.platypus import Table, TableStyle

    header_style = ParagraphStyle("TableHeader", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.white)
    cell_style = ParagraphStyle("TableCell", fontName="Helvetica", fontSize=8, leading=10, textColor=colors.HexColor("#111827"))
    wrapped_rows = []
    for row_index, row in enumerate(rows):
        style = header_style if row_index == 0 else cell_style
        wrapped_rows.append([Paragraph(escape(str(cell)), style) for cell in row])
    table = Table(wrapped_rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172033")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c7ccd8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fb")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)


def build_pdf(
    *,
    output: Path,
    manifest: dict[str, Any],
    profile: dict[str, Any],
    sources: list[dict[str, str]],
    statuses: list[ScreenshotStatus],
    project_name: str = "",
    cfx_file: str = "",
) -> None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise SystemExit(
            "Falta la dependencia reportlab. Instala con: python -m pip install reportlab"
        ) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontSize=24, leading=29, alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], fontSize=15, leading=19, spaceBefore=12, spaceAfter=8, textColor=colors.HexColor("#172033")))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontSize=9, leading=12, borderColor=colors.HexColor("#94a3b8"), borderWidth=0.5, borderPadding=7, backColor=colors.HexColor("#f8fafc")))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(1.4 * cm, 1.0 * cm, "SQX Edge Suite - Guia visual Custom Project")
        canvas.drawRightString(A4[0] - 1.4 * cm, 1.0 * cm, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=1.35 * cm,
        leftMargin=1.35 * cm,
        topMargin=1.45 * cm,
        bottomMargin=1.45 * cm,
        title="SQX Custom Project Visual Check Guide",
    )

    elements: list[Any] = []
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    elements.append(Paragraph("PDF Guia Visual SQX Custom Project", styles["CoverTitle"]))
    elements.append(Paragraph(
        "Guia maestra para comprobar visualmente en StrategyQuant X que un custom project generado conserva tareas, periodos, databanks, broker/source, Dukascopy/OOS2, precision, sesiones y parametros criticos.",
        styles["BodyText"],
    ))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "Aviso: esta guia verifica coherencia tecnica y metodologica. No certifica rentabilidad, no elimina el riesgo de trading y no sustituye una validacion independiente.",
        styles["Callout"],
    ))
    elements.append(Spacer(1, 10))
    add_table(elements, [
        ["Campo", "Valor"],
        ["Fecha de generacion", generated_at],
        ["Custom project", sanitize_text(project_name) or "Guia maestra"],
        [".cfx asociado", sanitize_text(cfx_file) or "No asociado"],
        ["Version manifiesto", str(manifest.get("version", "custom-project-visual-guide-v1"))],
        ["Perfil de referencia", str(profile.get("version", ""))],
        ["Capturas requeridas", str(sum(1 for s in statuses if s.item.get("required", True)))],
        ["Capturas presentes", str(sum(1 for s in statuses if s.ok))],
    ], [5 * cm, 11 * cm])

    elements.append(PageBreak())
    elements.append(Paragraph("Checklist rapido", styles["Section"]))
    checklist = [
        "Abrir el custom project en SQX y confirmar que no aparecen errores rojos de recursos.",
        "Revisar que el flujo de tareas conserva Build, Retest 0, Retest 1/OOS2, robustez, WFM y Forward.",
        "Confirmar Input/Output de cada tarea antes de ejecutar o registrar resultados.",
        "Verificar simbolo principal, simbolo Dukascopy, source, broker, timezone y precision en Data Manager.",
        "Comprobar que Retest 1/OOS2 mantiene Dukascopy por metodologia, incluso si el perfil destino usa otro broker.",
        "Comprobar que Custom Analysis y DeleteFailedStrategies coinciden con el objetivo de la tarea.",
        "Mantener databanks ligeros y exportar evidencia externa cuando el volumen de estrategias crezca.",
    ]
    for item in checklist:
        elements.append(Paragraph(f"- {item}", styles["BodyText"]))

    elements.append(Paragraph("Valores SQX Edge de referencia", styles["Section"]))
    elements.append(Paragraph("Periodos metodologicos definidos en generator_profiles.json.", styles["BodyText"]))
    add_table(elements, expected_period_rows(profile), [5.3 * cm, 4.2 * cm, 4.2 * cm])
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Target profiles disponibles para generacion y descarga.", styles["BodyText"]))
    add_table(elements, target_profile_rows(profile), [4.1 * cm, 4.1 * cm, 2.0 * cm, 2.0 * cm, 2.2 * cm, 2.4 * cm])
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Retests cross-broker protegidos.", styles["BodyText"]))
    add_table(elements, cross_broker_rows(profile), [1.5 * cm, 4.2 * cm, 3.5 * cm, 4.0 * cm, 3.2 * cm])

    elements.append(PageBreak())
    elements.append(Paragraph("Capturas criticas", styles["Section"]))
    elements.append(Paragraph(
        "Cada captura debe tomarse desde SQX real con el custom abierto. Si una captura aparece como pendiente, la guia sirve como lista de trabajo pero no como evidencia final.",
        styles["BodyText"],
    ))
    for status in statuses:
        item = status.item
        rows = [
            [Paragraph("Zona SQX", styles["Small"]), Paragraph(escape(sanitize_text(item.get("sqxZone"))), styles["Small"])],
            [Paragraph("Riesgo cubierto", styles["Small"]), Paragraph(escape(sanitize_text(item.get("risk"))), styles["Small"])],
            [Paragraph("Valores esperados", styles["Small"]), Paragraph(escape(sanitize_text(item.get("expectedValues"))), styles["Small"])],
            [Paragraph("Estado", styles["Small"]), Paragraph(escape("OK" if status.ok else sanitize_text(status.problem)), styles["Small"])],
        ]
        block: list[Any] = [Paragraph(sanitize_text(item.get("title")), styles["Heading3"])]
        meta = Table(rows, colWidths=[3.6 * cm, 13.2 * cm], hAlign="LEFT")
        meta.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8edf5")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c7ccd8")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        block.append(meta)
        block.append(Spacer(1, 6))
        if status.ok:
            img = Image(str(status.path))
            max_width = 16.4 * cm
            max_height = 8.8 * cm
            scale = min(max_width / img.imageWidth, max_height / img.imageHeight)
            img.drawWidth = img.imageWidth * scale
            img.drawHeight = img.imageHeight * scale
            block.append(img)
        else:
            placeholder = Table(
                [[Paragraph(f"CAPTURA PENDIENTE: {sanitize_text(status.path.name)}", styles["BodyText"])]],
                colWidths=[16.4 * cm],
                rowHeights=[3.2 * cm],
            )
            placeholder.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff7ed")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#f97316")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            block.append(placeholder)
        block.append(Spacer(1, 10))
        elements.append(KeepTogether(block))

    elements.append(PageBreak())
    elements.append(Paragraph("Errores tipicos vistos fuera", styles["Section"]))
    risk_rows = [["Riesgo", "Correccion visual en SQX"]]
    risk_rows.extend([
        ["Databanks enormes y RAM/CPU", "Revisar conteos, limpiar/exportar evidencia y evitar guardar miles de estrategias vivas sin necesidad."],
        ["Version/entorno Java diferente", "Anotar version SQX, Java/GC, RAM asignada, threads y GPU antes de comparar resultados."],
        ["Broker/source/simbolo no portable", "Confirmar Data Manager, broker profile, source id, symbol exacto, timezone y precision."],
        ["Custom Analysis o filtro activo por error", "Revisar metodo, filtro, Input y Output en Ranking/Custom Analysis."],
        ["Periodos desalineados", "Comparar Build, Retest 0, Retest 1, Robustness y Forward contra la tabla de referencia."],
    ])
    add_table(elements, risk_rows, [5.2 * cm, 11.4 * cm])

    elements.append(Paragraph("Como comparar contra un .cfx", styles["Section"]))
    elements.append(Paragraph(
        "Para una auditoria tecnica del archivo generado, ejecutar: python backend\\sqx-edge-tool\\tools\\cfx_compatibility_audit.py --json ruta\\al\\custom.cfx. El resultado debe revisarse junto con las capturas: el auditor detecta simbolos placeholder, dependencia SQ Equity Data, broker no declarado, sesiones obsoletas, symbols chart/resource distintos, precision/timezone y paths absolutos.",
        styles["BodyText"],
    ))

    elements.append(Paragraph("Fuentes usadas", styles["Section"]))
    for source in sources:
        elements.append(Paragraph(f"<b>{source['title']}</b><br/>{source['takeaway']}<br/><font size='8'>{source['url']}</font>", styles["Small"]))
        elements.append(Spacer(1, 4))

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)


def main() -> int:
    parser = argparse.ArgumentParser(description="Renderiza la guia visual SQX Custom Project en PDF.")
    parser.add_argument("--screenshots-dir", default=str(DEFAULT_SCREENSHOTS_DIR), help="Carpeta con capturas reales de SQX.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="PDF de salida.")
    parser.add_argument("--source-cache", default=None, help="JSON opcional con summaries de fuentes externas.")
    parser.add_argument("--project-name", default="", help="Nombre opcional del custom project asociado al PDF.")
    parser.add_argument("--cfx-file", default="", help="Ruta o nombre opcional del .cfx asociado al PDF.")
    parser.add_argument("--strict", action="store_true", help="Falla si faltan capturas obligatorias o tienen baja resolucion.")
    args = parser.parse_args()

    manifest = load_json(DEFAULT_MANIFEST)
    profile = load_json(DEFAULT_PROFILE)
    screenshots_dir = Path(args.screenshots_dir)
    statuses = validate_screenshots(manifest, screenshots_dir)
    failures = strict_failures(statuses)
    if args.strict and failures:
        process_status = detect_sqx_process()
        print("Validacion estricta fallida: faltan capturas obligatorias o no son legibles.", file=sys.stderr)
        print(f"Estado SQX detectado: {process_status}", file=sys.stderr)
        print("Capturas pendientes:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 2

    sources = load_external_sources(Path(args.source_cache) if args.source_cache else None)
    build_pdf(
        output=Path(args.output),
        manifest=manifest,
        profile=profile,
        sources=sources,
        statuses=statuses,
        project_name=args.project_name,
        cfx_file=args.cfx_file,
    )
    print(f"PDF generado: {Path(args.output).resolve()}")
    if failures:
        print("Aviso: PDF generado en modo no estricto con capturas pendientes:")
        for failure in failures:
            print(f"- {failure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
