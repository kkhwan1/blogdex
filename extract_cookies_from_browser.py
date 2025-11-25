"""
현재 열려있는 Chrome 브라우저 세션에서 blogdex.space 쿠키 추출
Selenium으로 새 브라우저를 열어 수동 로그인 후 쿠키 저장
"""
import pickle
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def extract_and_save_cookies():
    """브라우저를 열고 로그인 후 쿠키 저장"""
    print("=" * 60)
    print("BlogDex 쿠키 추출 도구")
    print("=" * 60)
    print()
    print("1. 브라우저가 열립니다")
    print("2. blogdex.space에서 로그인을 완료하세요")
    print("3. 로그인 완료 후 이 창에서 Enter를 누르세요")
    print()

    # Chrome 드라이버 생성
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')

    driver = uc.Chrome(options=options, use_subprocess=False)

    try:
        # BlogDex로 이동
        print("blogdex.space로 이동 중...")
        driver.get("https://blogdex.space/")
        time.sleep(3)

        print()
        print("=" * 60)
        print("브라우저에서 로그인을 완료한 후 Enter를 누르세요...")
        print("(이미 로그인되어 있다면 바로 Enter)")
        print("=" * 60)
        input()

        # 쿠키 추출
        print("쿠키 추출 중...")
        cookies = driver.get_cookies()

        if cookies:
            # cookies.pkl로 저장
            with open('cookies.pkl', 'wb') as f:
                pickle.dump(cookies, f)

            print(f"총 {len(cookies)}개의 쿠키를 저장했습니다.")
            print()
            print("저장된 쿠키:")
            for c in cookies:
                print(f"  - {c['name']}: {c['value'][:30]}...")

            print()
            print("=" * 60)
            print("cookies.pkl 저장 완료!")
            print("이제 서버를 재시작하면 쿠키가 적용됩니다.")
            print("=" * 60)
        else:
            print("쿠키가 없습니다. 로그인을 확인하세요.")

    except Exception as e:
        print(f"오류: {e}")
    finally:
        print()
        print("브라우저를 닫으려면 Enter를 누르세요...")
        input()
        driver.quit()

if __name__ == "__main__":
    extract_and_save_cookies()
