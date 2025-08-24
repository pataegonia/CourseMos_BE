# CourseMos_BE

**완벽한 데이트코스 추천기 – AI와 함께하는 맞춤형 코스 추천 서비스**

![CourseMos Banner](https://user-images.githubusercontent.com/your-banner-image.png)

---

## 📝 프로젝트 소개

**CourseMos_BE**는 위치, 날짜, 시간, 날씨 정보를 기반으로 AI가 최적의 데이트 코스를 추천해주는 백엔드 서비스입니다.  
Firebase 인증, 사진 업로드, FastAPI 기반 AI 추천 서버, Google Places 연동 등 다양한 기능을 제공합니다.

---

## 🚀 주요 기능

- **AI 데이트코스 추천**  
  위치/날짜/시간/날씨 기반 맞춤형 코스 추천 (OpenAI GPT, FastAPI)
- **Firebase 인증 및 프로필 관리**  
  회원가입/로그인, 프로필 사진 업로드, 마이페이지
- **Google Places 사진 연동**  
  추천 장소별 대표 사진 자동 제공
- **Swagger API 문서 제공**  
  `/api-docs`에서 실시간 API 명세 확인
- **Python/Node.js 멀티 서버 구조**  
  Node.js(Express) + Python(FastAPI) 연동

---

## 🗂️ 폴더 구조

```
CourseMos_BE/
├── app.js                # Express 앱 진입점
├── server.js             # 서버 실행 파일
├── config/               # Firebase 등 환경설정
├── controllers/          # 라우트별 컨트롤러
├── middlewares/          # 인증 등 미들웨어
├── routes/               # API 라우터
├── python_ai_server/     # AI 추천/날씨 FastAPI 서버
├── data/, models/, ...   # 기타
├── tests/                # 테스트 코드
├── .env                  # 환경변수
└── README.md
```

---

## ⚙️ 기술 스택

- **Node.js** / **Express**  
- **Python** / **FastAPI**  
- **Firebase Admin SDK** (Auth, Firestore, Storage)
- **OpenAI GPT-4o** (Langchain)
- **Google Places API**
- **VWorld 지오코딩 API**
- **Swagger** (API 문서화)
- **Multer** (사진 업로드)
- **Joi** (입력 검증)
- **dotenv** (환경변수 관리)

---

## 🛠️ 설치 및 실행

### 1. 환경 변수 설정

- `.env` 파일을 프로젝트 루트에 생성하고 아래 항목을 채워주세요.

```
FIREBASE_WEB_API_KEY=...
FIREBASE_STORAGE_BUCKET=...
FIREBASE_DB_URL=...
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
OPENAI_API_KEY=...
GOOGLE_MAPS_API_KEY=...
VWORLD_API_KEY=...
KMA_SERVICE_KEY=...
```

### 2. 의존성 설치

#### Node.js 백엔드

```bash
npm install
```

#### Python AI 서버

```bash
cd python_ai_server
pip install -r requirements.txt
```

### 3. 서버 실행

#### Node.js 서버

```bash
npm run dev
# 또는
npm start
```

#### Python AI 서버

```bash
./run.sh
# 또는
cd python_ai_server
uvicorn app:app --host 0.0.0.0 --port 5000
```

---

## 📚 API 문서

- Swagger: [http://localhost:4000/api-docs](http://localhost:4000/api-docs)

### 예시: AI 추천 요청

```http
POST /api/ai/recommend
Content-Type: application/json

{
  "location": "서울 강남역",
  "date": "2025-08-17",
  "time": "15:00"
}
```

#### 응답 예시

```json
{
  "courses": [
    {
      "코스명": "강남 브런치 코스",
      "총예상소요시간": 360,
      "스톱": [
        {
          "장소명": "카페 드 파리",
          "설명": "분위기 좋은 브런치 카페",
          "권장체류시간": 60,
          "권장시간대": "아침",
          "카테고리": "카페",
          "photo_url": "https://..."
        }
        // ...
      ]
    }
    // ...
  ],
  "weather_text": "맑음, 27°C"
}
```

---

## 🤝 기여 방법

1. 이 저장소를 fork 합니다.
2. 새로운 브랜치에서 작업합니다. (`feature/awesome-feature`)
3. PR(Pull Request)을 생성합니다.

---

## 📄 라이선스

MIT License

---

## 💬 문의

- [이슈 등록](https://github.com/pataegonia/CourseMos_BE/issues)
- 이메일: your@email.com

---

> **CourseMos_BE** – AI와 함께하는 데이트코스의 모든 것!