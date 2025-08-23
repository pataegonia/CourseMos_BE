import os
import json
import re
import time
from typing import Any, Dict, List, Optional
from openai import OpenAI

JSON_SCHEMA = {
    "name": "itinerary_schema",
    "schema": {
        "type": "object",
        "properties": {
            "courses": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "required": ["title", "total_estimated_minutes", "stops"],
                    "properties": {
                        "title": {"type": "string"},
                        "total_estimated_minutes": {"type": "integer", "minimum": 120, "maximum": 900},
                        "stops": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 7,
                            "items": {
                                "type": "object",
                                "required": ["name", "desc", "typical_duration_min", "suggested_time_of_day", "category"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "desc": {"type": "string"},
                                    "typical_duration_min": {"type": "integer", "minimum": 15, "maximum": 240},
                                    "suggested_time_of_day": {
                                        "type": "string",
                                        "enum": ["morning", "afternoon", "evening", "night"]
                                    },
                                    "category": {
                                        "type": "string",
                                        "enum": ["cafe", "restaurant", "museum", "park", "view", "bar", "activity", "other"]
                                    }
                                },
                                "additionalProperties": False
                            }
                        }
                    },
                    "additionalProperties": False
                }
            }
        },
        "required": ["courses"],
        "additionalProperties": False
    },
    "strict": True
}

# 금지 접미사(포괄 지명)
FORBIDDEN_SUFFIXES = ["동", "읍", "면", "리", "거리", "타운", "스퀘어", "프라자"]
CATEGORY_ENUM = ["cafe", "restaurant", "museum", "park", "view", "bar", "activity", "other"]
TIME_ENUM = ["morning", "afternoon", "evening", "night"]

# 품질 검증 함수

