# BlogDex 등급 조회 API - 간단 요약

## 🌐 접속 URL
```
https://stephine-ganglial-signally.ngrok-free.dev
```

## 📝 주요 엔드포인트

### 1. 단일 URL 조회
```http
POST /api/blog/grade
```

**요청:**
```json
{
  "url": "https://blog.naver.com/nyang2ne/224038751161"
}
```

**응답:**
```json
{
  "url": "https://blog.naver.com/nyang2ne/224038751161",
  "level": "엑스퍼트3",
  "success": true
}
```

### 2. 다수 URL 일괄 조회
```http
POST /api/blog/grades
```

**요청:**
```json
{
  "urls": [
    "https://blog.naver.com/nyang2ne/224038751161",
    "https://blog.naver.com/test1/123"
  ]
}
```

**응답:**
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

## 🚀 빠른 사용법

### Python
```python
import requests

response = requests.post(
    "https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grade",
    json={"url": "https://blog.naver.com/nyang2ne/224038751161"},
    headers={"ngrok-skip-browser-warning": "true"}
)
print(response.json())
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

axios.post(
    'https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grade',
    { url: 'https://blog.naver.com/nyang2ne/224038751161' },
    { headers: { 'ngrok-skip-browser-warning': 'true' } }
).then(response => console.log(response.data));
```

### cURL
```bash
curl -X POST https://stephine-ganglial-signally.ngrok-free.dev/api/blog/grade \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{"url":"https://blog.naver.com/nyang2ne/224038751161"}'
```

## ⚠️ 중요 사항

1. **응답 시간**: URL당 30-40초 소요
2. **동시 처리**: 최대 3개 URL 동시 처리
3. **ngrok 헤더**: 프로그래밍 방식 사용 시 헤더 필수
   ```json
   "ngrok-skip-browser-warning": "true"
   ```
4. **API 문서**: https://stephine-ganglial-signally.ngrok-free.dev/docs

## 📚 상세 문서
전체 API 문서는 `API_외부전달용.md` 참고

