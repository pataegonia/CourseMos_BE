# 추천/날씨 완전 통합 버전
from recommendations.places import get_place_recommendations
from recommendations.weather import get_weather

def recommend_with_weather(location, date, time):
    weather = get_weather(location, date, time)
    weather_text = f"{weather['summary']}, {weather['temp']}°C"
    return get_place_recommendations(location, date, time, weather_text=weather_text)
