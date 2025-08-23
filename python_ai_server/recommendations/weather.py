import asyncio
from python_ai_server.weather_provider import fetch_simple_weather
from python_ai_server.geocoding_vworld import geocode_vworld

def get_weather(location: str, date: str, time: str) -> dict:
    """
    실제 외부 날씨 API에서 날씨 정보를 받아오는 함수
    location: 위치명 (예: '서울특별시 강남구 역삼동')
    date: 날짜 (예: '2025-08-23')
    time: 시간 (예: '13:00')
    Returns: {"summary": "맑음", "temp": 27, ...}
    """
    # 1. 위치명 → 위도/경도 변환 (브이월드 지오코딩)
    async def get_coords():
        return await geocode_vworld(location)
    lat, lon = asyncio.run(get_coords())

    # 2. 비동기 날씨 API 호출 (Open-Meteo 폴백 포함)
    async def fetch():
        return await fetch_simple_weather(lat, lon, date.replace("-", ""), time)
    weather = asyncio.run(fetch())

    return {
        "summary": weather.get("COND", "알수없음"),
        "temp": weather.get("TMP"),
        "location": location,
        "date": date,
        "time": time
    }
