import json
import re
import logging

from sqlalchemy.orm import Session
from app.agents.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage
from app.database.models import Report
from app.prompt_template.writter_prompt import writter_prompt

logger = logging.getLogger(__name__)


REPORT_STYLES = {
    "academic": "Use formal academic language. Include methodology notes. Structure: Abstract, Introduction, Key Findings, Analysis, Conclusion.",
    "business": "Use professional business language. Focus on actionable insights. Structure: Executive Summary, Market Overview, Key Insights, Risks, Recommendations.",
    "news":     "Use clear journalistic language. Lead with the most important point. Structure: Headline Summary, Background, Key Developments, Expert Views, What's Next.",
}


async def witter_agent(verified_claim_state:dict, db:Session, research_query_id) -> dict:
    topic = verified_claim_state.get("topic", "the given topic")
    report_type = verified_claim_state.get("report_type", "business")
    verified_claims = verified_claim_state.get("verified_claims", [])
    raw_sources = verified_claim_state.get("sources", [])

    report_style = REPORT_STYLES.get(report_type, REPORT_STYLES["business"])
    trace = list(verified_claim_state.get("agent_trace", []))
    trace.append("[Writter] Starting report generation based on verified claims")
    logger.info(
        "writter_agent started topic=%s report_type=%s claims=%s sources=%s research_query_id=%s",
        topic,
        report_type,
        len(verified_claims),
        len(raw_sources),
        research_query_id,
    )

    sources_text = "\n".join([
        f"- {r['url']}: {r['content'][:300]}"
        for r in raw_sources[:4]
    ]) 

    prompt = f"""Topic: {topic}
Report Type: {report_type}
Verified Claims:
{json.dumps(verified_claims, indent=2)}    
Report Style:{report_style}

Write a thorough research report. Each section should be 150-300 words.
Cite source URLs inline where relevant."""

    if sources_text:
        prompt = f"{prompt}\nSource Highlights:\n{sources_text}"

    try:
        trace.append("[Writter] Constructed prompt for LLM")
        logger.info("writter_agent invoking llm")
        response = await llm().ainvoke([
            SystemMessage(content=writter_prompt()),
            HumanMessage(content=prompt)
        ])

        content = response.content
        raw_text = (
            "".join(c if isinstance(c, str) else c.get("text", "") for c in content)
            if isinstance(content, list)
            else content
        ).strip()
        raw_text = re.sub(r"^```json|^```|```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            report = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.exception("writter_agent failed to parse llm response as JSON")
            report = {
                "title": f"Report on {topic}",
                "sections": [],
                "summary": "Report generation failed due to JSON parsing error.",
                "key_takeaways": []
            }

        if research_query_id:
            db_report = Report(
                research_query_id=research_query_id,
                title=report.get("title", ""),
                sections=json.dumps(report.get("sections", [])),
                summary=report.get("summary", ""),
                key_takeaways=json.dumps(report.get("key_takeaways", [])),
            )
            db.add(db_report)
            db.commit()
            logger.info("writter_agent stored report research_query_id=%s", research_query_id)
        else:
            logger.warning("writter_agent missing research_query_id, skipping report persistence")

        section_count = len(report.get("sections", []))
        logger.info("writter_agent completed title=%s sections=%s", report.get("title", topic), section_count)
        trace.append(f"[Writer] Generated {section_count} sections for '{report.get('title', topic)}'")

        return {
            "structured_content": report,
            "agent_trace":        trace,
        }
    except Exception:
        logger.exception("writter_agent failed topic=%s research_query_id=%s", topic, research_query_id)
        raise
     
