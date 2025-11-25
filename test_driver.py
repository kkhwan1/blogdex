"""
드라이버 생성 테스트 스크립트
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import undetected_chromedriver as uc

def test_driver():
    """드라이버 생성 테스트"""
    print("=" * 60)
    print("Testing undetected-chromedriver...")
    print("=" * 60)

    try:
        print("\n[1/3] Creating ChromeOptions...")
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        print("[OK] ChromeOptions created")

        print("\n[2/3] Creating Chrome driver...")
        driver = uc.Chrome(
            options=options,
            use_subprocess=False,
            version_main=141  # Chrome 141 버전 명시
        )
        print("[OK] Chrome driver created successfully!")

        print("\n[3/3] Testing driver...")
        driver.get("https://www.google.com")
        print(f"[OK] Current URL: {driver.current_url}")
        print(f"[OK] Title: {driver.title}")

        print("\n" + "=" * 60)
        print("[SUCCESS] Driver test completed!")
        print("=" * 60)

        driver.quit()
        return True

    except Exception as e:
        print(f"\n[ERROR] Driver test failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_driver()
