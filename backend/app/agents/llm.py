from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from app.config import settings


def llm():
    api_key = settings().GEMINI_API_KEY
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in backend/.env.")

    return ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", api_key=SecretStr(api_key))
