"""
크롤링 + 파일 저장 통합 테스트
"""
import sys
import io

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path
from crawler import crawl_blog_grade

def main():
    # 테스트용 블로그 URL
    test_url = "https://blog.naver.com/nightd/224041403656"

    print("=" * 60)
    print("크롤링 + 파일 저장 통합 테스트")
    print("=" * 60)
    print(f"\n테스트 URL: {test_url}\n")

    try:
        # 크롤링 실행
        result = crawl_blog_grade(test_url)

        print("\n" + "=" * 60)
        print("크롤링 결과")
        print("=" * 60)

        if result:
            print(f"\nSuccess: {result.get('success')}")
            print(f"URL: {result.get('url')}")
            print(f"Blog ID: {result.get('blog_id')}")
            print(f"Grade: {result.get('grade')}")
            print(f"Level: {result.get('level')}")
            print(f"Tier: {result.get('tier')}")
            print(f"Timestamp: {result.get('timestamp')}")
            print(f"File Path: {result.get('file_path')}")

            # 저장된 파일 확인
            file_path = result.get('file_path')
            if file_path and Path(file_path).exists():
                print(f"\n✅ 파일 저장 확인: {file_path}")

                # 파일 내용 읽기
                with open(file_path, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)

                print("\n저장된 파일 내용:")
                print(json.dumps(saved_data, ensure_ascii=False, indent=2))

                # 검증
                assert saved_data['url'] == result['url']
                assert saved_data['success'] == result['success']
                print("\n✅ 파일 내용 검증 성공")

                if result.get('success'):
                    print("\n[SUCCESS] 크롤링 + 저장 완료!")
                    return 0
                else:
                    print("\n[FAILED] 크롤링 실패")
                    return 1
            else:
                print(f"\n❌ 파일 저장 실패: {file_path}")
                return 1
        else:
            print("\n❌ 크롤링 결과 없음")
            return 1

    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("=" * 60)

if __name__ == "__main__":
    sys.exit(main())
