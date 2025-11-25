# ngrok 사용 안내

## 서버 및 ngrok 설정 완료

### 현재 설정 상태

✅ **FastAPI 서버**: 포트 8000에서 실행 중
✅ **ngrok 터널**: 실행 중
✅ **외부 접속 URL**: https://stephine-ganglial-signally.ngrok-free.dev

---

## 서버 실행 방법

### 옵션 1: 개별 실행 (수동)

#### 1단계: FastAPI 서버 시작
```bash
# 별도 PowerShell 창에서
python start_server.py
```

또는

```bash
python api_server.py
```

#### 2단계: ngrok 터널 시작
```bash
# 다른 PowerShell 창에서
.\start_ngrok.bat
```

### 옵션 2: 통합 실행 (자동 - 추천)

```bash
# FastAPI 서버와 ngrok을 모두 시작
.\start_server_with_ngrok.bat
```

이 스크립트는:
1. FastAPI 서버를 별도 창에서 시작
2. 5초 대기 후 ngrok 터널을 별도 창에서 시작
3. 각각 독립적으로 실행됨

---

## 외부 접속 정보

### ngrok 외부 URL
- **URL**: `https://stephine-ganglial-signally.ngrok-free.dev`
- **설명**: 이 URL은 서버를 재시작하면 변경될 수 있습니다

### API 엔드포인트

#### 1. 단일 블로그 등급 조회
```
POST https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grade
Content-Type: application/json

{
  "url": "https://blog.naver.com/nyang2ne/224038751161"
}
```

#### 2. 다수 블로그 등급 일괄 조회
```
POST https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grades
Content-Type: application/json

{
  "urls": [
    "https://blog.naver.com/url1",
    "https://blog.naver.com/url2"
  ]
}
```

#### 3. 헬스 체크
```
GET https://stephine-ganglial-signally.ngrok-free.dev/health
```

#### 4. API 문서 (Swagger UI)
```
GET https://stephine-ganglial-signally.ngrok-free.dev/docs
```

---

## ngrok 웹 인터페이스

ngrok는 웹 인터페이스를 제공합니다:

```
http://localhost:4040
```

이 페이지에서:
- 현재 터널 상태 확인
- HTTP 요청 로그 실시간 확인
- 터널 URL 확인

---

## 주의사항

### ngrok 무료 플랜 제한
- ✅ HTTPS 자동 적용
- ✅ 무제한 데이터 전송
- ⚠️ 재시작시 URL 변경됨
- ⚠️ 세션 2시간 제한 (인증 토큰 없을 경우)
- ⚠️ 분당 40개 연결 제한

### 세션 시간 제한 해제하기
인증 토큰을 설정하면 세션 제한이 해제됩니다:

1. https://dashboard.ngrok.com/get-started/your-authtoken 에서 무료 가입
2. `.env` 파일에 토큰 추가:
   ```
   NGROK_AUTH_TOKEN=your_token_here
   ```

### ngrok 방문 페이지
무료 플랜은 처음 접속 시 "Visit Site" 버튼을 클릭해야 합니다.
프로그래밍 방식으로 사용하려면 헤더에 다음 추가:
```
ngrok-skip-browser-warning: true
```

---

## 프로세스 종료

### 서버 및 ngrok 종료

각 창에서 `Ctrl+C`를 눌러 종료하거나, 프로세스를 종료:

```powershell
# FastAPI 서버 종료
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process

# ngrok 종료
Get-Process | Where-Object {$_.ProcessName -eq "ngrok"} | Stop-Process
```

---

## 파일 구성

```
blogdex_251028/
├── api_server.py                    # FastAPI 서버 메인 파일
├── crawler.py                       # 크롤링 로직
├── start_server.py                  # FastAPI 서버 시작 (로컬용)
├── start_ngrok.bat                  # ngrok 터널 시작
├── start_server_with_ngrok.bat      # 통합 실행 (추천)
├── ngrok.exe                        # ngrok 실행 파일
├── .env                             # 환경변수 (구글 계정 등)
├── cookies.pkl                      # 로그인 쿠키 (자동 생성)
└── requirements.txt                 # Python 의존성
```

---

## 테스트 방법

### PowerShell로 테스트

```powershell
# 단일 URL
$body = @{
    url = "https://blog.naver.com/nyang2ne/224038751161"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/api/blog/grade" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

### Python으로 테스트

```python
import requests

# 단일 URL
response = requests.post(
    "http://localhost:8000/api/blog/grade",
    json={"url": "https://blog.naver.com/nyang2ne/224038751161"}
)
print(response.json())

# 다수 URL
response = requests.post(
    "http://localhost:8000/api/blog/grades",
    json={
        "urls": [
            "https://blog.naver.com/nyang2ne/224038751161",
            "https://blog.naver.com/test/123"
        ]
    }
)
print(response.json())
```

---

## 문제 해결

### ngrok이 시작되지 않음
- Windows 보안 정책 확인
- `ngrok.exe` 파일이 프로젝트 폴더에 있는지 확인

### 외부에서 접속 불가
- 방화벽 설정 확인
- ngrok 서비스 상태 확인: http://localhost:4040

### 서버가 응답하지 않음
- FastAPI 서버가 실행 중인지 확인
- `http://localhost:8000/health` 접속 테스트

---

## 성능 정보

- **단일 요청**: 30-40초
- **3개 동시 처리**: 30-40초 (병렬 처리)
- **5개 동시 처리**: 60-80초 (3개 + 2개 순차)
- **쿠키 사용**: 로그인 불필요 (자동)
- **첫 실행**: 약 2분 (구글 로그인 필요)

---

## 현재 상태

✅ FastAPI 서버: 실행 중 (포트 8000)
✅ ngrok 터널: 실행 중
✅ 로그인 쿠키: 저장됨 (cookies.pkl)
✅ 외부 접속: https://stephine-ganglial-signally.ngrok-free.dev




