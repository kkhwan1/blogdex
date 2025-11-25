# BlogDex 등급 조회 API 사용 안내

## 📖 개요

블로그 URL을 입력하면 BlogDex 등급(level)을 반환하는 FastAPI 서버입니다.

### 주요 기능
- ✅ 단일 URL 등급 조회
- ✅ 다수 URL 일괄 처리 (병렬)
- ✅ 최대 3개 동시 처리
- ✅ 실시간 크롤링 (캐시 없음)
- ✅ 쿠키 재사용 (구글 로그인 자동화)

---

## 🚀 서버 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일에 구글 계정 정보 설정:
```
GOOGLE_EMAIL=your-email@gmail.com
GOOGLE_PASSWORD=your-password
```

### 3. 서버 실행

#### 옵션 A: 로컬 전용 서버 (같은 PC 또는 LAN)
```bash
python start_server.py
```
- 서버 주소: `http://localhost:8000`
- API 문서: `http://localhost:8000/docs`

#### 옵션 B: 외부 접속 서버 (인터넷 어디서든) 🌐
```bash
python start_server_ngrok.py
```

**실행 결과**:
```
✅ ngrok 터널 생성 완료!
🌐 외부 접속 URL (HTTPS):
   https://abc123.ngrok-free.app

📚 API 문서:
   https://abc123.ngrok-free.app/docs
```

**ngrok 무료 플랜 특징**:
- ✅ 인터넷 어디서든 접속 가능
- ✅ HTTPS 자동 적용
- ✅ 분당 40개 연결 지원
- ✅ 무료 회원가입시 세션 무제한
- ⚠️ 재시작시 URL 변경됨

**선택사항: ngrok 인증 토큰 설정** (세션 시간 제한 해제)
1. https://dashboard.ngrok.com/get-started/your-authtoken 에서 무료 가입
2. `.env` 파일에 추가:
   ```
   NGROK_AUTH_TOKEN=your_token_here
   ```

---

## 📚 API 엔드포인트

### 1. 헬스 체크
```http
GET /health
```

**응답 예시**:
```json
{
  "status": "ok",
  "message": "BlogDex Grade API is running",
  "max_concurrent": 3
}
```

---

### 2. 단일 URL 등급 조회
```http
POST /api/blog/grade
Content-Type: application/json

{
  "url": "https://blog.naver.com/nyang2ne/224038751161"
}
```

**응답 예시** (성공):
```json
{
  "url": "https://blog.naver.com/nyang2ne/224038751161",
  "level": "엑스퍼트3",
  "success": true
}
```

**응답 예시** (실패):
```json
{
  "url": "https://blog.naver.com/invalid/000",
  "level": null,
  "success": false,
  "error": "등급 추출 실패"
}
```

**소요 시간**: 약 30-40초

---

### 3. 다수 URL 일괄 처리
```http
POST /api/blog/grades
Content-Type: application/json

{
  "urls": [
    "https://blog.naver.com/nyang2ne/224038751161",
    "https://blog.naver.com/test1/123"
  ]
}
```

**응답 예시**:
```json
[
  {
    "url": "https://blog.naver.com/nyang2ne/224038751161",
    "level": "엑스퍼트3",
    "success": true
  },
  {
    "url": "https://blog.naver.com/test1/123",
    "level": null,
    "success": false,
    "error": "등급 추출 실패"
  }
]
```

**병렬 처리**:
- 최대 3개 동시 처리
- 5개 URL: 30-40초 (3개) + 30-40초 (2개) = 약 60-80초

---

### 4. 현재 처리 상태 조회 (디버깅용)
```http
GET /api/status
```

**응답 예시**:
```json
{
  "processing_urls": [
    "https://blog.naver.com/nyang2ne/224038751161"
  ],
  "count": 1,
  "max_concurrent": 3
}
```

---

## 🧪 테스트

### Python 테스트 스크립트
```bash
python test_api.py
```

### cURL 테스트
```bash
# 단일 URL
curl -X POST http://localhost:8000/api/blog/grade \
  -H "Content-Type: application/json" \
  -d '{"url":"https://blog.naver.com/nyang2ne/224038751161"}'

# 다수 URL
curl -X POST http://localhost:8000/api/blog/grades \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://blog.naver.com/nyang2ne/224038751161","https://blog.naver.com/test/123"]}'
```

### PowerShell 테스트
```powershell
# 단일 URL
Invoke-RestMethod -Uri "http://localhost:8000/api/blog/grade" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"url":"https://blog.naver.com/nyang2ne/224038751161"}'

# 다수 URL
Invoke-RestMethod -Uri "http://localhost:8000/api/blog/grades" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"urls":["https://blog.naver.com/nyang2ne/224038751161","https://blog.naver.com/test/123"]}'
```

