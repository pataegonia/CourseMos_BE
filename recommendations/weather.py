import os
import requests

def get_weather(location: str, date: str, time: str) -> dict:
    """
    외부 날씨 API에서 날씨 정보를 받아오는 함수 (예시: KMA, OpenWeather 등)
    location: 위치명 (예: '서울특별시 강남구 역삼동')
    date: 날짜 (예: '2025-08-23')
    time: 시간 (예: '13:00')
    Returns: {"summary": "맑음", "temp": 27, ...}
    """
    # 실제 API 연동은 아래에 구현 (여기선 예시)
    # KMA_SERVICE_KEY = os.getenv("KMA_SERVICE_KEY")
    # resp = requests.get(...)
    # return resp.json()
    return {
        "summary": "맑음",
        "temp": 27,
        "location": location,
        "date": date,
        "time": time
    }
