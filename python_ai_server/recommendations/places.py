# 구조 보정 함수: 코스/스톱 개수 및 필수 필드 강제
def fix_schema_structure(data):
    courses = data.get("courses", [])
    while len(courses) < 3:
        courses.append({
            "코스명": f"기본 코스 {len(courses)+1}",
            "총예상소요시간": 360,
            "스톱": []
        })
    data["courses"] = courses[:3]
    for course in data["courses"]:
        stops = course.get("스톱", [])
        while len(stops) < 3:
            stops.append({
                "장소명": f"기본 장소 {len(stops)+1}",
                "설명": "기본 설명",
                "권장체류시간": 60,
                "권장시간대": "오후",
                "카테고리": "기타",
                "photo_url": ""
            })
        course["스톱"] = stops[:7]
    return data
# 영문→한글 필드명 매핑 및 후처리 변환 함수
FIELD_MAP = {
    "title": "코스명",
    "total_estimated_minutes": "총예상소요시간",
    "stops": "스톱",
    "name": "장소명",
    "desc": "설명",
    "typical_duration_min": "권장체류시간",
    "suggested_time_of_day": "권장시간대",
    "category": "카테고리"
}

def convert_fields_to_korean(data):
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            new_key = FIELD_MAP.get(k, k)
            if new_key is None:
                continue  # None 키는 무시
            out[str(new_key)] = convert_fields_to_korean(v)
        return out
    elif isinstance(data, list):
        return [convert_fields_to_korean(item) for item in data]
    return data
