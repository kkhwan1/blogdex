"""
ngrok을 통한 외부 접속 가능한 FastAPI 서버 시작 스크립트

이 스크립트는:
1. ngrok 터널 생성
2. FastAPI 서버 시작
3. 공개 URL 출력

사용법:
    python start_server_ngrok.py

환경변수 (선택사항):
    PORT=8000              # FastAPI 서버 포트 (기본값: 8000)
    NGROK_AUTH_TOKEN=...   # ngrok 인증 토큰 (무료 회원가입 후 발급, 세션 시간 제한 해제용)
"""

import uvicorn
import os
import sys
import io
from pyngrok import ngrok, conf
import threading
import time
from dotenv import load_dotenv

# UTF-8 출력 설정 (Windows cp949 인코딩 문제 해결)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# .env 파일 로드
load_dotenv()

def start_fastapi_server(port: int):
    """FastAPI 서버를 별도 스레드에서 실행"""
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # ngrok 사용시 reload 비활성화 권장
        log_level="info"
    )

def main():
    # 환경 변수에서 포트 가져오기
    port = int(os.getenv("PORT", 8000))
    
    # ngrok 인증 토큰 설정 (선택사항)
    ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
    if ngrok_auth_token:
        conf.get_default().auth_token = ngrok_auth_token
        print(f"✅ ngrok 인증 토큰 설정 완료 (세션 시간 제한 해제)")
    else:
        print(f"⚠️ ngrok 인증 토큰 없음 (세션 2시간 제한)")
        print(f"   → https://dashboard.ngrok.com/get-started/your-authtoken 에서 무료 토큰 발급")
        print(f"   → 환경변수 NGROK_AUTH_TOKEN 설정 또는 .env 파일에 추가\n")
    
    print("=" * 60)
    print("🚀 BlogDex Grade API 서버 (ngrok 터널) 시작")
    print("=" * 60)
    print(f"📍 로컬 주소: http://localhost:{port}")
    print(f"⏳ ngrok 터널 생성 중...")
    
    try:
        # ngrok 터널 생성
        public_url = ngrok.connect(port, bind_tls=True)  # HTTPS 터널 생성
        
        print(f"\n✅ ngrok 터널 생성 완료!")
        print("=" * 60)
        print(f"🌐 외부 접속 URL (HTTPS):")
        print(f"   {public_url}")
        print(f"\n📚 API 문서:")
        print(f"   {public_url}/docs")
        print(f"\n🔍 헬스체크:")
        print(f"   {public_url}/health")
        print("=" * 60)
        print(f"\n💡 이 URL을 외부 서버에 전달하면 인터넷 어디서든 접속 가능합니다!")
        print(f"⚠️  서버를 종료하려면 Ctrl+C를 누르세요.")
        print(f"⚠️  무료 플랜: 매번 재시작시 URL이 변경됩니다.\n")
        
        # FastAPI 서버를 메인 스레드에서 실행 (블로킹)
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 서버 종료 중...")
        ngrok.kill()
        print("✅ ngrok 터널 종료 완료")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        ngrok.kill()
        sys.exit(1)

if __name__ == "__main__":
    main()

