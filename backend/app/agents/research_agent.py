from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tavily import TavilyClient
from app.config import Settings

# initialize tavily client
tavily = TavilyClient(Settings.TAVILY_API_KEY)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    api_key=Settings.GEMINI_API_KEY
)

def research_agent(state:dict) -> dict:
    query = state["topic"]
    report_type = state.get("report_type","business")
    trace = [f"[Research] Starting search for: `{query}`"]

    # websrarch using talvy
    response = tavily.search( 
        query=query,
        search_depth="advanced",
        max_results=8,
        include_raw_content=True)
    
    results =[]
    for r in response.get("results", []):
        results.append({
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "content": r.get("content", "")[:2000],   # cap at 2k chars
            "score":   r.get("score", 0),
        })
 
    trace.append(f"[Researcher] Found {len(results)} sources from web search")

    # generate embedding of search output
    # flow =  content -> embedding -> store in vector db -> semantic search -> filter relevant chunks

    
    
    
