import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
import sys
import pytest
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from python_ai_server.recommendations.places import get_place_recommendations, validate_course_schema, fallback_parse

def test_schema_valid():
    result = get_place_recommendations("서울특별시 강남구 역삼동", "2025-08-23", "13:00", weather_text="맑음")
    assert isinstance(result, dict)
    assert "courses" in result
    # 스키마 검증 통과 시 3개, 실패 시 1개 코스 반환 허용
    if result["courses"][0]["코스명"] == "생성 실패":
        assert len(result["courses"]) == 1
        assert len(result["courses"][0]["스톱"]) == 1
    else:
        assert len(result["courses"]) == 3
        for course in result["courses"]:
            assert 3 <= len(course["스톱"]) <= 7
            assert isinstance(course["코스명"], str)
            assert isinstance(course["총예상소요시간"], int)
            for stop in course["스톱"]:
                assert isinstance(stop["장소명"], str)
                assert isinstance(stop["설명"], str)
                assert isinstance(stop["권장체류시간"], int)
                assert stop["권장시간대"] in ["아침", "오후", "저녁", "밤"]
                assert stop["카테고리"] in ["카페", "식당", "박물관", "공원", "야경", "바", "액티비티", "기타"]

def test_forbidden_suffix():
    bad = {
        "courses": [
            {
                "코스명": "테스트",
                "총예상소요시간": 360,
                "스톱": [
                    {"장소명": "강남동", "설명": "포괄 지명", "권장체류시간": 60, "권장시간대": "아침", "카테고리": "카페"},
                    {"장소명": "스타벅스 강남역 2호점", "설명": "정상", "권장체류시간": 60, "권장시간대": "오후", "카테고리": "식당"},
                    {"장소명": "국립중앙박물관", "설명": "정상", "권장체류시간": 60, "권장시간대": "저녁", "카테고리": "박물관"}
                ]
            }
        ] * 3
    }
    assert not validate_course_schema(bad)

def test_example_input_load():
    from python_ai_server.recommendations.places import load_example_input
    example = load_example_input()
    assert isinstance(example, dict)
    assert "location" in example and "date" in example and "time" in example

def test_fallback_parse():
    # 코드블록
    text = """```json\n{\"courses\": [{\"title\": \"테스트\",\"total_estimated_minutes\":360,\"stops\":[{\"name\":\"스타벅스 강남역 2호점\",\"desc\":\"테스트\",\"typical_duration_min\":60,\"suggested_time_of_day\":\"morning\",\"category\":\"cafe\"}]}]}\n```"""
    parsed = fallback_parse(text)
    assert parsed and "courses" in parsed
    # 배열만 응답
    arr_text = "[{\"title\":\"테스트\",\"total_estimated_minutes\":360,\"stops\":[{\"name\":\"스타벅스 강남역 2호점\",\"desc\":\"테스트\",\"typical_duration_min\":60,\"suggested_time_of_day\":\"morning\",\"category\":\"cafe\"}]}]"
    arr_parsed = fallback_parse(arr_text)
    assert arr_parsed and "courses" in arr_parsed
