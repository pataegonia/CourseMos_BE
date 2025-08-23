import openai
import json
import os

def get_place_recommendations(location=None, date=None, time=None, weather_text: str = "날씨 정보 없음"):
    # 테스트용: 인자가 없으면 example_input.json에서 로드
    if location is None or date is None or time is None:
        example_path = os.path.join(os.path.dirname(__file__), "examples", "example_input.json")
        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)
        location = example.get("location")
        date = example.get("date")
        time = example.get("time")

    # location, date, time이 항상 값이 있으므로 아래에서 바로 prompt 정의
    prompt = f"""
    사용자의 현재 위치: {location}
    날짜: {date}
    현재 시간: {time}
    현지 날씨 : {weather_text}
    위 정보를 바탕으로 네이버 지도에서 검색하면 바로 나오는 구체적인 장소(예: 카페, 음식점, 공원, 박물관 등)만 5개 추천해줘.
    장소는 '용인시 서천동'처럼 지역명이나 동 이름이 아니라, 실제로 방문할 수 있는 하나의 공간(예: 스타벅스 강남역점, 한강공원, 국립중앙박물관 등)이어야 해.
    모든 답변은 반드시 한국어로 작성해줘.
    아래와 같은 JSON 형식으로만 반환해줘. (설명도 구체적으로)
    [
      {{"name": "장소명", "desc": "설명"}},
      ...
    ]
    """

    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("GPT 응답이 없습니다.")
        places = json.loads(content)
    except Exception as e:
        places = [{"name": "파싱 실패", "desc": str(e)}]

    return {"places": places}
