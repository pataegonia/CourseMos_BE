

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from python_ai_server.recommendations.places import get_place_recommendations
import os
from dotenv import load_dotenv
from python_ai_server.geocoding_vworld import geocode_vworld
from python_ai_server.weather_kma import latlon_to_grid, fetch_vilage_fcst, map_condition, nearest_fcst_time
from python_ai_server.langchain_logic import get_place_recommendations
from python_ai_server.weather_provider import fetch_simple_weather
from python_ai_server.weather_kma import latlon_to_grid, nearest_fcst_time  # 격자/시간만 사용

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

@app.post("/recommend")
async def recommend(body: RecommendRequest):
    # 1) 주소 → VWorld
    lat, lon = await geocode_vworld(body.location)

    # 2) 격자 변환(지금은 Open-Meteo만 쓰더라도 lat/lon은 어차피 있음)
    nx, ny = latlon_to_grid(lat, lon)

    yyyymmdd = body.date.replace("-", "")
    fcst_time = nearest_fcst_time(body.time)

    # 3) 날씨(우선 Open-Meteo 폴백으로 확보)
    wx = await fetch_simple_weather(lat, lon, yyyymmdd, fcst_time)
    temperature_c = None
    tmp_value = wx.get("TMP")

    if tmp_value is not None:
        try:
            temperature_c = float(tmp_value)
        except (TypeError, ValueError):
            pass

    condition = wx.get("COND") or "알수없음"

    # 4) 날씨 텍스트
    if temperature_c is not None and condition != "알수없음":
        weather_text = f"{condition}, {temperature_c:.0f}°C"
    elif condition != "알수없음":
        weather_text = condition
    elif temperature_c is not None:
        weather_text = f"{temperature_c:.0f}°C"
    else:
        weather_text = "날씨 정보 없음"

    # 5) 추천 호출
    result = get_place_recommendations(body.location, body.date, body.time, weather_text=weather_text)  # Ensure weather_text is always passed
    return JSONResponse(content=result)
