
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from langchain_logic import get_place_recommendations
import os
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일을 명시적으로 로드
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)


app = FastAPI()

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    location: str
    date: str
    time: str

@app.post('/recommend')
async def recommend(body: RecommendRequest):
    result = get_place_recommendations(body.location, body.date, body.time)
    return JSONResponse(content=result)

# FastAPI 서버 실행: uvicorn app:app --host 0.0.0.0 --port 5000
