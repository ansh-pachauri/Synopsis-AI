from fastapi import FastAPI
from app.config import settings
app = FastAPI()

@app.get("/")
def health_check():
    return {"message":"Hello From Backend....Working Fine"}