"""
BlogDex 페이지의 실제 HTML 구조 확인용 디버깅 스크립트
"""
import time
from crawler import create_undetected_driver, load_cookies, verify_login_status
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_page_structure():
    print("=== BlogDex 페이지 구조 디버깅 시작 ===\n")

    # 드라이버 생성
    driver = create_undetected_driver()
    if not driver:
        print("[ERROR] 드라이버 생성 실패")
        return

    try:
        # BlogDex 접속
        print("[1단계] BlogDex 홈페이지 접속...")
        driver.get("https://blogdex.space/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2)
        print("✅ 페이지 로딩 완료\n")

        # 쿠키 로드
        print("[2단계] 쿠키 로드 및 로그인...")
        cookie_loaded = load_cookies(driver, "cookies.pkl")
        if cookie_loaded:
            driver.refresh()
            time.sleep(2)

            if verify_login_status(driver):
                print("✅ 로그인 성공\n")
            else:
                print("❌ 로그인 실패 - 수동으로 로그인 필요\n")
                print("60초 대기 중... 브라우저에서 수동으로 로그인하세요.")
                time.sleep(60)

        # 페이지 HTML 구조 분석
        print("[3단계] input 태그 검색...\n")

        # 모든 input 태그 찾기
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"총 {len(all_inputs)}개의 input 태그 발견:\n")

        for idx, input_elem in enumerate(all_inputs, 1):
            try:
                tag_type = input_elem.get_attribute("type")
                placeholder = input_elem.get_attribute("placeholder")
                class_name = input_elem.get_attribute("class")
                is_displayed = input_elem.is_displayed()
                is_enabled = input_elem.is_enabled()

                print(f"[Input {idx}]")
                print(f"  - Type: {tag_type}")
                print(f"  - Placeholder: {placeholder}")
                print(f"  - Class: {class_name}")
                print(f"  - Displayed: {is_displayed}")
                print(f"  - Enabled: {is_enabled}")
                print()
            except Exception as e:
                print(f"[Input {idx}] 정보 추출 실패: {e}\n")

        # 추가: main 태그 내부 확인
        print("\n[4단계] main 태그 내부 구조 확인...\n")
        try:
            main_element = driver.find_element(By.TAG_NAME, "main")
            main_html = main_element.get_attribute("innerHTML")[:1000]  # 처음 1000자
            print("Main 태그 내부 HTML (처음 1000자):")
            print(main_html)
            print()
        except Exception as e:
            print(f"Main 태그 찾기 실패: {e}\n")

        # 페이지 소스 일부 저장
        print("\n[5단계] 페이지 소스 저장...")
        page_source = driver.page_source
        with open("blogdex_page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("✅ 페이지 소스가 blogdex_page_source.html에 저장되었습니다.")

        print("\n=== 디버깅 완료 ===")
        print("브라우저는 60초 후 자동으로 종료됩니다.")
        time.sleep(60)

    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("드라이버 종료")

if __name__ == "__main__":
    debug_page_structure()
