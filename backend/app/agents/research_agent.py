import logging

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr
from sqlalchemy.orm import Session
from tavily import TavilyClient
from app.config import settings
from app.database.models import ResearchQuery, Embedding

logger = logging.getLogger(__name__)

tavily = TavilyClient(settings().TAVILY_API_KEY)
gemini_api_key = settings().GEMINI_API_KEY
if not gemini_api_key:
    raise ValueError("Missing GEMINI_API_KEY in backend/.env.")

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=SecretStr(gemini_api_key)
)

SIMILARITY_TOP_K = 5


def research_agent(state: dict, db: Session, user_id) -> dict:
    query = state["topic"]
    report_type = state.get("report_type", "business")
    trace = [f"[Research] Starting search for: `{query}`"]
    logger.info("research_agent started topic=%s report_type=%s user_id=%s", query, report_type, user_id)

    try:
        logger.info("research_agent calling tavily.search")
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=8,
            include_raw_content=True,
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "content": r.get("content", "")[:2000],
                "score":   r.get("score", 0),
            })

        logger.info("research_agent search complete results=%s", len(results))
        trace.append(f"[Researcher] Found {len(results)} sources from web search")

        chunks = [f"{r['title']}\n\n{r['content']}" for r in results]
        logger.info("research_agent generating document embeddings chunk_count=%s", len(chunks))
        vectors = embeddings.embed_documents(
            chunks,
            task_type="retrieval_document",
            output_dimensionality=EMBEDDING_DIMENSIONS,
        )

        stored_ids = []
        for i, _ in enumerate(results):
            db_research = ResearchQuery(user_id=user_id, query=query)
            db.add(db_research)
            db.flush()

            db_embedding = Embedding(
                research_query_id=db_research.id,
                embedding=vectors[i],
            )
            db.add(db_embedding)
            stored_ids.append(db_research.id)

        db.commit()
        logger.info("research_agent stored embeddings count=%s", len(stored_ids))
        trace.append(f"[Researcher] Stored {len(results)} embeddings in DB")

        logger.info("research_agent generating query embedding")
        query_vector = embeddings.embed_query(
            query,
            task_type="retrieval_query",
            output_dimensionality=EMBEDDING_DIMENSIONS,
        )
        distance_expr = Embedding.embedding.cosine_distance(query_vector).label("distance")

        similar_rows = (
            db.query(Embedding, ResearchQuery, distance_expr)
            .join(ResearchQuery, Embedding.research_query_id == ResearchQuery.id)
            .filter(ResearchQuery.user_id == user_id)
            .order_by(distance_expr)
            .limit(SIMILARITY_TOP_K)
            .all()
        )

        similar_results = [
            {
                "query": research_query.query,
                "distance": float(distance),
            }
            for _, research_query, distance in similar_rows
        ]

        logger.info("research_agent similarity search complete matches=%s", len(similar_results))
        trace.append(f"[Researcher] Top {len(similar_results)} similar results via vector search")

        return {
            "topic":           query,
            "query":           query,
            "report_type":     report_type,
            "results":         results,
            "similar_results": similar_results,
            "research_query_id": stored_ids[0] if stored_ids else None,
            "trace":           trace,
            "agent_trace":     trace,
        }
    except Exception:
        logger.exception("research_agent failed topic=%s user_id=%s", query, user_id)
        raise
