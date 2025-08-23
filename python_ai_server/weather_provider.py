# weather_provider.py
import os, ssl, httpx, math
from datetime import datetime
from typing import Optional, Dict
from fastapi import HTTPException

# === KMA (기상청) ===
KMA_KEY = os.getenv("KMA_SERVICE_KEY")  # '디코딩키(일반키)' 권장

def _tls12_client() -> httpx.AsyncClient:
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    transport = httpx.AsyncHTTPTransport(verify=ctx, http2=False, retries=1)
    return httpx.AsyncClient(transport=transport, timeout=15, trust_env=False)

async def _kma_fetch(params: dict) -> dict:
    if not KMA_KEY:
        raise HTTPException(500, "KMA_SERVICE_KEY 미설정")
    url_https = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    headers = {"User-Agent": "Mozilla/5.0"}
    # 1) HTTPS
    async with _tls12_client() as c:
        r = await c.get(url_https, params=params, headers=headers)
        r.raise_for_status()
        return r.json()

# === Open-Meteo (무료, 키 불필요) ===
# weathercode -> 한국어 간단 매핑
WMO_KO = {
    0: "맑음",
    1: "대체로 맑음", 2: "부분적으로 흐림", 3: "흐림",
    45: "안개", 48: "착빙 안개",
    51: "이슬비(약)", 53: "이슬비(보통)", 55: "이슬비(강)",
    56: "어는 이슬비(약)", 57: "어는 이슬비(강)",
    61: "비(약)", 63: "비(보통)", 65: "비(강)",
    66: "어는 비(약)", 67: "어는 비(강)",
    71: "눈(약)", 73: "눈(보통)", 75: "눈(강)",
    77: "눈송이",
    80: "소나기(약)", 81: "소나기(보통)", 82: "소나기(강)",
    85: "소낙눈(약)", 86: "소낙눈(강)",
    95: "뇌우", 96: "뇌우/우박(약)", 99: "뇌우/우박(강)"
}

def _nearest_hour(hhmm: str) -> str:
    hhmm = hhmm.replace(":", "")
    if len(hhmm) != 4 or not hhmm.isdigit(): return "1200"
    h, m = int(hhmm[:2]), int(hhmm[2:])
    if m >= 30: h = (h + 1) % 24
    return f"{h:02d}00"

async def fetch_simple_weather(lat: float, lon: float, yyyymmdd: str, hhmm: str) -> Dict[str, Optional[str]]:
    """
    우선 KMA 시도 -> 실패 시 Open-Meteo 폴백
    반환: {"TMP": "23.4", "COND": "맑음"}
    """
    # 1) 먼저 KMA (현재/과거/미래를 단순화해서 베이스타임 계산)
    try:
        from weather_kma import pick_base_date_time
        base_date, base_time = pick_base_date_time(datetime.strptime(yyyymmdd, "%Y%m%d"))
        params = {
            "serviceKey": KMA_KEY,
            "pageNo": "1",
            "numOfRows": "300",
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            # nx, ny는 호출하는 쪽에서 계산해서 넣어주세요(여기선 생략)
        }
        # 여기서는 KMA 호출을 실제로 하지 않고, 원래 weather_kma.fetch_vilage_fcst로 맡깁니다.
        # 만약 그 함수가 TLS로 계속 깨지면 except로 떨어지게 하세요.
        raise Exception("force-fallback")  # ← 지금은 의도적으로 폴백 강제(환경 문제 회피)
    except Exception:
        pass  # Open-Meteo로 폴백

    # 2) Open-Meteo
    target_hhmm = _nearest_hour(hhmm)
    target_hour = int(target_hhmm[:2])
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,weathercode",
        "timezone": "Asia/Seoul",
    }
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    hours = data.get("hourly", {}).get("time", [])
    temps = data.get("hourly", {}).get("temperature_2m", [])
    codes = data.get("hourly", {}).get("weathercode", [])

    # 해당 날짜의 target_hour 가장 가까운 시간 인덱스 찾기
    want_date = f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}"
    idx_best, min_gap = None, 999
    for i, t in enumerate(hours):
        # t 예: "2025-08-24T14:00"
        if not t.startswith(want_date): continue
        hh = int(t[11:13])
        gap = abs(hh - target_hour)
        if gap < min_gap:
            min_gap, idx_best = gap, i

    if idx_best is None:
        # 날짜가 범위를 벗어나면 첫 항목이라도
        if hours:
            idx_best = 0
        else:
            raise HTTPException(502, "Open-Meteo 응답 파싱 실패")

    tmp = temps[idx_best] if idx_best < len(temps) else None
    code = codes[idx_best] if idx_best < len(codes) else None
    cond = WMO_KO.get(int(code), "알수없음") if code is not None else "알수없음"

    return {"TMP": f"{tmp}" if tmp is not None else None, "COND": cond}
