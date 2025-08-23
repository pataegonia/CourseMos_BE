# 추천/날씨 통합
from python_ai_server.recommendations.places import get_place_recommendations
from python_ai_server.recommendations.weather import get_weather

def recommend_with_weather(location, date, time):
    weather = get_weather(location, date, time)
    weather_text = f"{weather['summary']}, {weather['temp']}°C"
    return get_place_recommendations(location, date, time, weather_text=weather_text)