---

## 📊 등급 매핑

| BlogDex 등급 | Level |
|-------------|-------|
| 일반 | 스타터1 |
| 준최1 | 스타터2 |
| 준최2 | 스타터3 |
| 준최3 | 스타터4 |
| 준최4 | 스타터5 |
| 준최5 | 엘리트1 |
| 준최6 | 엘리트2 |
| 준최7 | 엘리트3 |
| 최적1 | 엘리트4 |
| 최적2 | 엘리트5 |
| 최적3 | 엑스퍼트1 |
| 최적4 | 엑스퍼트2 |
| 최적5 | 엑스퍼트3 |
| 최적2+ | 엑스퍼트3 |
| 최적6 | 엑스퍼트4 |
| 최적7 | 엑스퍼트5 |
| 최적1+ | 마스터1 |
| 최적3+ | 마스터3 |
| 최적4+ | 마스터4 |
| 최적5+ | 마스터5 |

---

## 🔧 주요 기능

### 1. 병렬 처리
- 최대 3개 브라우저 동시 실행
- Semaphore로 제한

### 2. 중복 방지
- 같은 URL 동시 요청 차단
- 처리 중인 URL은 409 에러 반환

### 3. 쿠키 재사용
- 구글 로그인 1회만 수행
- 이후 쿠키로 로그인 건너뛰기
- `cookies.pkl` 파일로 저장

### 4. 에러 처리
- 타임아웃, 요소 찾기 실패 등 자동 처리
- 실패 시 명확한 에러 메시지 반환

---

## 📁 파일 구조

```
블랜크(서버용)/
├── api_server.py          - FastAPI 서버
├── crawler.py             - 크롤링 로직
├── start_server.py        - 서버 실행
├── test_api.py            - 테스트 스크립트
├── blogdex_selenium_login.py  - 원본 스크립트 (참고용)
├── requirements.txt       - 의존성
├── .env                   - 환경변수 (구글 계정)
├── cookies.pkl           - 쿠키 캐시 (자동 생성)
└── API_사용안내.md        - 이 문서
```

---

## 🐛 문제 해결

### 구글 로그인 실패
- `.env` 파일에 정확한 계정 정보 확인
- 2FA 설정 시 앱 비밀번호 사용

### 크롤링 실패
- `cookies.pkl` 삭제 후 재시도
- Chrome 버전과 undetected-chromedriver 버전 호환성 확인

### 서버 포트 충돌
`start_server.py`에서 포트 변경:
```python
uvicorn.run(
    "api_server:app",
    host="0.0.0.0",
    port=8001,  # 포트 변경
    ...
)
```

---

## 📝 API 문서

서버 실행 후 자동 생성되는 Swagger UI:
- 주소: `http://localhost:8000/docs`
- 모든 엔드포인트를 브라우저에서 테스트 가능

---

## 💡 사용 예시

### Python에서 사용
```python
import requests

# 단일 URL
response = requests.post(
    "http://localhost:8000/api/blog/grade",
    json={"url": "https://blog.naver.com/nyang2ne/224038751161"}
)
result = response.json()
print(f"등급: {result['level']}")  # 엑스퍼트3

# 다수 URL
response = requests.post(
    "http://localhost:8000/api/blog/grades",
    json={"urls": [
        "https://blog.naver.com/nyang2ne/224038751161",
        "https://blog.naver.com/test/123"
    ]}
)
results = response.json()
for result in results:
    print(f"{result['url']}: {result['level']}")
```

### Node.js에서 사용
```javascript
const axios = require('axios');

// 단일 URL
const response = await axios.post('http://localhost:8000/api/blog/grade', {
  url: 'https://blog.naver.com/nyang2ne/224038751161'
});
console.log(`등급: ${response.data.level}`);  // 엑스퍼트3

// 다수 URL
const response = await axios.post('http://localhost:8000/api/blog/grades', {
  urls: [
    'https://blog.naver.com/nyang2ne/224038751161',
    'https://blog.naver.com/test/123'
  ]
});
response.data.forEach(result => {
  console.log(`${result.url}: ${result.level}`);
});
```

---

## ⚡ 성능

- **단일 요청**: 30-40초 (쿠키 사용 시)
- **첫 실행** (로그인): 약 2분
- **3개 동시**: 30-40초 (병렬 처리)
- **5개 동시**: 60-80초 (3개 + 2개)

---

## 📞 지원

문제 발생 시:
1. 서버 로그 확인
2. `/api/status`로 현재 상태 확인
3. `cookies.pkl` 삭제 후 재시도

