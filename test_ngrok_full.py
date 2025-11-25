"""
ngrok 외부 URL로 전체 API 테스트
"""
import requests
import json
import time

# ngrok 공개 URL (서버 실행시 표시된 URL로 업데이트)
NGROK_URL = "https://848d68b44bf0.ngrok-free.app"

# ngrok 무료 플랜은 이 헤더가 필요합니다
HEADERS = {
    "ngrok-skip-browser-warning": "true",
    "Content-Type": "application/json"
}

def test_health():
    print("=" * 60)
    print("🔍 1단계: 헬스체크 테스트")
    print("=" * 60)
    response = requests.get(f"{NGROK_URL}/health", headers=HEADERS, timeout=10)
    print(f"✅ 상태 코드: {response.status_code}")
    print(f"📊 응답:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_single_url():
    print("=" * 60)
    print("📍 2단계: 블로그 등급 조회 테스트")
    print("=" * 60)
    test_url = "https://blog.naver.com/nyang2ne/224038751161"
    print(f"🔗 테스트 URL: {test_url}")
    print(f"⏳ 크롤링 중... (30-40초 소요)\n")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{NGROK_URL}/api/blog/grade",
            json={"url": test_url},
            headers=HEADERS,
            timeout=90  # 90초 타임아웃
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"\n✅ 상태 코드: {response.status_code}")
        print(f"⏱️  소요 시간: {elapsed:.2f}초")
        print(f"📊 응답:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        result = response.json()
        if result.get("success"):
            print(f"\n🎉 성공! 블로그 등급: {result.get('level')}")
        else:
            print(f"\n⚠️  실패: {result.get('error', '알 수 없는 오류')}")
            
    except requests.exceptions.Timeout:
        print(f"\n❌ 타임아웃: 90초 내에 응답이 없습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 ngrok 외부 접속 API 전체 테스트")
    print("=" * 60)
    print(f"📡 ngrok URL: {NGROK_URL}")
    print(f"🌐 이 URL은 인터넷 어디서든 접속 가능합니다!\n")
    
    # 1. 헬스체크
    test_health()
    
    # 2. 블로그 등급 조회
    test_single_url()
    
    print("\n" + "=" * 60)
    print("✅ 전체 테스트 완료!")
    print("=" * 60)
    print(f"\n💡 외부 서버에서 사용할 수 있는 정보:")
    print(f"   - API 엔드포인트: {NGROK_URL}/api/blog/grade")
    print(f"   - API 문서: {NGROK_URL}/docs")
    print(f"   - 헬스체크: {NGROK_URL}/health")
    print(f"\n⚠️  주의: 서버 재시작시 URL이 변경됩니다.\n")

