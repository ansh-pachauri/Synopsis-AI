import logging
from typing import Any

logger = logging.getLogger(__name__)


def _normalize_sections(sections: Any) -> list[dict]:
    if not isinstance(sections, list):
        return []

    normalized_sections: list[dict] = []
    for index, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            normalized_sections.append(
                {
                    "heading": f"Section {index}",
                    "content": str(section).strip(),
                    "citations": [],
                }
            )
            continue

        citations = section.get("citations", [])
        if not isinstance(citations, list):
            citations = [str(citations)]

        normalized_sections.append(
            {
                "heading": str(section.get("heading", f"Section {index}")).strip(),
                "content": str(section.get("content", "")).strip(),
                "citations": [str(citation).strip() for citation in citations if str(citation).strip()],
            }
        )

    return normalized_sections


def _normalize_takeaways(takeaways: Any) -> list[str]:
    if not isinstance(takeaways, list):
        return []

    return [str(takeaway).strip() for takeaway in takeaways if str(takeaway).strip()]


def _build_markdown_report(title: str, summary: str, sections: list[dict], key_takeaways: list[str]) -> str:
    lines: list[str] = [f"# {title}", ""]

    if summary:
        lines.extend(["## Summary", summary, ""])

    if key_takeaways:
        lines.append("## Key Takeaways")
        lines.extend([f"- {takeaway}" for takeaway in key_takeaways])
        lines.append("")

    for section in sections:
        lines.append(f"## {section['heading']}")
        lines.append(section["content"] or "No content provided.")

        if section["citations"]:
            lines.append("")
            lines.append("Citations:")
            lines.extend([f"- {citation}" for citation in section["citations"]])

        lines.append("")

    return "\n".join(lines).strip()


def formater_agent(writer_state: dict) -> dict:
    trace = list(writer_state.get("agent_trace", []))
    trace.append("[Formatter] Starting report formatting")
    logger.info("formater_agent started")

    try:
        structured_content = writer_state.get("structured_content", {})
        if not isinstance(structured_content, dict):
            structured_content = {}

        title = str(structured_content.get("title", "Research Report")).strip() or "Research Report"
        summary = str(structured_content.get("summary", "")).strip()
        sections = _normalize_sections(structured_content.get("sections", []))
        key_takeaways = _normalize_takeaways(structured_content.get("key_takeaways", []))

        formatted_report = _build_markdown_report(
            title=title,
            summary=summary,
            sections=sections,
            key_takeaways=key_takeaways,
        )

        logger.info("formater_agent completed title=%s sections=%s", title, len(sections))
        trace.append(f"[Formatter] Formatted report with {len(sections)} sections")

        return {
            "formatted_content": {
                "title": title,
                "summary": summary,
                "sections": sections,
                "key_takeaways": key_takeaways,
            },
            "formatted_report": formatted_report,
            "agent_trace": trace,
        }
    except Exception:
        logger.exception("formater_agent failed")
        raise
