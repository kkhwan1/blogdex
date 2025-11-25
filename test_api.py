"""
API 테스트 스크립트
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_single_url():
    """단일 URL 테스트"""
    print("\n" + "=" * 60)
    print("📍 단일 URL 테스트")
    print("=" * 60)
    
    url = "https://blog.naver.com/nyang2ne/224038751161"
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/blog/grade",
        json={"url": url}
    )
    elapsed_time = time.time() - start_time
    
    print(f"✅ 응답 시간: {elapsed_time:.2f}초")
    print(f"📊 결과:")
    result = response.json()
    print(f"  - URL: {result['url']}")
    print(f"  - Level: {result['level']}")
    print(f"  - Success: {result['success']}")
    
    return result

def test_batch_urls():
    """다수 URL 일괄 테스트"""
    print("\n" + "=" * 60)
    print("📍 다수 URL 일괄 테스트 (2개)")
    print("=" * 60)
    
    urls = [
        "https://blog.naver.com/nyang2ne/224038751161",
        "https://blog.naver.com/nyang2ne/224038751161"  # 동일 URL 재테스트
    ]
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/blog/grades",
        json={"urls": urls}
    )
    elapsed_time = time.time() - start_time
    
    print(f"✅ 응답 시간: {elapsed_time:.2f}초")
    print(f"📊 결과:")
    results = response.json()
    for idx, result in enumerate(results, 1):
        print(f"\n  [{idx}] {result['url']}")
        print(f"      Level: {result['level']}")
        print(f"      Success: {result['success']}")
    
    return results

if __name__ == "__main__":
    print("🚀 BlogDex API 테스트 시작")
    
    try:
        # 헬스 체크
        health = requests.get(f"{BASE_URL}/health").json()
        print(f"\n✅ 서버 상태: {health['status']}")
        print(f"📊 최대 동시 처리: {health['max_concurrent']}개")
        
        # 단일 URL 테스트
        test_single_url()
        
        # 잠시 대기
        print("\n⏳ 2초 대기 중...")
        time.sleep(2)
        
        # 다수 URL 테스트
        test_batch_urls()
        
        print("\n" + "=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")

