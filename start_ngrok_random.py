"""
포트 8000용 랜덤 도메인 ngrok 터널 생성 스크립트
"""

import os
import sys
from pyngrok import ngrok, conf
from dotenv import load_dotenv

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# .env 파일 로드
load_dotenv()

def main():
    # ngrok 인증 토큰 설정
    ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
    if ngrok_auth_token:
        conf.get_default().auth_token = ngrok_auth_token
        print("[OK] ngrok auth token configured")
    else:
        print("[WARNING] ngrok auth token not found (free plan limitations)")

    print("=" * 60)
    print("Creating ngrok tunnel for port 8000...")
    print("=" * 60)

    try:
        # 랜덤 도메인으로 터널 생성 (도메인 지정 안 함)
        public_url = ngrok.connect(8000, bind_tls=True)

        print(f"\n[SUCCESS] ngrok tunnel created!")
        print("=" * 60)
        print(f"Public URL (HTTPS):")
        print(f"   {public_url}")
        print(f"\nAPI Documentation:")
        print(f"   {public_url}/docs")
        print(f"\nHealth Check:")
        print(f"   {public_url}/health")
        print("=" * 60)
        print(f"\nThis URL is accessible from anywhere on the internet!")
        print(f"Press Ctrl+C to stop the tunnel.\n")

        # 터널 유지
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping tunnel...")
        ngrok.kill()
        print("Tunnel stopped successfully")
    except Exception as e:
        print(f"\nError: {e}")
        ngrok.kill()

if __name__ == "__main__":
    main()