import os
import requests
# Google Places API를 활용한 장소 사진 가져오기
def get_photo_url(place_name: str, api_key: str) -> str:
    """
    Google Places API를 통해 장소명으로 대표 사진 URL을 반환합니다.
    - place_name: 장소명(예: '카페 드 파리')
    - api_key: 구글 API 키
    """
    search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": place_name,
        "inputtype": "textquery",
        "fields": "photos,place_id",
        "key": api_key
    }
    try:
        resp = requests.get(search_url, params=params, timeout=3)
        data = resp.json()
        candidates = data.get("candidates")
        if candidates and isinstance(candidates, list) and len(candidates) > 0:
            photos = candidates[0].get("photos")
            if photos and isinstance(photos, list) and len(photos) > 0:
                photo_ref = photos[0].get("photo_reference")
                if photo_ref:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}"
                    return photo_url
    except Exception as e:
        print(f"[사진 가져오기 실패] {place_name}: {e}")
    return ""
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
                    "required": ["코스명", "총예상소요시간", "스톱"],
                    "properties": {
                        "코스명": {"type": "string"},
                        "총예상소요시간": {"type": "integer", "minimum": 120, "maximum": 900},
                        "스톱": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 7,
                            "items": {
                                "type": "object",
                                "required": ["장소명", "설명", "권장체류시간", "권장시간대", "카테고리"],
                                "properties": {
                                    "장소명": {"type": "string"},
                                    "설명": {"type": "string"},
                                    "권장체류시간": {"type": "integer", "minimum": 15, "maximum": 240},
                                    "권장시간대": {
                                        "type": "string",
                                        "enum": ["아침", "오후", "저녁", "밤"]
                                    },
                                    "카테고리": {
                                        "type": "string",
                                        "enum": ["카페", "식당", "박물관", "공원", "야경", "바", "액티비티", "기타"]
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
CATEGORY_ENUM = ["카페", "식당", "박물관", "공원", "야경", "바", "액티비티", "기타"]
TIME_ENUM = ["아침", "오후", "저녁", "밤"]

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
        stops = course.get("스톱")
        if not isinstance(stops, list) or not (3 <= len(stops) <= 7):
            return False
        categories = set()
        total_stop_minutes = 0
        for stop in stops:
            if not isinstance(stop, dict):
                return False
            for key in ["장소명", "설명", "권장체류시간", "권장시간대", "카테고리"]:
                if key not in stop:
                    return False
            if not isinstance(stop["장소명"], str) or not stop["장소명"]:
                return False
            if not isinstance(stop["설명"], str) or not stop["설명"]:
                return False
            if not isinstance(stop["권장체류시간"], int) or not (15 <= stop["권장체류시간"] <= 240):
                return False
            if stop["권장시간대"] not in TIME_ENUM:
                return False
            if stop["카테고리"] not in CATEGORY_ENUM:
                return False
            for suffix in FORBIDDEN_SUFFIXES:
                if stop["장소명"].strip().endswith(suffix):
                    return False
            categories.add(stop["카테고리"])
            total_stop_minutes += stop["권장체류시간"]
        if len(categories) < 2:
            return False
        est = course.get("총예상소요시간")
        if not isinstance(est, int) or not (120 <= est <= 900):
            return False
        if not (total_stop_minutes + 30 <= est <= total_stop_minutes + 120):
            return False
        if not isinstance(course.get("코스명"), str) or not course["코스명"]:
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

def get_place_recommendations(location: Optional[str] = None, date: Optional[str] = None, time_str: Optional[str] = None, weather_text: Optional[str] = None) -> Dict[str, Any]:
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
        "너는 반드시 한글로만 답한다. 아래 스키마와 구조에 '정확히' 맞는 JSON만 반환한다. 모든 필드명, 카테고리, 시간대 값은 반드시 한글로 작성한다.\n"
        "필드명: 코스명, 총예상소요시간, 스톱, 장소명, 설명, 권장체류시간, 권장시간대, 카테고리\n"
        "카테고리 값: 카페, 식당, 박물관, 공원, 야경, 바, 액티비티, 기타\n"
        "시간대 값: 아침, 오후, 저녁, 밤\n"
        "반드시 3개 코스, 각 코스는 3~7개 스톱으로 구성되어야 하며, 모든 필드명과 값은 한글로 작성되어야 한다.\n"
        "예시 JSON과 완전히 동일한 구조, 필드명, 값, 배열 개수를 따라야 한다.\n"
        "예시 JSON: {\n  \"courses\": [\n    {\n      \"코스명\": \"강남 브런치 코스\",\n      \"총예상소요시간\": 360,\n      \"스톱\": [\n        {\n          \"장소명\": \"카페 드 파리\",\n          \"설명\": \"분위기 좋은 브런치 카페\",\n          \"권장체류시간\": 60,\n          \"권장시간대\": \"아침\",\n          \"카테고리\": \"카페\"\n        },\n        {\n          \"장소명\": \"봉은사\",\n          \"설명\": \"조용한 분위기의 전통 사찰\",\n          \"권장체류시간\": 90,\n          \"권장시간대\": \"오후\",\n          \"카테고리\": \"기타\"\n        },\n        {\n          \"장소명\": \"선릉과 정릉\",\n          \"설명\": \"조용한 산책로와 역사적인 유적지\",\n          \"권장체류시간\": 90,\n          \"권장시간대\": \"오후\",\n          \"카테고리\": \"공원\"\n        }\n      ]\n    },\n    {\n      \"코스명\": \"강남 저녁 야경 코스\",\n      \"총예상소요시간\": 420,\n      \"스톱\": [\n        {\n          \"장소명\": \"서울 스카이\",\n          \"설명\": \"서울의 전경을 감상할 수 있는 전망대\",\n          \"권장체류시간\": 120,\n          \"권장시간대\": \"저녁\",\n          \"카테고리\": \"야경\"\n        },\n        {\n          \"장소명\": \"한남동 소고기 전문점\",\n          \"설명\": \"고급스러운 소고기를 즐길 수 있는 식당\",\n          \"권장체류시간\": 90,\n          \"권장시간대\": \"저녁\",\n          \"카테고리\": \"식당\"\n        },\n        {\n          \"장소명\": \"이태원 바\",\n          \"설명\": \"다양한 칵테일을 즐길 수 있는 바\",\n          \"권장체류시간\": 90,\n          \"권장시간대\": \"저녁\",\n          \"카테고리\": \"바\"\n        }\n      ]\n    },\n    {\n      \"코스명\": \"강남 밤 문화 탐방 코스\",\n      \"총예상소요시간\": 360,\n      \"스톱\": [\n        {\n          \"장소명\": \"홍대 클럽\",\n          \"설명\": \"젊은이들이 모이는 클럽\",\n          \"권장체류시간\": 120,\n          \"권장시간대\": \"밤\",\n          \"카테고리\": \"액티비티\"\n        },\n        {\n          \"장소명\": \"이태원 펍\",\n          \"설명\": \"다양한 맥주를 즐길 수 있는 펍\",\n          \"권장체류시간\": 90,\n          \"권장시간대\": \"밤\",\n          \"카테고리\": \"바\"\n        },\n        {\n          \"장소명\": \"청담동 디저트 카페\",\n          \"설명\": \"고급 디저트를 즐길 수 있는 카페\",\n          \"권장체류시간\": 60,\n          \"권장시간대\": \"밤\",\n          \"카테고리\": \"카페\"\n        }\n      ]\n    }\n  ]\n}\n"
        "예시와 구조, 필드명, 값, 배열 개수가 하나라도 다르면 반드시 실패.\n"
        "비/눈/악천후 등 날씨에 따라 실내/실외/야경/카페/박물관 등 코스 구성을 다르게 추천.\n"
        "오직 지정된 JSON 스키마와 구조에 '정확히' 맞춰 출력한다(여분의 텍스트/주석/설명 금지)."
    )
    user_prompt = f"""
    사용자의 현재 위치: {location}
    날짜: {date}
    현재 시간: {time_str}
    현지 날씨: {weather_text if weather_text else '날씨 정보 없음'}

    요청:
    - 반드시 3개 코스, 각 코스는 3~7개 스톱으로 구성
    - 모든 필드명과 값은 한글로 작성
    - 각 코스/스톱의 구조, 필드명, 값, 배열 개수는 예시 JSON과 완전히 동일하게 작성
    - 각 스톱은 반드시 아래 한글 필드명만 사용: 장소명, 설명, 권장체류시간, 권장시간대, 카테고리
    - 행정동/상권/거리/타운/프라자 등 포괄 지명 금지, 지점명(브랜치명) 명확히
    - 카테고리 값은 반드시: 카페, 식당, 박물관, 공원, 야경, 바, 액티비티, 기타 중 하나
    - 권장시간대 값은 반드시: 아침, 오후, 저녁, 밤 중 하나
    - 카테고리 다양성 및 동선 합리성(이동 과도하지 않게) 고려
    - 현재 시간대/요일에 어울리는 스팟 우선
    - 출력은 제공된 JSON 스키마에 '정확히' 맞춰 반환
    - 예시 JSON을 참고해 반드시 동일한 구조와 한글 필드명/값으로 반환
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    max_retries = 3
    backoff = [0.8, 1.6, 3.2]
    last_error = None
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
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
            # 영문/한글 필드명 모두 변환
            result_kor = convert_fields_to_korean(result) if result else None
            # 구조 보정 없이, 스키마 검증만 통과한 경우만 반환
            if isinstance(result_kor, dict) and validate_course_schema(result_kor):
                for course in result_kor.get("courses", []):
                    for stop in course.get("스톱", []):
                        place_name = stop.get("장소명") or stop.get("name")
                        stop["photo_url"] = get_photo_url(place_name, api_key) if place_name else ""
                result_kor["weather_text"] = weather_text
                return result_kor
            else:
                last_error = f"스키마 미스매치: {content[:200]}"
        except Exception as e:
            last_error = str(e)
        if attempt < max_retries - 1:
            time.sleep(backoff[attempt])
    # 최종 실패 시 (사진 없음)
    return {
        "courses": [
            {
                "코스명": "생성 실패",
                "총예상소요시간": 0,
                "스톱": [
                    {
                        "장소명": "파싱 실패",
                        "설명": str(last_error),
                        "권장체류시간": 0,
                        "권장시간대": "아침",
                        "카테고리": "기타",
                        "photo_url": ""
                    }
                ]
            }
        ],
        "weather_text": weather_text
    }

# TODO: Naver/Kakao/Google Places API로 지점명/영업시간/좌표 검증 및 이동시간 추정.
# TODO: 좌표 기반 반경 및 영업 중 필터, 시간대별 가중치.
# TODO: 로깅/샘플링 및 품질 지표 대시보드.
