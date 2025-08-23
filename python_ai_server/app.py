
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from recommendations.places import get_place_recommendations
import os
from dotenv import load_dotenv
from geocoding_naver import geocode_naver
from weather_kma import latlon_to_grid, fetch_vilage_fcst, map_condition, nearest_fcst_time


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
    # 1) 주소 -> 위경도(네이버)
    lat, lon = await geocode_naver(body.location)

    # 2) 위경도 -> 기상청 격자
    nx, ny = latlon_to_grid(lat, lon)

    # 3) 날짜/시간 가공
    yyyymmdd = body.date.replace("-", "")
    fcst_time = nearest_fcst_time(body.time)  # 요청 시간과 가장 가까운 정각

    # 4) 기상청 단기예보 호출
    fcst = await fetch_vilage_fcst(nx, ny, yyyymmdd, fcst_time)
    condition = map_condition(fcst.get("SKY"), fcst.get("PTY"))
    temperature_c = None
    tmp_value = fcst.get("TMP")
    if tmp_value is not None:
        try:
            temperature_c = float(tmp_value)
        except (TypeError, ValueError):
            pass

    # 5) OpenAI 프롬프트용 날씨 텍스트
    if temperature_c is not None and condition != "알수없음":
        weather_text = f"{condition}, {temperature_c:.0f}°C"
    elif condition != "알수없음":
        weather_text = condition
    elif temperature_c is not None:
        weather_text = f"{temperature_c:.0f}°C"
    else:
        weather_text = "날씨 정보 없음"

    # 6) 장소 추천 호출(프롬프트에 날씨 포함)
    result = get_place_recommendations(
        body.location, body.date, body.time, weather_text=weather_text
    )
    return JSONResponse(content=result)


# FastAPI 서버 실행: uvicorn app:app --host 0.0.0.0 --port 5000
