# geocoding_vworld.py
import os, httpx
from fastapi import HTTPException
from dotenv import load_dotenv, find_dotenv

# app.py에서 이미 로드한다면 생략 가능
load_dotenv(find_dotenv())

VWORLD_KEY = os.getenv("VWORLD_API_KEY")
VWORLD_URL = "https://api.vworld.kr/req/address"

async def _call_vworld(address: str, addr_type: str) -> tuple[float, float]:
    params = {
        "service": "address",
        "request": "getCoord",
        "version": "2.0",
        "crs": "epsg:4326",   # WGS84로 반환
        "format": "json",
        "type": addr_type,    # "ROAD" or "PARCEL"
        "address": address,
        "refine": "true",
        "simple": "false",
        "key": VWORLD_KEY,
    }
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(VWORLD_URL, params=params)
    if r.status_code != 200:
        raise HTTPException(r.status_code, f"VWorld error: {r.text}")
    data = r.json()
    try:
        p = data["response"]["result"]["point"]  # x=lon, y=lat
        lon, lat = float(p["x"]), float(p["y"])
        return lat, lon
    except Exception:
        raise HTTPException(404, f"VWorld 결과 없음({addr_type}): {address}")

async def geocode_vworld(address: str) -> tuple[float, float]:
    """
    주소 -> (lat, lon) (WGS84)
    1) 도로명(ROAD) 시도, 2) 없으면 지번(PARCEL) 폴백
    """
    if not VWORLD_KEY:
        raise HTTPException(500, "VWORLD_API_KEY 미설정")
    try:
        return await _call_vworld(address, "ROAD")
    except HTTPException:
        return await _call_vworld(address, "PARCEL")
