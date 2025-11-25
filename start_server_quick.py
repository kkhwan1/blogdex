"""
빠른 시작 서버 (드라이버 풀 초기화 없음)
요청 시 드라이버 생성 방식으로 작동
"""
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    port = int(os.getenv("PORT", 8000))

    print("=" * 60)
    print("FastAPI Server - BlogDex Grade API (Quick Start)")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Swagger UI: http://localhost:{port}/docs")
    print(f"Health Check: http://localhost:{port}/health")
    print("=" * 60)
    print("\nNOTE: Driver pool initialization skipped.")
    print("Drivers will be created on-demand for each request.")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
