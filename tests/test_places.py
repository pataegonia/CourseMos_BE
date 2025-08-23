import os
import sys
import pytest
import json
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from recommendations.places import get_place_recommendations, validate_course_schema, fallback_parse

def test_schema_valid():
    result = get_place_recommendations("서울특별시 강남구 역삼동", "2025-08-23", "13:00")
    assert isinstance(result, dict)
    assert "courses" in result
    assert len(result["courses"]) == 3
    for course in result["courses"]:
        assert 3 <= len(course["stops"]) <= 7
        assert isinstance(course["title"], str)
        assert isinstance(course["total_estimated_minutes"], int)
        for stop in course["stops"]:
            assert isinstance(stop["name"], str)
            assert isinstance(stop["desc"], str)
            assert isinstance(stop["typical_duration_min"], int)
            assert stop["suggested_time_of_day"] in ["아침", "오후", "저녁", "밤"]
            assert stop["category"] in ["카페", "식당", "박물관", "공원", "야경", "바", "액티비티", "기타"]

def test_forbidden_suffix():
    bad = {
        "courses": [
            {
                "title": "테스트",
                "total_estimated_minutes": 360,
                "stops": [
                    {"name": "강남동", "desc": "포괄 지명", "typical_duration_min": 60, "suggested_time_of_day": "morning", "category": "cafe"},
                    {"name": "스타벅스 강남역 2호점", "desc": "정상", "typical_duration_min": 60, "suggested_time_of_day": "afternoon", "category": "restaurant"},
                    {"name": "국립중앙박물관", "desc": "정상", "typical_duration_min": 60, "suggested_time_of_day": "evening", "category": "museum"}
                ]
            }
        ] * 3
    }
    assert not validate_course_schema(bad)

def test_example_input_load():
    from recommendations.places import load_example_input
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
