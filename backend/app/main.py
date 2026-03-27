from fastapi import FastAPI, Depends
from app.config import settings
from app.middlewares.verification_token import verify_token
from fastapi.middleware.cors import CORSMiddleware

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
def protected(user=Depends(verify_token)):
    print("user:", user.user.id, user.user.email)
    return {
        "message": "You are authenticated",
        "user_id": user.user.id,
        "email": user.user.email,
    }





