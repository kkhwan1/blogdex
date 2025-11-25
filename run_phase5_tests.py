"""Phase 5: 10회 테스트 배터리 실행 스크립트"""
import requests
import json
import time

def run_tests():
    print("=== Phase 5: 10회 테스트 배터리 시작 ===\n")

    urls = [
        "https://blog.naver.com/nightd",
        "https://blog.naver.com/yeonbly_b",
        "https://blog.naver.com/jaesung_lee7/223720697894",
        "https://blog.naver.com/nyang2ne",
        "https://blog.naver.com/nightd/224041403656",
        "https://blog.naver.com/jaesung_lee7",
        "https://blog.naver.com/nightd",
        "https://blog.naver.com/yeonbly_b",
        "https://blog.naver.com/nyang2ne",
        "https://blog.naver.com/jaesung_lee7"
    ]

    results = []
    success_count = 0

    for i, url in enumerate(urls, 1):
        try:
            response = requests.post(
                "http://localhost:8000/api/blog/grade",
                headers={"Content-Type": "application/json"},
                json={"url": url},
                timeout=30
            )
            data = response.json()

            status = "SUCCESS" if data.get("success") else "FAIL"
            level = data.get("level", "N/A")

            print(f"[{i}/10] {status} - {level}")

            results.append(data)
            if data.get("success"):
                success_count += 1

        except Exception as e:
            print(f"[{i}/10] ERROR - {str(e)[:30]}")
            results.append({"success": False, "error": str(e)})

        time.sleep(1)

    print(f"\n=== 테스트 완료 ===")
    print(f"성공: {success_count}/10 ({success_count*10}%)")

    return results, success_count

if __name__ == "__main__":
    results, success_count = run_tests()
