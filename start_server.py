"""
BlogDex API 서버 실행 스크립트
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BlogDex Grade API 서버 시작")
    print("=" * 60)
    print("📍 주소: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("🔍 헬스체크: http://localhost:8000/health")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 프로덕션 모드
        log_level="info",
        access_log=True
    )

