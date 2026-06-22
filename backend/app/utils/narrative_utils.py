from typing import Any


def render_section(title: str, bullets: list[str]) -> str:
    if not bullets:
        return f"## {title}\n\nNo significant findings.\n"
    lines = "\n".join(f"- {b}" for b in bullets)
    return f"## {title}\n\n{lines}\n"


def format_pct_change(value: float) -> str:
    direction = "increased" if value >= 0 else "decreased"
    return f"{direction} {abs(value):.1f}%"


def build_executive_paragraph(facts: list[str]) -> str:
    if not facts:
        return "Insufficient data to generate an executive summary."
    return " ".join(facts)
