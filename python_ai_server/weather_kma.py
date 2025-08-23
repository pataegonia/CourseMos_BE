# weather_kma.py
import os, math
from datetime import datetime
from typing import Optional, Tuple, Dict
import httpx
from fastapi import HTTPException

KMA_SERVICE_KEY = os.getenv("KMA_SERVICE_KEY")  # 반드시 '디코딩키(plain)' 값

# ---------- 격자 변환 ----------
def latlon_to_grid(lat: float, lon: float) -> Tuple[int, int]:
    RE = 6371.00877; GRID = 5.0
    SLAT1, SLAT2 = 30.0, 60.0; OLON, OLAT = 126.0, 38.0
    XO, YO = 43, 136
    import math as _m
    DEGRAD = _m.pi / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD; slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD;  olat = OLAT * DEGRAD
    sn = _m.log(_m.cos(slat1)/_m.cos(slat2)) / _m.log(
        _m.tan(_m.pi*0.25+slat2*0.5)/_m.tan(_m.pi*0.25+slat1*0.5)
    )
    sf = (_m.cos(slat1)*(_m.tan(_m.pi*0.25+slat1*0.5)**sn))/sn
    ro = re*sf/(_m.tan(_m.pi*0.25+olat*0.5)**sn)
    ra = re*sf/(_m.tan(_m.pi*0.25+(lat*DEGRAD)*0.5)**sn)
    theta = (lon*DEGRAD)-olon
    if theta > _m.pi: theta -= 2.0*_m.pi
    if theta < -_m.pi: theta += 2.0*_m.pi
    theta *= sn
    x = ra*_m.sin(theta)+XO+0.5
    y = ro - ra*_m.cos(theta)+YO+0.5
    return int(x), int(y)

BASE_TIMES = ["0200","0500","0800","1100","1400","1700","2000","2300"]

def pick_base_date_time(target_date: datetime) -> tuple[str, str]:
    now = datetime.now()
    if target_date.date() == now.date():
        now_hhmm = now.strftime("%H%M")
        base_time = BASE_TIMES[0]
        for bt in BASE_TIMES:
            if bt <= now_hhmm: base_time = bt
        return now.strftime("%Y%m%d"), base_time
    return target_date.strftime("%Y%m%d"), "1100"

def nearest_fcst_time(hhmm: str) -> str:
    hhmm = hhmm.replace(":", "")
    if len(hhmm) != 4 or not hhmm.isdigit(): return "1200"
    h = int(hhmm[:2]); m = int(hhmm[2:])
    if m >= 30: h = (h+1) % 24
    return f"{h:02d}00"

def map_condition(sky: Optional[str], pty: Optional[str]) -> str:
    if pty in {"1","5"}: return "비"
    if pty in {"2","6"}: return "비/눈"
    if pty in {"3","7"}: return "눈"
    if pty == "4":       return "소나기"
    if sky == "1": return "맑음"
    if sky == "3": return "구름많음"
    if sky == "4": return "흐림"
    return "알수없음"

# ---------- KMA 호출 (HTTP 강제) ----------
async def fetch_vilage_fcst(nx: int, ny: int, yyyymmdd: str, fcst_time: str) -> Dict[str, Optional[str]]:
    if not KMA_SERVICE_KEY:
        raise HTTPException(500, "KMA_SERVICE_KEY 미설정")

    base_date, base_time = pick_base_date_time(datetime.strptime(yyyymmdd, "%Y%m%d"))

    # ★ HTTPS 대신 HTTP로 강제 (TLS 이슈 회피)
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        "serviceKey": KMA_SERVICE_KEY,   # 디코딩키(plain) 그대로
        "pageNo": "1",
        "numOfRows": "300",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": str(nx),
        "ny": str(ny),
    }
    headers = {"User-Agent": "Mozilla/5.0"}  # 일부 환경에서 필요

    # HTTP는 TLS 협상 자체가 없으므로 SSL 에러가 날 수 없음
    try:
        async with httpx.AsyncClient(timeout=15, http2=False, trust_env=True) as c:
            r = await c.get(url, params=params, headers=headers)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        raise HTTPException(502, f"KMA 요청 실패(HTTP): {e}")

    # 응답 파싱/검증
    try:
        header = data["response"]["header"]
        code = header.get("resultCode")
        if code != "00":
            raise HTTPException(502, f"KMA 오류 코드: {code}, msg={header.get('resultMsg')}")
        items = data["response"]["body"]["items"]["item"]
    except KeyError:
        raise HTTPException(502, f"기상청 응답 파싱 실패: {data}")

    bucket = {"TMP": None, "SKY": None, "PTY": None}
    for it in items:
        if it.get("fcstDate") == yyyymmdd and it.get("fcstTime") == fcst_time:
            cat = it.get("category")
            if cat in bucket:
                bucket[cat] = it.get("fcstValue")
    return bucket
