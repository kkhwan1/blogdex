"""
ngrok 외부 URL로 API 테스트
"""
import requests
import json

# ngrok 공개 URL
NGROK_URL = "https://4854ad321056.ngrok-free.app"

def test_health():
    print("=" * 60)
    print("🔍 헬스체크 테스트")
    print("=" * 60)
    response = requests.get(f"{NGROK_URL}/health")
    print(f"상태 코드: {response.status_code}")
    print(f"응답:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_single_url():
    print("=" * 60)
    print("📍 단일 URL 테스트")
    print("=" * 60)
    test_url = "https://blog.naver.com/nyang2ne/224038751161"
    print(f"테스트 URL: {test_url}")
    print(f"⏳ 크롤링 중... (30-40초 소요)")
    
    response = requests.post(
        f"{NGROK_URL}/api/blog/grade",
        json={"url": test_url},
        timeout=60
    )
    
    print(f"\n상태 코드: {response.status_code}")
    print(f"응답:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    print("\n🚀 ngrok 외부 접속 API 테스트 시작\n")
    print(f"📡 ngrok URL: {NGROK_URL}\n")
    
    # 1. 헬스체크
    test_health()
    
    # 2. 단일 URL 테스트 (시간이 오래 걸리므로 사용자가 원할 경우에만)
    user_input = input("블로그 등급 조회 테스트를 진행하시겠습니까? (y/n): ")
    if user_input.lower() == 'y':
        test_single_url()
    else:
        print("✅ 헬스체크만 완료했습니다!")
    
    print("=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    print(f"\n💡 이 URL을 다른 서버나 컴퓨터에서도 사용할 수 있습니다:")
    print(f"   {NGROK_URL}/docs")
    print(f"\n⚠️  주의: 서버를 재시작하면 URL이 변경됩니다.\n")

