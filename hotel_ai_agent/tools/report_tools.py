from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _safe_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_json_report(report_data: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"revenue_report_{_safe_ts()}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
    logger.info("Reporte JSON guardado: %s", file_path)
    return file_path


def write_txt_report(report_data: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"revenue_report_{_safe_ts()}.txt"

    lines: list[str] = []
    lines.append("REPORTE DIARIO - REVENUE MANAGEMENT (MODO SUGERENCIA)")
    lines.append("=" * 70)
    lines.append(f"Fecha: {report_data.get('generated_at')}")
    lines.append("")

    lines.append("RESUMEN EJECUTIVO")
    lines.append("-" * 70)
    lines.append(str(report_data.get("executive_summary", "N/A")))
    lines.append("")

    lines.append("OCUPACIÓN PRÓXIMOS 7 DÍAS")
    lines.append("-" * 70)
    for row in report_data.get("occupancy", []):
        lines.append(
            f"{row.get('date')}: {row.get('occupied_rooms')}/{row.get('total_rooms')} "
            f"({row.get('occupancy_pct')}%)"
        )
    lines.append("")

    lines.append("SUGERENCIAS DE CAMBIO")
    lines.append("-" * 70)
    for suggestion in report_data.get("suggestions", []):
        lines.append(
            f"Hab {suggestion.get('room_name')} | {suggestion.get('target_date')} | "
            f"{suggestion.get('action')} | Actual {suggestion.get('current_price')} -> "
            f"Sugerido {suggestion.get('suggested_price')}"
        )
        lines.append(f"  Motivo: {suggestion.get('reason')}")
    lines.append("")

    lines.append("NOTA DE SEGURIDAD")
    lines.append("-" * 70)
    lines.append("NO se ejecutaron UPDATE de precios. Solo análisis y sugerencias.")

    with file_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("Reporte TXT guardado: %s", file_path)
    return file_path
