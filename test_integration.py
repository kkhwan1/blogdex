"""
통합 테스트: 결과 저장 기능 검증
"""
import sys
import io
import json
from pathlib import Path

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 모듈 import 테스트
try:
    print("=" * 60)
    print("통합 테스트 시작")
    print("=" * 60)

    print("\n[1/5] result_store 모듈 import 테스트...")
    from result_store import persist_result, enrich_result, get_level_info, GRADE_MAPPING
    print("✅ result_store 모듈 import 성공")

    print("\n[2/5] crawler 모듈 import 테스트...")
    from crawler import crawl_blog_grade
    print("✅ crawler 모듈 import 성공")

    print("\n[3/5] api_server 모듈 import 테스트...")
    from api_server import app, GradeResponse
    print("✅ api_server 모듈 import 성공")

    print("\n[4/5] 등급 매핑 테스트...")
    test_grade = "최적2+"
    level_info = get_level_info(test_grade)
    assert level_info is not None
    assert level_info["level"] == "엑스퍼트3"
    print(f"✅ 등급 매핑 성공: {test_grade} → {level_info['level']}")

    print("\n[5/5] 결과 저장 기능 테스트...")
    test_data = enrich_result(
        url="https://blog.naver.com/test/123",
        grade="최적2+",
        success=True,
        error=None
    )

    print(f"   테스트 데이터:")
    print(f"   - URL: {test_data['url']}")
    print(f"   - Grade: {test_data['grade']}")
    print(f"   - Level: {test_data['level']}")
    print(f"   - Tier: {test_data['tier']}")
    print(f"   - Success: {test_data['success']}")

    file_path = persist_result(test_data, output_dir="data/json_results_test")
    if file_path:
        print(f"✅ 파일 저장 성공: {file_path}")

        # 저장된 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        # 검증
        assert saved_data['url'] == test_data['url']
        assert saved_data['grade'] == test_data['grade']
        assert saved_data['level'] == test_data['level']
        print("✅ 저장된 데이터 검증 성공")

        # 테스트 파일 삭제
        Path(file_path).unlink()
        Path("data/json_results_test").rmdir()
        print("✅ 테스트 파일 정리 완료")
    else:
        print("❌ 파일 저장 실패")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ 모든 통합 테스트 통과!")
    print("=" * 60)
    sys.exit(0)

except Exception as e:
    print(f"\n❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
