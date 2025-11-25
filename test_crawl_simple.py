"""
간단한 크롤링 테스트 스크립트
실제 웹에서 블로그 등급을 가져오는지 확인
"""
import sys
import json
from datetime import datetime
from crawler import crawl_blog_grade

def main():
    # 테스트용 블로그 URL
    test_url = "https://blog.naver.com/nightd/224041403656"

    print("=" * 60)
    print("BlogDex Crawling Test")
    print("=" * 60)
    print(f"\nTest URL: {test_url}")
    print("\nStarting crawl...")
    print("-" * 60)

    try:
        # 크롤링 실행
        result = crawl_blog_grade(test_url)

        print("\n" + "=" * 60)
        print("CRAWLING RESULT")
        print("=" * 60)

        if result:
            print(f"\nSuccess: {result.get('success', False)}")
            print(f"URL: {result.get('url', 'N/A')}")
            print(f"Level: {result.get('level', 'N/A')}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")

            # JSON 파일로 저장
            output_file = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\nResult saved to: {output_file}")

            if result.get('success'):
                print("\n[SUCCESS] Crawling completed successfully!")
                return 0
            else:
                print("\n[FAILED] Crawling failed")
                print(f"Error: {result.get('error', 'Unknown error')}")
                return 1
        else:
            print("\n[ERROR] No result returned")
            return 1

    except Exception as e:
        print(f"\n[EXCEPTION] Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    print("=" * 60)

if __name__ == "__main__":
    sys.exit(main())
