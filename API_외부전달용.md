# BlogDex 등급 조회 API 문서

## 📋 개요

이 API는 네이버 블로그 URL을 입력받아 BlogDex 등급 정보를 반환합니다.

### 주요 기능
- ✅ 네이버 블로그 URL 등급 조회
- ✅ 단일 URL 조회
- ✅ 다수 URL 일괄 처리 (최대 3개 동시)
- ✅ 실시간 크롤링 (항상 최신 데이터)

### 접속 URL
```
https://stephine-ganglial-signally.ngrok-free.dev
```

**Note**: ngrok 무료 플랜 사용 중이며, 서버 재시작 시 URL이 변경될 수 있습니다.

### API 문서 (Swagger UI)
```
https://stephine-ganglial-signally.ngrok-free.dev/docs
```

브라우저에서 직접 접속하여 API를 테스트할 수 있습니다.

---

## 🔑 인증

현재 인증이 필요하지 않습니다. API 키나 토큰 없이 바로 사용 가능합니다.

---

## ⚠️ 제한사항

### Rate Limit
- 최대 3개 요청 동시 처리
- 한 URL당 약 30-40초 소요
- 5개 URL 요청 시: 약 60-80초 소요 (3개 + 2개 순차 처리)

### 응답 시간
- 단일 URL: 30-40초
- 다수 URL: 30-40초 × (URL 수 / 3 올림)

### ngrok 무료 플랜
- 처음 접속 시 "Visit Site" 버튼 클릭 필요
- 프로그래밍 방식 사용 시 헤더에 `ngrok-skip-browser-warning: true` 추가

---

## 📡 API 엔드포인트

### 1. 헬스 체크

서버 상태를 확인합니다.

#### 요청
```http
GET /health
```

#### 응답
```json
{
  "status": "ok",
  "message": "BlogDex Grade API is running",
  "max_concurrent": 3
}
```

#### cURL 예시
```bash
curl https://stephine-ganglial-signally.ngrok-free.dev/health \
  -H "ngrok-skip-browser-warning: true"
```

---

### 2. 단일 블로그 등급 조회

하나의 블로그 URL 등급을 조회합니다.

#### 요청
```http
POST /api/blog/grade
Content-Type: application/json
```

#### 요청 본문
```json
{
  "url": "https://blog.naver.com/nyang2ne/224038751161"
}
```

#### 성공 응답 (200 OK)
```json
{
  "url": "https://blog.naver.com/nyang2ne/224038751161",
  "level": "엑스퍼트3",
  "success": true
}
```

#### 실패 응답 (200 OK)
```json
{
  "url": "https://blog.naver.com/invalid/000",
  "level": null,
  "success": false,
  "error": "등급 추출 실패"
}
```

#### 필드 설명
- `url` (string, required): 요청한 블로그 URL
- `level` (string, nullable): BlogDex 등급 (성공 시)
- `success` (boolean, required): 성공 여부
- `error` (string, nullable): 에러 메시지 (실패 시)

#### cURL 예시
```bash
curl -X POST https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grade \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "url": "https://blog.naver.com/nyang2ne/224038751161"
  }'
```

#### Python 예시
```python
import requests

url = "https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grade"
headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}
data = {
    "url": "https://blog.naver.com/nyang2ne/224038751161"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"URL: {result['url']}")
print(f"등급: {result['level']}")
print(f"성공: {result['success']}")
```

#### JavaScript (Node.js) 예시
```javascript
const axios = require('axios');

const url = 'https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grade';
const headers = {
  'Content-Type': 'application/json',
  'ngrok-skip-browser-warning': 'true'
};
const data = {
  url: 'https://blog.naver.com/nyang2ne/224038751161'
};

axios.post(url, data, { headers })
  .then(response => {
    console.log('URL:', response.data.url);
    console.log('등급:', response.data.level);
    console.log('성공:', response.data.success);
  })
  .catch(error => {
    console.error('에러:', error);
  });
```

---

### 3. 다수 블로그 등급 일괄 조회

여러 블로그 URL의 등급을 일괄 조회합니다.

#### 요청
```http
POST /api/blog/grades
Content-Type: application/json
```

#### 요청 본문
```json
{
  "urls": [
    "https://blog.naver.com/nyang2ne/224038751161",
    "https://blog.naver.com/test1/123",
    "https://blog.naver.com/test2/456"
  ]
}
```

#### 성공 응답 (200 OK)
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
  },
  {
    "url": "https://blog.naver.com/test2/456",
    "level": "마스터1",
    "success": true
  }
]
```

#### 응답 형태
- 배열 형태로 반환
- 각 항목은 단일 조회와 동일한 구조
- 성공/실패가 섞여 있어도 개별 처리됨

#### cURL 예시
```bash
curl -X POST https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grades \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "urls": [
      "https://blog.naver.com/nyang2ne/224038751161",
      "https://blog.naver.com/test1/123"
    ]
  }'
