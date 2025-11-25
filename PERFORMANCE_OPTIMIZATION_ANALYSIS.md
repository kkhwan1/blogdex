# BlogDex Grade API - 성능 최적화 분석

**작성 일시**: 2025-11-07
**목적**: 30-60초 크롤링 시간을 단축하기 위한 최적화 방안 도출

---

## 📊 현재 성능 분석

### 실제 측정 시간
- **테스트 URL**: https://blog.naver.com/jaesung_lee7/224063822402
- **측정 시간**: 50.6초
- **목표**: 30초 이하로 단축

---

## ⏱️ 시간 소요 분석 (Line-by-Line)

### 1. Chrome 드라이버 생성 (~3초)
**위치**: [crawler.py:155-177](crawler.py#L155-L177)

```python
# L155-177: create_undetected_driver()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-dev-shm-usage")
# ... 기타 옵션들
driver = uc.Chrome(options=options, version_main=141)
```

**소요 시간**: 약 3초 (Chrome 프로세스 시작 + 드라이버 초기화)
**최적화 가능성**: ⚠️ 중간 (프로세스 재사용 시 제거 가능)

---

### 2. BlogDex 접속 (~6초)
**위치**: [crawler.py:296-297](crawler.py#L296-L297)

```python
# L296: BlogDex 메인 페이지 접속
driver.get("https://blogdex.space")
time.sleep(3)  # ← 하드코딩된 대기
```

**소요 시간**: 약 6초 (3초 sleep + 페이지 로드)
**최적화 가능성**: ✅ 높음 (불필요한 sleep 제거 가능)

---

### 3. 팝업 처리 (~2초)
**위치**: [crawler.py:189-211](crawler.py#L189-L211)

```python
# L189-211: close_login_popup()
popup_close_selectors = [
    "#radix-\\:r12\\: > div.relative > button",
    "button[class*='close']",
    # ... 여러 셀렉터
]
```

**소요 시간**: 약 2초
**최적화 가능성**: ⚠️ 낮음 (필수 작업)

---

### 4. 로그인 처리 (~15초)
**위치**: [crawler.py:303-392](crawler.py#L303-L392)

#### 4-1. 쿠키 로드 및 검증 (~8초)
```python
# L303-312: 쿠키 기반 로그인
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()  # ← 페이지 새로고침 (3초)
time.sleep(3)     # ← 하드코딩된 대기
time.sleep(5)     # ← 안정화 대기
```

**소요 시간**: 약 8초 (refresh + sleep 8초)
**최적화 가능성**: ✅ 높음 (sleep 5초 → 2초로 단축 가능)

#### 4-2. 구글 로그인 (첫 로그인 시만 ~60-120초)
```python
# L318-392: Google OAuth 로그인
time.sleep(3)  # 로그인 버튼 대기
time.sleep(3)  # 이메일 입력 대기
time.sleep(7)  # Google 버튼 클릭 후 대기
time.sleep(3)  # 페이지 전환 대기
```

**소요 시간**: 첫 로그인 시 60-120초 (쿠키 있으면 생략)
**최적화 가능성**: ⚠️ 중간 (쿠키 재사용으로 대부분 회피 가능)

---

### 5. 메인 페이지 이동 (~6초)
**위치**: [crawler.py:354-365](crawler.py#L354-L365)

```python
# L354: 메인 페이지로 재이동
time.sleep(3)  # ← 하드코딩된 대기
driver.get("https://blogdex.space")
time.sleep(7)  # ← 과도한 대기
```

**소요 시간**: 약 6초 (sleep 3+7=10초, 실제는 페이지 로드로 단축됨)
**최적화 가능성**: ✅ 매우 높음 (sleep 7초 → 2초로 단축)

---

### 6. 블로그 URL 입력 (~3초)
**위치**: [crawler.py:401-413](crawler.py#L401-L413)

```python
# L405-412: 한 글자씩 입력 (휴먼 시뮬레이션)
for char in blog_url:
    search_input.send_keys(char)
    time.sleep(0.1)  # ← 글자당 0.1초 대기
search_input.send_keys(Keys.RETURN)
time.sleep(3)
```

**소요 시간**: 약 3초 (URL 길이 × 0.1초 + sleep 3초)
**최적화 가능성**: ⚠️ 중간 (봇 감지 회피 필요)

---

### 7. 등급 추출 (~15초)
**위치**: [crawler.py:244-268](crawler.py#L244-L268)

```python
# L244-268: extract_blog_grade()
grade_svg = WebDriverWait(driver, 15).until(  # ← 최대 15초 대기
    EC.presence_of_element_located((By.CSS_SELECTOR, grade_svg_selector))
)
```

**소요 시간**: 최대 15초 (실제는 5-10초)
**최적화 가능성**: ⚠️ 낮음 (페이지 로딩 시간)

---

## 📈 시간 분포 요약

| 단계 | 현재 시간 | 최적화 후 예상 | 절감 |
|------|----------|---------------|------|
| 1. Chrome 드라이버 생성 | 3초 | **0초** (재사용) | -3초 |
| 2. BlogDex 접속 | 6초 | **3초** (sleep 제거) | -3초 |
| 3. 팝업 처리 | 2초 | 2초 | 0초 |
| 4. 로그인 (쿠키) | 8초 | **3초** (sleep 단축) | -5초 |
| 5. 메인 페이지 이동 | 6초 | **3초** (sleep 단축) | -3초 |
| 6. URL 입력 | 3초 | 3초 | 0초 |
| 7. 등급 추출 | 15초 | **10초** (timeout 단축) | -5초 |
| **총합** | **43초** | **24초** | **-19초** |

**실제 측정**: 50.6초 (Chrome 종료 포함)
**최적화 목표**: 30초 이하 (약 **40% 단축**)

---

## 🚀 최적화 전략

### 전략 1: Chrome 세션 재사용 ⭐⭐⭐⭐⭐
**효과**: 약 3-5초 단축

#### 현재 구조
```python
def crawl_blog_grade(url: str):
    driver = create_undetected_driver()  # 매번 새로 생성
    try:
        # ... 크롤링
    finally:
        driver.quit()  # 매번 종료
```

#### 개선 방안
```python
# 글로벌 드라이버 풀 생성
from queue import Queue
driver_pool = Queue(maxsize=3)

def initialize_driver_pool():
    """서버 시작 시 3개 드라이버 미리 생성"""
    for _ in range(3):
        driver = create_undetected_driver()
        driver.get("https://blogdex.space")
        # 로그인까지 완료해둠
        driver_pool.put(driver)

def crawl_blog_grade_optimized(url: str):
    driver = driver_pool.get()  # 풀에서 가져오기
    try:
        # 이미 로그인된 상태에서 시작
        driver.get("https://blogdex.space")  # 메인 페이지로만 이동
        # ... 크롤링
        return result
    finally:
        driver_pool.put(driver)  # 풀에 반환 (종료 안 함)
```

**장점**:
- ✅ Chrome 프로세스 생성 시간 제거 (3초)
- ✅ 로그인 과정 생략 (쿠키 유지됨)
- ✅ 서버 안정성 향상 (프로세스 재사용)

**단점**:
- ⚠️ 메모리 사용량 증가 (Chrome 3개 상주)
- ⚠️ 장시간 사용 시 세션 만료 가능성

**구현 복잡도**: ⭐⭐⭐ (중간)

---

### 전략 2: 불필요한 sleep() 제거 ⭐⭐⭐⭐
**효과**: 약 8-10초 단축

#### 제거 가능한 sleep
```python
# crawler.py:297
time.sleep(3)  # BlogDex 접속 후
# → WebDriverWait로 대체 가능

# crawler.py:307
time.sleep(3)  # 쿠키 refresh 후
# → 0.5초로 단축 가능

# crawler.py:312
time.sleep(5)  # 페이지 안정화
# → 2초로 단축 가능

# crawler.py:361
time.sleep(7)  # Google 버튼 클릭 후
# → 3초로 단축 가능

# crawler.py:354
time.sleep(3)  # 메인 페이지 이동 전
# → 제거 가능
```

#### 개선 방안
```python
# Before
driver.get("https://blogdex.space")
time.sleep(3)  # 무조건 3초 대기

# After
driver.get("https://blogdex.space")
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)
# 최대 5초 대기하지만, 로드되면 즉시 진행
```

**장점**:
- ✅ 구현 간단
- ✅ 부작용 없음
- ✅ 즉시 적용 가능

**단점**:
- ⚠️ 느린 네트워크에서 타임아웃 가능성

**구현 복잡도**: ⭐ (쉬움)

---

### 전략 3: WebDriverWait 타임아웃 최적화 ⭐⭐⭐
**효과**: 약 5초 단축

#### 현재 타임아웃
```python
# crawler.py:244
grade_svg = WebDriverWait(driver, 15).until(...)  # 최대 15초
```

#### 개선 방안
```python
# 타임아웃을 10초로 단축 (실제 로드는 5-7초)
grade_svg = WebDriverWait(driver, 10).until(...)

# 더 빠른 polling 간격 설정
grade_svg = WebDriverWait(driver, 10, poll_frequency=0.1).until(...)
# 기본 0.5초 → 0.1초로 단축하여 반응 속도 향상
```

**장점**:
- ✅ 빠른 응답 시 즉시 진행
- ✅ 평균 대기 시간 감소

**단점**:
- ⚠️ 느린 페이지 로드 시 실패 가능성

**구현 복잡도**: ⭐ (쉬움)

---

### 전략 4: Headless 모드 전환 ⭐⭐
**효과**: 약 2-3초 단축

#### 개선 방안
```python
# crawler.py:159
options.add_argument("--headless=new")  # 새로운 headless 모드
options.add_argument("--disable-gpu")
```

**장점**:
- ✅ 렌더링 오버헤드 감소
- ✅ 서버 리소스 절약

**단점**:
- ⚠️ 일부 사이트에서 봇 감지 가능성
- ⚠️ 디버깅 어려움

**구현 복잡도**: ⭐ (쉬움)

---

### 전략 5: URL 입력 속도 향상 ⭐
**효과**: 약 1-2초 단축

#### 현재 구현
```python
# crawler.py:405-412
for char in blog_url:
    search_input.send_keys(char)
    time.sleep(0.1)  # 글자당 0.1초
```

#### 개선 방안
```python
# 방법 1: 한 번에 입력 (봇 감지 위험)
search_input.send_keys(blog_url)

# 방법 2: 속도만 높임
for char in blog_url:
    search_input.send_keys(char)
    time.sleep(0.05)  # 0.1초 → 0.05초

# 방법 3: JavaScript로 직접 입력
driver.execute_script(
    f"arguments[0].value = '{blog_url}';",
    search_input
)
```

**장점**:
- ✅ 1-2초 단축

**단점**:
- ⚠️ 봇 감지 위험 증가

**구현 복잡도**: ⭐ (쉬움)

---

## 📋 최적화 우선순위

### Phase 1: 즉시 적용 가능 (Low Risk, High Impact)
1. ✅ **불필요한 sleep() 제거** (8-10초 단축)
   - crawler.py:297, 307, 312, 354, 361
   - WebDriverWait로 대체

2. ✅ **WebDriverWait 타임아웃 최적화** (5초 단축)
   - 15초 → 10초 단축
   - polling 간격 0.5초 → 0.1초

**예상 효과**: 50초 → 37초 (약 **26% 단축**)

---

### Phase 2: 중간 적용 (Medium Risk, High Impact)
3. ⭐ **Chrome 세션 재사용** (3-5초 단축)
   - 글로벌 드라이버 풀 구현
   - 서버 시작 시 3개 미리 생성

**예상 효과**: 37초 → 30초 (약 **40% 단축**)

---

### Phase 3: 추가 최적화 (Optional)
4. ⚠️ **Headless 모드** (2-3초 단축)
   - 봇 감지 테스트 필요

5. ⚠️ **URL 입력 속도 향상** (1-2초 단축)
   - 0.1초 → 0.05초

**최종 목표**: 50초 → 25초 (약 **50% 단축**)

---

## 🔧 구현 계획

### Step 1: sleep() 최적화 (즉시 적용)

**파일**: crawler.py

**변경 1**: BlogDex 접속 후 대기 제거
```python
# L296-297 Before
driver.get("https://blogdex.space")
time.sleep(3)

# L296-297 After
driver.get("https://blogdex.space")
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)
```

**변경 2**: 쿠키 refresh 후 대기 단축
```python
# L307 Before
time.sleep(3)

# L307 After
time.sleep(0.5)  # 3초 → 0.5초
```

**변경 3**: 페이지 안정화 대기 단축
```python
# L312 Before
time.sleep(5)

# L312 After
time.sleep(2)  # 5초 → 2초
```

**변경 4**: 메인 페이지 이동 전 대기 제거
```python
# L354 Before
time.sleep(3)
driver.get("https://blogdex.space")

# L354 After
driver.get("https://blogdex.space")  # 즉시 이동
```

**변경 5**: Google 버튼 클릭 후 대기 단축
```python
# L361 Before
time.sleep(7)

# L361 After
time.sleep(3)  # 7초 → 3초
```

---

### Step 2: WebDriverWait 최적화

**파일**: crawler.py

**변경**: 타임아웃 및 polling 간격 최적화
```python
# L244 Before
grade_svg = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, grade_svg_selector))
)

# L244 After
grade_svg = WebDriverWait(driver, 10, poll_frequency=0.1).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, grade_svg_selector))
)
```

---

### Step 3: Chrome 세션 재사용 (별도 구현)

**새 파일**: driver_pool.py

```python
from queue import Queue, Empty
import threading
from crawler import create_undetected_driver
import time

class DriverPool:
    def __init__(self, size=3):
        self.pool = Queue(maxsize=size)
        self.size = size
        self.lock = threading.Lock()
        self.initialized = False

    def initialize(self):
        """서버 시작 시 드라이버 풀 생성"""
        if self.initialized:
            return

        with self.lock:
            if self.initialized:
                return

            print(f"[INFO] 드라이버 풀 초기화 중... (크기: {self.size})")
            for i in range(self.size):
                driver = create_undetected_driver()
                driver.get("https://blogdex.space")
                self.pool.put(driver)
                print(f"[INFO] 드라이버 {i+1}/{self.size} 생성 완료")

            self.initialized = True
            print("[INFO] 드라이버 풀 초기화 완료")

    def get(self, timeout=30):
        """드라이버 가져오기"""
        if not self.initialized:
            raise RuntimeError("드라이버 풀이 초기화되지 않았습니다")

        try:
            return self.pool.get(timeout=timeout)
        except Empty:
            raise TimeoutError("드라이버 풀에서 드라이버를 가져오는 데 실패했습니다")

    def put(self, driver):
        """드라이버 반환"""
        try:
            # 드라이버 상태 확인
            driver.current_url  # 연결 확인
            self.pool.put(driver)
        except Exception as e:
            print(f"[ERROR] 손상된 드라이버 감지: {e}")
            # 새 드라이버 생성
            new_driver = create_undetected_driver()
            new_driver.get("https://blogdex.space")
            self.pool.put(new_driver)

    def cleanup(self):
        """서버 종료 시 모든 드라이버 정리"""
        print("[INFO] 드라이버 풀 정리 중...")
        while not self.pool.empty():
            try:
                driver = self.pool.get_nowait()
                driver.quit()
            except Exception as e:
                print(f"[ERROR] 드라이버 정리 실패: {e}")
        print("[INFO] 드라이버 풀 정리 완료")

# 글로벌 인스턴스
driver_pool = DriverPool(size=3)
```

**파일**: api_server.py

```python
# L14 After: 추가 import
from driver_pool import driver_pool

# L29 After: 서버 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 드라이버 풀 초기화"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, driver_pool.initialize)
    logger.info("드라이버 풀 초기화 완료")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 드라이버 풀 정리"""
    driver_pool.cleanup()
    logger.info("드라이버 풀 정리 완료")
```

**파일**: crawler.py

```python
# 새 함수 추가
def crawl_blog_grade_with_pool(url: str):
    """드라이버 풀을 사용한 크롤링 (최적화 버전)"""
    from driver_pool import driver_pool

    driver = driver_pool.get()  # 풀에서 가져오기
    start_time = time.time()

    try:
        # 이미 BlogDex에 접속된 상태
        # 메인 페이지로만 이동
        driver.get("https://blogdex.space")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # URL 입력 및 등급 추출 (기존 로직)
        # ... (L401-436 동일)

        return result

    finally:
        driver_pool.put(driver)  # 풀에 반환 (quit 안 함)
```

---

## 📊 예상 성능 개선

| 버전 | 시간 | 개선율 | 적용 내용 |
|------|------|--------|-----------|
| **현재** | 50.6초 | - | 개선 전 |
| **Phase 1** | 37초 | **27%** | sleep 최적화 + timeout 단축 |
| **Phase 2** | 30초 | **40%** | + 드라이버 풀 |
| **Phase 3** | 25초 | **50%** | + headless + 입력 속도 |

---

## ⚠️ 주의사항

### 봇 감지 위험
- **Headless 모드**: BlogDex가 headless 브라우저를 차단할 수 있음
- **빠른 입력**: 너무 빠른 타이핑은 봇으로 감지될 수 있음
- **세션 재사용**: 장시간 사용 시 세션 만료 가능

### 테스트 필요
1. Phase 1 적용 후 100회 테스트
2. 성공률 95% 이상 확인
3. Phase 2 적용 (드라이버 풀)
4. 메모리 사용량 모니터링

---

## 🎯 실행 계획

### 1단계: Phase 1 적용 (즉시)
- [ ] crawler.py의 sleep() 값 수정 (5곳)
- [ ] WebDriverWait 타임아웃 단축 (1곳)
- [ ] 테스트 10회 실행 → 성공률 확인
- [ ] 평균 시간 측정 (목표: 37초)

### 2단계: Phase 2 적용 (1일 후)
- [ ] driver_pool.py 생성
- [ ] api_server.py에 startup/shutdown 이벤트 추가
- [ ] crawler.py에 crawl_blog_grade_with_pool() 추가
- [ ] 테스트 50회 실행 → 안정성 확인
- [ ] 메모리 사용량 모니터링

### 3단계: Phase 3 검토 (선택)
- [ ] Headless 모드 테스트
- [ ] 봇 감지 여부 확인
- [ ] 성공 시 적용, 실패 시 Phase 2 유지

---

**작성자**: Claude Code
**최종 업데이트**: 2025-11-07
**버전**: 1.0 (Performance Optimization Plan)
**상태**: 📋 계획 수립 완료
