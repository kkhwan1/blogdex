# 블덱스 블로그 등급 스크래퍼 + API 서버

블덱스(blogdex.space)에서 블로그 등급 정보를 자동으로 수집하는 스크래퍼 및 FastAPI 서버입니다.

## ✨ 주요 기능

### 스크래퍼
- ✅ 구글 계정으로 로그인 (수동 2단계 인증)
- ✅ 블로그 ID별 등급 정보 자동 추출
- ✅ JSON 형식으로 결과 저장
- ✅ 세션 쿠키 저장/재사용 (재로그인 불필요)
- ✅ 로깅 시스템 및 에러 처리
- ✅ 환경변수 사용 (보안 강화)

### FastAPI 서버 ⭐ NEW
- ✅ REST API로 블로그 등급 조회
- ✅ 단일/다수 URL 일괄 처리
- ✅ 최대 3개 동시 병렬 처리
- ✅ 실시간 크롤링 (항상 최신 데이터)
- ✅ 쿠키 자동 관리
- ✅ Swagger UI 자동 문서화

## 📦 설치

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정
# .env 파일을 생성하고 구글 계정 정보를 입력하세요
# 예시:
# GOOGLE_EMAIL=your-email@gmail.com
# GOOGLE_PASSWORD=your-password
```

## 🚀 사용 방법

### ⭐ 방법 1: FastAPI 서버 (추천)

#### 1️⃣ 로컬 전용 서버 (같은 PC 또는 LAN 내)

**서버 시작**:
```bash
python start_server.py
```

**접속**:
- 같은 PC: `http://localhost:8000/docs`
- 같은 네트워크: `http://192.168.x.x:8000/docs`

#### 2️⃣ 외부 접속 서버 (인터넷 어디서든) 🌐

**서버 시작**:
```bash
# 1. ngrok 설치 (처음 한번만)
pip install -r requirements.txt

# 2. (선택) ngrok 무료 회원가입 후 토큰 설정
# https://dashboard.ngrok.com/get-started/your-authtoken
# .env 파일에 추가: NGROK_AUTH_TOKEN=your_token_here

# 3. 서버 시작
python start_server_ngrok.py
```

**결과**:
```
✅ ngrok 터널 생성 완료!
🌐 외부 접속 URL (HTTPS):
   https://abc123.ngrok-free.app

📚 API 문서:
   https://abc123.ngrok-free.app/docs
```

**특징**:
- ✅ 인터넷 어디서든 접속 가능
- ✅ HTTPS 자동 적용 (보안)
- ✅ 무료 플랜 제공 (세션 무제한*)
- ⚠️ 재시작시 URL 변경됨

\* 무료 회원가입 + 토큰 설정시

---

**API 사용 예시**:
```bash
# 단일 URL 조회
curl -X POST https://your-ngrok-url.ngrok-free.app/api/blog/grade \
  -H "Content-Type: application/json" \
  -d '{"url":"https://blog.naver.com/nyang2ne/224038751161"}'

# 다수 URL 일괄 처리
curl -X POST https://your-ngrok-url.ngrok-free.app/api/blog/grades \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://blog.naver.com/url1","https://blog.naver.com/url2"]}'
```

**공통 특징**:
- ✅ REST API로 간편한 통합
- ✅ 병렬 처리 (최대 3개 동시)
- ✅ 30-40초 응답 시간
- ✅ 자동 쿠키 관리

📚 **자세한 사용법**: [`API_사용안내.md`](API_사용안내.md) 참고

---

### 방법 2: 직접 스크립트 실행

**명령줄 인자 사용**:
```bash
python blogdex_selenium_login.py https://blog.naver.com/nyang2ne/224038751161
```

**특징**:
- ✅ 구글 로그인 자동화
- ✅ 쿠키 자동 저장/재사용
- ✅ JSON 파일로 결과 저장

## ⚙️ 환경변수 설정

`.env` 파일 예시:

```env
GOOGLE_EMAIL=your-email@gmail.com
GOOGLE_PASSWORD=your-password
BLOG_IDS=doromi__,blogpeople,djusti
RESULT_PATH=data/json_results/blog_grades.json
WAIT_TIME=10
TWO_FACTOR_WAIT_TIME=60
HEADLESS=false
```

## 🔐 로그인 과정

1. 스크립트가 브라우저를 열고 블덱스 로그인 페이지로 이동
2. 자동으로 이메일 입력까지 진행
3. **60초 동안 수동으로 완료**:
   - 비밀번호 입력
   - 2단계 인증 완료
4. 로그인 성공 시 쿠키 자동 저장
5. **다음 실행부터는 쿠키로 자동 로그인** (재로그인 불필요)

## 📊 출력 형식

```json
{
  "timestamp": "2025-10-14T17:00:00",
  "total_count": 2,
  "results": {
    "doromi__": "준최2",
    "blogpeople": "최적3+"
  }
}
```

## ⚠️ 주의사항

### 구글 로그인 제한
- 구글은 자동화 도구를 감지하여 로그인을 차단합니다
- 이메일 입력까지 자동화, 이후는 수동으로 진행해야 합니다
- 첫 로그인 후 쿠키가 저장되면 재로그인이 불필요합니다

### 속도 제한
- 너무 많은 요청을 빠르게 보내면 차단될 수 있습니다
- 각 블로그 조회 사이에 2초 대기 시간이 설정되어 있습니다

### 보안
- ⚠️ `.env` 파일을 Git에 커밋하지 마세요
- ⚠️ `config.py`를 Git에 커밋하지 마세요 (deprecated)
- ⚠️ `cookies.json`을 Git에 커밋하지 마세요

## 📁 파일 구조

```
진행용_blogdex/
├── api_server.py          # FastAPI 서버 ⭐
├── crawler.py             # 크롤링 모듈 ⭐
├── start_server.py        # 로컬 서버 실행 ⭐
├── start_server_ngrok.py  # 외부 접속 서버 (ngrok) ⭐
├── blogdex_selenium_login.py  # 메인 스크립트 (직접 실행용)
├── result_store.py        # 결과 저장 모듈 ⭐
├── driver_pool.py         # 드라이버 풀 관리 ⭐
├── .env                   # 환경변수 (gitignore)
├── requirements.txt       # Python 의존성
├── cookies.pkl            # 세션 쿠키 (자동 생성)
├── README.md              # 이 파일
├── API_사용안내.md        # API 상세 가이드 ⭐
└── data/
    └── json_results/      # 크롤링 결과 저장
```

## 🔧 문제 해결

### 구글 로그인 실패
**증상**: "브라우저가 안전하지 않습니다"

**해결**: 60초 동안 수동으로 비밀번호 + 2단계 인증 완료

### 로그 확인
```bash
# 로그 파일 확인
cat scraper.log

# 실시간 로그 모니터링
tail -f scraper.log
```

## 🎯 개선 완료 / 향후 계획

### ✅ 완료
- [x] FastAPI REST API 서버
- [x] 병렬 처리 (최대 3개 동시)
- [x] 쿠키 자동 관리
- [x] API 문서 자동 생성 (Swagger)

### 📋 향후 계획
- [ ] 웹 대시보드
- [ ] Docker 컨테이너화
- [ ] 데이터베이스 연동
- [ ] CI/CD 파이프라인

## 📚 추가 문서

- [`API_사용안내.md`](API_사용안내.md) - FastAPI 서버 사용 가이드 ⭐

## 📄 라이선스

개인 프로젝트 - 교육 및 개인 사용 목적