def validate_course_schema(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
    courses = data.get("courses")
    if not isinstance(courses, list) or len(courses) != 3:
        return False
    for course in courses:
        if not isinstance(course, dict):
            return False
        stops = course.get("stops")
        if not isinstance(stops, list) or not (3 <= len(stops) <= 7):
            return False
        categories = set()
        total_stop_minutes = 0
        for stop in stops:
            if not isinstance(stop, dict):
                return False
            # 필수 필드 검사
            for key in ["name", "desc", "typical_duration_min", "suggested_time_of_day", "category"]:
                if key not in stop:
                    return False
            # 타입/범위 검사
            if not isinstance(stop["name"], str) or not stop["name"]:
                return False
            if not isinstance(stop["desc"], str) or not stop["desc"]:
                return False
            if not isinstance(stop["typical_duration_min"], int) or not (15 <= stop["typical_duration_min"] <= 240):
                return False
            if stop["suggested_time_of_day"] not in TIME_ENUM:
                return False
            if stop["category"] not in CATEGORY_ENUM:
                return False
            # 금지 접미사 검사
            for suffix in FORBIDDEN_SUFFIXES:
                if stop["name"].strip().endswith(suffix):
                    return False
            categories.add(stop["category"])
            total_stop_minutes += stop["typical_duration_min"]
        # 카테고리 다양성(최소 2종)
        if len(categories) < 2:
            return False
        # 총 소요 시간 합리성(±30~120분)
        est = course.get("total_estimated_minutes")
        if not isinstance(est, int) or not (120 <= est <= 900):
            return False
        if not (total_stop_minutes + 30 <= est <= total_stop_minutes + 120):
            return False
        if not isinstance(course.get("title"), str) or not course["title"]:
            return False
    return True

# 폴백 파서: 코드블록/본문/배열 추출

def fallback_parse(text: str) -> Optional[Dict[str, Any]]:
    # 코드블록 내 JSON 추출
    codeblock = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if codeblock:
        text = codeblock.group(1)
    # 배열만 응답 시
    if text.strip().startswith("["):
        try:
            arr = json.loads(text)
            return {"courses": arr}
        except Exception:
            pass
    # 본문 {...} 또는 [...] 추출
    obj_match = re.search(r"({[\s\S]+})", text)
    arr_match = re.search(r"(\[[\s\S]+\])", text)
    try:
        if obj_match:
            return json.loads(obj_match.group(1))
        elif arr_match:
            arr = json.loads(arr_match.group(1))
            return {"courses": arr}
    except Exception:
        pass
    return None

# 입력 폴백 로딩

def load_example_input() -> Dict[str, str]:
    example_path = os.path.join(os.path.dirname(__file__), "..", "examples", "example_input.json")
    with open(example_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 메인 함수

def get_place_recommendations(location: Optional[str] = None, date: Optional[str] = None, time_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns:
      {
        "courses": [ ... ]
      }
    """
    if location is None or date is None or time_str is None:
        example = load_example_input()
        location = example.get("location")
        date = example.get("date")
        time_str = example.get("time")

    system_prompt = (
        "너는 한국어로만 답한다. 사용자의 현재 위치/날짜/시간을 반영해 '하루 안에 소화 가능한' 3개의 데이트 코스를 설계하는 로컬 가이드다. "
        "각 코스는 3~7개의 '구체적 지점명'으로 구성하며, 네이버 지도에서 바로 검색 가능해야 한다. "
        "행정동/상권/거리/타운/프라자 등 포괄 지명은 금지. 프랜차이즈는 지점명까지 명확히(예: '스타벅스 강남역 2호점'). "
        "같은 카테고리로 몰리지 않게 다양성(카페/식당/산책/전시/야경/바/액티비티 등)을 고려한다. "
        "현재 시간대와 요일을 감안해 영업 가능성과 분위기를 맞춘다(아침-브런치, 저녁-야경/바 등). "
        "각 코스의 총 소요 시간은 대략 반나절~하루(6~12시간)를 권장하되 스키마 범위 내에서 수치화한다. "
        "오직 지정된 JSON 스키마에 '정확히' 맞춰 출력한다(여분의 텍스트/주석/설명 금지)."
    )
    user_prompt = f"""
    사용자의 현재 위치: {location}
    날짜: {date}
    현재 시간: {time_str}

    요청:
    - 하루에 가능한 3개 코스를 설계
    - 각 코스는 3~7개의 '구체적 지점명' 스톱으로 구성
    - 각 스톱은 {"name","desc","typical_duration_min","suggested_time_of_day","category"} 필수
    - 행정동/상권/거리/타운/프라자 등 포괄 지명 금지, 지점명(브랜치명) 명확히
    - 카테고리 다양성 및 동선 합리성(이동 과도하지 않게) 고려
    - 현재 시간대/요일에 어울리는 스팟 우선
    - 출력은 제공된 JSON 스키마에 '정확히' 맞춰 반환
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    max_retries = 3
    backoff = [0.8, 1.6, 3.2]
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                timeout=30
            )
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("GPT 응답이 없습니다.")
            # 1차 파싱
            try:
                result = json.loads(content)
            except Exception:
                result = fallback_parse(content)
            if result and validate_course_schema(result):
                return result
            else:
                last_error = f"스키마 미스매치: {content[:200]}"
        except Exception as e:
            last_error = str(e)
        if attempt < max_retries - 1:
            time.sleep(backoff[attempt])
    # 최종 실패 시
    return {
        "courses": [
            {
                "title": "생성 실패",
                "total_estimated_minutes": 0,
                "stops": [
                    {
                        "name": "파싱 실패",
                        "desc": str(last_error),
                        "typical_duration_min": 0,
                        "suggested_time_of_day": "morning",
                        "category": "other"
                    }
                ]
            }
        ]
    }

# TODO: Naver/Kakao/Google Places API로 지점명/영업시간/좌표 검증 및 이동시간 추정.
# TODO: 좌표 기반 반경 및 영업 중 필터, 시간대별 가중치.
# TODO: 로깅/샘플링 및 품질 지표 대시보드.
