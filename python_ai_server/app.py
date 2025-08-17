from fastapi import FastAPI, Request
from langchain_logic import get_place_recommendations
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일을 명시적으로 로드
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

app = FastAPI()


@app.post('/recommend')
async def recommend(request: Request):
    data = await request.json()
    location = data.get('location')
    date = data.get('date')
    time = data.get('time')
    # LangChain 로직 호출
    result = get_place_recommendations(location, date, time)
    return JSONResponse(content=result)

# FastAPI 서버 실행: uvicorn app:app --host 0.0.0.0 --port 5000
