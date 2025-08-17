import openai
import json
import os

def get_place_recommendations(location=None, date=None, time=None):
    # 테스트용: 인자가 없으면 example_input.json에서 로드
    if location is None or date is None or time is None:
        example_path = os.path.join(os.path.dirname(__file__), "examples", "example_input.json")
        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)
        location = example.get("location")
        date = example.get("date")
        time = example.get("time")

    prompt = f"""
    사용자의 현재 위치: {location}
    날짜: {date}
    현재 시간: {time}
    위 정보를 바탕으로 추천 장소 리스트와 각 장소별 설명을 아래와 같은 JSON 형식으로 반환해줘. 무슨동 이런게 아니라 구체적인 장소의 이름.
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