```

#### Python 예시
```python
import requests

url = "https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grades"
headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}
data = {
    "urls": [
        "https://blog.naver.com/nyang2ne/224038751161",
        "https://blog.naver.com/test1/123",
        "https://blog.naver.com/test2/456"
    ]
}

response = requests.post(url, json=data, headers=headers)
results = response.json()

for result in results:
    if result['success']:
        print(f"✅ {result['url']}: {result['level']}")
    else:
        print(f"❌ {result['url']}: {result.get('error', '알 수 없는 오류')}")
```

#### JavaScript (Node.js) 예시
```javascript
const axios = require('axios');

const url = 'https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grades';
const headers = {
  'Content-Type': 'application/json',
  'ngrok-skip-browser-warning': 'true'
};
const data = {
  urls: [
    'https://blog.naver.com/nyang2ne/224038751161',
    'https://blog.naver.com/test1/123',
    'https://blog.naver.com/test2/456'
  ]
};

axios.post(url, data, { headers })
  .then(response => {
    response.data.forEach(result => {
      if (result.success) {
        console.log(`✅ ${result.url}: ${result.level}`);
      } else {
        console.log(`❌ ${result.url}: ${result.error || '알 수 없는 오류'}`);
      }
    });
  })
  .catch(error => {
    console.error('에러:', error);
  });
```

---

### 4. 현재 처리 상태 조회 (디버깅용)

현재 처리 중인 URL 목록을 조회합니다.

#### 요청
```http
GET /api/status
```

#### 응답
```json
{
  "processing_urls": [
    "https://blog.naver.com/nyang2ne/224038751161"
  ],
  "count": 1,
  "max_concurrent": 3
}
```

#### cURL 예시
```bash
curl https://stephine-ganglial-signally.ngrok-free.dev/api/status \
  -H "ngrok-skip-browser-warning: true"
```

---

## 📊 등급 매핑

BlogDex 등급과 Level 매핑 정보:

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

API는 `level` 필드에 변환된 등급을 반환합니다.

---

## ⚡ 성능 및 특징

### 병렬 처리
- 최대 3개 요청을 동시에 처리
- 더 많은 요청은 대기 후 순차 처리
- 예: 5개 URL → 3개(30-40초) + 2개(30-40초) = 약 60-80초

### 중복 방지
- 같은 URL의 중복 요청은 409 Conflict 반환
- 처리 완료 후 다시 요청 가능

### 실시간 크롤링
- 캐시 없이 항상 최신 데이터 반환
- 실제 BlogDex 사이트에서 크롤링

---

## 🐛 에러 처리

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 성공적으로 처리됨 |
| 400 | Bad Request | 요청 파라미터 오류 |
| 409 | Conflict | 이미 처리 중인 URL |
| 500 | Internal Server Error | 서버 내부 오류 |

### 에러 응답 예시
```json
{
  "detail": "이미 처리 중인 URL입니다: https://blog.naver.com/..."
}
```

또는

```json
{
  "url": "https://blog.naver.com/invalid",
  "level": null,
  "success": false,
  "error": "등급 추출 실패"
}
```

---

## 🧪 빠른 테스트

### 1. Swagger UI 사용
브라우저에서 접속하여 직접 테스트:
```
https://stephine-ganglial-signally.ngrok-free.dev/docs
```

### 2. 샘플 URL로 테스트
```bash
# 단일 조회
curl -X POST https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grade \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{"url":"https://blog.naver.com/nyang2ne/224038751161"}'

# 일괄 조회
curl -X POST https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grades \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{"urls":["https://blog.naver.com/nyang2ne/224038751161"]}'
```

---

## 📞 문의

API 관련 문의사항이 있으시면 연락 바랍니다.

**주요 정보**
- 현재 URL: `https://stephine-ganglial-signally.ngrok-free.dev`
- API 문서: `https://stephine-ganglial-signally.ngrok-free.dev/docs`
- 서버 상태: `https://stephine-ganglial-signally.ngrok-free.dev/health`

---

## 🔗 관련 자료

### 추가 문서
- `API_사용안내.md` - 상세 사용 가이드
- `NGROK_사용안내.md` - ngrok 설정 및 관리

### 특징 요약
- ✅ 인증 불필요
- ✅ RESTful API
- ✅ JSON 응답
- ✅ 실시간 크롤링
- ✅ 병렬 처리 (최대 3개)
- ✅ 상세한 에러 메시지

