import json, re
import logging
from app.agents.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage
from app.prompt_template.critic_prompt import critic_prompt

logger = logging.getLogger(__name__)

async def critic_agent(search_results_state:dict) -> dict :
    search_results = search_results_state.get("results", [])
    topic = search_results_state.get("topic", search_results_state.get("query", "the given topic"))
    report_type = search_results_state.get("report_type", "business")

    trace = list(search_results_state.get("agent_trace", search_results_state.get("trace", [])))
    trace.append("[Critic] Starting fact-check on research results")
    logger.info("critic_agent started topic=%s source_count=%s report_type=%s", topic, len(search_results), report_type)

    try:
        source_context = "\n\n---\n\n".join([
            f"SOURCE: {r['url']}\n{r['content']}"
            for r in search_results[:5]
        ])

        prompt = f"""Topic: {topic}
Sources:
{source_context}

Extract the 8-12 most important factual claims from these sources about the topic.
Verify each claim against the provided sources."""

        trace.append("[Critic] Constructed prompt for LLM")
        logger.info("critic_agent invoking llm")
        response = await llm().ainvoke([
            SystemMessage(content=critic_prompt()),
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
            verified_facts = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.exception("critic_agent failed to parse llm response as JSON")
            verified_facts = [
                {"claim": r["content"][:200], "verified": False,
                 "confidence": 50, "source_url": r["url"], "reasoning": "Parse error fallback"}
                for r in search_results[:5]
            ]

        verified_count = sum(1 for f in verified_facts if f.get("verified"))
        avg_confidence = sum(f.get("confidence", 0) for f in verified_facts) / max(len(verified_facts), 1)

        logger.info(
            "critic_agent completed claims=%s verified=%s avg_confidence=%.2f",
            len(verified_facts),
            verified_count,
            avg_confidence,
        )
        trace.append(
            f"[Critic] Checked {len(verified_facts)} claims — "
            f"{verified_count} verified, avg confidence {avg_confidence:.0f}%"
        )

        return {
            "verified_claims": verified_facts,
            "confidence_score": avg_confidence,
            "topic": topic,
            "report_type": report_type,
            "sources": search_results,
            "research_query_id": search_results_state.get("research_query_id"),
            "agent_trace": trace,
        }
    except Exception:
        logger.exception("critic_agent failed topic=%s", topic)
        raise
