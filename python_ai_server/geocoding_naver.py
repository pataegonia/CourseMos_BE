# geocoding_naver.py
import os, httpx
from fastapi import HTTPException
from dotenv import load_dotenv

# 루트 폴더 .env 로드
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

NAVER_API_KEY_ID = os.getenv("NAVER_MAPS_CLIENT_ID")
NAVER_API_KEY = os.getenv("NAVER_MAPS_CLIENT_SECRET")
print("NAVER_API_KEY_ID:", NAVER_API_KEY_ID)
print("NAVER_API_KEY:", NAVER_API_KEY) 
async def geocode_naver(address: str) -> tuple[float, float]:
    if not NAVER_API_KEY_ID or not NAVER_API_KEY:
        raise HTTPException(500, "NAVER MAPS API 키가 설정되지 않았습니다.")

    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_API_KEY_ID,
        "X-NCP-APIGW-API-KEY": NAVER_API_KEY,
    }
    params = {"query": address}

    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, headers=headers, params=params)

    if r.status_code != 200:
        raise HTTPException(r.status_code, f"Naver geocode error: {r.text}")

    data = r.json()
    addrs = data.get("addresses", [])
    if not addrs:
        raise HTTPException(404, "지오코딩 결과가 없습니다.")

    lon = float(addrs[0]["x"])
    lat = float(addrs[0]["y"])
    return lat, lon
