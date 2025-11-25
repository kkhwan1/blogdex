"""
BlogDex 등급 조회 API 서버
FastAPI 기반, 동시 최대 3개 브라우저 병렬 처리
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from typing import List, Optional
from crawler import crawl_blog_grade, crawl_blog_grade_with_pool
from driver_pool import driver_pool
import time
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BlogDex Grade API",
    description="블로그 등급 조회 API - level 정보 제공",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 병렬 처리 제한 (최대 3개)
MAX_CONCURRENT_CRAWLS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_CRAWLS)

# 중복 요청 방지
crawling_urls = set()
crawling_lock = threading.Lock()

# 서버 시작/종료 이벤트
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 드라이버 풀 초기화"""
    logger.info("서버 시작 - 드라이버 풀 초기화 시작...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, driver_pool.initialize)
    logger.info("드라이버 풀 초기화 완료")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 드라이버 풀 정리"""
    logger.info("서버 종료 - 드라이버 풀 정리 시작...")
    driver_pool.cleanup()
    logger.info("드라이버 풀 정리 완료")

# HTTPException을 GradeResponse 형식으로 변환
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTPException을 GradeResponse 형식으로 변환
    모든 에러를 일관된 JSON 형식으로 반환
    """
    # URL 추출 시도
    url = "unknown"
    try:
        body = await request.json()
        url = body.get("url", "unknown")
    except:
        pass

    # GradeResponse 형식으로 통일 (확장된 필드 포함)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "url": url,
            "blog_id": None,
            "grade": None,
            "level": None,
            "level_en": None,
            "tier": None,
            "tier_en": None,
            "tier_rank": None,
            "timestamp": None,
            "success": False,
            "error": exc.detail,
            "file_path": None
        }
    )

# Pydantic 모델
class GradeRequest(BaseModel):
    url: HttpUrl
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://blog.naver.com/nyang2ne/224038751161"
            }
        }

class GradeResponse(BaseModel):
    url: str
    blog_id: Optional[str] = None
    grade: Optional[str] = None
    level: Optional[str] = None
    level_en: Optional[str] = None
    tier: Optional[str] = None
    tier_en: Optional[str] = None
    tier_rank: Optional[int] = None
    timestamp: Optional[str] = None
    success: bool
    error: Optional[str] = None
    file_path: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://blog.naver.com/nyang2ne/224038751161",
                "blog_id": "nyang2ne",
                "grade": "최적2+",
                "level": "엑스퍼트3",
                "level_en": "Expert3",
                "tier": "엑스퍼트 블로거",
                "tier_en": "Expert Blogger",
                "tier_rank": 3,
                "timestamp": "2025-11-19 19:30:45",
                "success": True,
                "file_path": "data/json_results/nyang2ne_grade_20251119_193045.json"
            }
        }

class BatchGradeRequest(BaseModel):
    urls: List[HttpUrl]
    
    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://blog.naver.com/nyang2ne/224038751161",
                    "https://blog.naver.com/test1/123"
                ]
            }
        }

def validate_naver_blog_url(url: str) -> bool:
    """
    네이버 블로그 URL 여부 검증

    허용:
    - https://blog.naver.com/아이디/글번호
    - https://blog.naver.com/아이디
    - http://blog.naver.com/아이디/글번호
    - http://blog.naver.com/아이디

    거부:
    - 다른 블로그 플랫폼
    - 네이버 블로그 메인 페이지
    - 잘못된 형식
    """
    from urllib.parse import urlparse
    import re

    try:
        parsed = urlparse(url)

        # 도메인 체크
        if "blog.naver.com" not in parsed.netloc:
            return False

        # 경로 체크 (아이디 또는 아이디/글번호 형식)
        path_pattern = r'^/[^/]+(/\d+)?$'
        if not re.match(path_pattern, parsed.path):
            return False

        return True
    except:
        return False

# 헬스 체크
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "ok",
        "message": "BlogDex Grade API is running",
        "max_concurrent": MAX_CONCURRENT_CRAWLS
    }

# 단일 URL 조회
@app.post("/api/blog/grade", response_model=GradeResponse)
async def get_blog_grade(request: GradeRequest):
    """
    단일 블로그 URL의 등급 조회

    - **url**: 블로그 URL (필수)

    크롤링 완료까지 30-40초 소요됩니다.
    최대 180초 타임아웃 적용.
    """
    url = str(request.url)
    start_time = time.time()
    logger.info(f"요청 시작: {url}")

    # 중복 요청 체크
    with crawling_lock:
        if url in crawling_urls:
            logger.warning(f"중복 요청 거부: {url}")
            raise HTTPException(
                status_code=409,
                detail=f"이미 처리 중인 URL입니다: {url}"
            )
        crawling_urls.add(url)

    try:
        # 세마포어로 병렬 제한 (최대 3개)
        async with semaphore:
            # 블로킹 크롤링을 별도 스레드에서 실행
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                # 타임아웃 추가 (180초 = 3분)
                # Phase 2: 드라이버 풀 사용
                result = await asyncio.wait_for(
                    loop.run_in_executor(pool, crawl_blog_grade_with_pool, url),
                    timeout=180
                )

        elapsed = time.time() - start_time
        logger.info(f"요청 완료: {url} ({elapsed:.2f}초)")
        return GradeResponse(**result)

    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        logger.error(f"타임아웃: {url} ({elapsed:.2f}초)")
        raise HTTPException(
            status_code=504,
            detail=f"크롤링 타임아웃 (180초 초과): {url}"
        )

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"요청 실패: {url} ({elapsed:.2f}초) - {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"크롤링 실패: {str(e)}"
        )
    finally:
        # 처리 완료 후 제거
        with crawling_lock:
            crawling_urls.discard(url)

# 다수 URL 일괄 조회
@app.post("/api/blog/grades", response_model=List[GradeResponse])
async def get_blog_grades(request: BatchGradeRequest):
    """
    다수 블로그 URL의 등급 일괄 조회
    
    - **urls**: 블로그 URL 리스트 (필수)
    
    최대 3개까지 동시 처리, 나머지는 대기합니다.
    5개 URL의 경우: 30-40초 (3개) + 30-40초 (2개) = 약 60-80초 소요
    """
    tasks = []
    
    for url in request.urls:
        # 각 URL에 대해 get_blog_grade 호출
        task = get_blog_grade(GradeRequest(url=url))
        tasks.append(task)
    
    # 모든 작업 동시 실행 (세마포어로 제한)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 예외 처리
    final_results = []
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append(GradeResponse(
                url=str(request.urls[idx]),
                level=None,
                success=False,
                error=str(result)
            ))
        else:
            final_results.append(result)
    
    return final_results

# 현재 처리 중인 URL 조회 (디버깅용)
@app.get("/api/status")
async def get_status():
    """
    현재 처리 중인 URL 목록 조회
    """
    with crawling_lock:
        return {
            "processing_urls": list(crawling_urls),
            "count": len(crawling_urls),
            "max_concurrent": MAX_CONCURRENT_CRAWLS
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

