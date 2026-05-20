from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config.settings import settings


def generate_combined_report_pdf(report_id: int, context: dict[str, Any]) -> str:
    from weasyprint import HTML

    settings.report_output_dir.mkdir(parents=True, exist_ok=True)
    file_path = settings.report_output_dir / f"combined_report_{report_id}.pdf"
    html = _render_template("combined_report.html", context)

    HTML(string=html, base_url=str(Path.cwd())).write_pdf(str(file_path))

    return str(file_path)


def _render_template(template_name: str, context: dict[str, Any]) -> str:
    environment = Environment(
        loader=FileSystemLoader(str(settings.template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    environment.filters["currency"] = _format_currency
    environment.globals["generated_now"] = datetime.utcnow

    return environment.get_template(template_name).render(**context)


def _format_currency(value: float | int | None) -> str:
    return f"${float(value or 0):,.0f}"
