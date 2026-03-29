import logging

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import settings
from app.middlewares.verification_token import verify_token
from app.database.db import get_db
from app.database.models import User
from app.agents.research_agent import research_agent
from app.agents.critic_agent import critic_agent
from app.agents.writter_agent import witter_agent
from app.agents.formater import formater_agent
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"message":"Hello From Backend....Working Fine"}

# getting token from frontend
@app.get("/protected")
def protected(user=Depends(verify_token), db: Session = Depends(get_db)):
    supabase_user = user.user

    db_user = db.query(User).filter(User.email == supabase_user.email).first()
    if not db_user:
        db_user = User(
            email=supabase_user.email,
            google_id=supabase_user.id,
            name=supabase_user.user_metadata.get("full_name") if supabase_user.user_metadata else None,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return {
        "message": "You are authenticated",
        "user_id": str(db_user.id),
        "email": db_user.email,
    }


@app.post("/research")
async def run_research(body: dict, user=Depends(verify_token), db: Session = Depends(get_db)):
    supabase_user = user.user
    logger.info("run_research called topic=%s report_type=%s email=%s", body.get("topic"), body.get("report_type"), supabase_user.email)

    db_user = db.query(User).filter(User.email == supabase_user.email).first()
    if not db_user:
        logger.warning("run_research user not found email=%s", supabase_user.email)
        raise HTTPException(status_code=404, detail="User not found. Hit /protected first.")

    try:
        research_state = research_agent(state=body, db=db, user_id=db_user.id)
        logger.info("run_research research_agent completed results=%s", len(research_state.get("results", [])))

        critic_state = await critic_agent(research_state)
        logger.info("run_research critic_agent completed claims=%s", len(critic_state.get("verified_claims", [])))

        writer_state = await witter_agent(
            critic_state,
            db=db,
            research_query_id=critic_state.get("research_query_id"),
        )
        logger.info("run_research writter_agent completed sections=%s", len(writer_state.get("structured_content", {}).get("sections", [])))

        formatter_state = formater_agent(writer_state)
        logger.info("run_research formater_agent completed")

        return {
            "topic": critic_state.get("topic", body.get("topic")),
            "report_type": critic_state.get("report_type", body.get("report_type", "business")),
            "confidence_score": critic_state.get("confidence_score", 0),
            "research_results": research_state.get("results", []),
            "similar_results": research_state.get("similar_results", []),
            "verified_claims": critic_state.get("verified_claims", []),
            "structured_content": writer_state.get("structured_content", {}),
            "formatted_content": formatter_state.get("formatted_content", {}),
            "formatted_report": formatter_state.get("formatted_report", ""),
            "agent_trace": formatter_state.get("agent_trace", []),
        }
    except Exception as exc:
        logger.exception("run_research failed topic=%s", body.get("topic"))
        raise HTTPException(status_code=500, detail=f"Research pipeline failed: {exc}") from exc



