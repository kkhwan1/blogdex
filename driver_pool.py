"""
Chrome 드라이버 풀 관리
서버 시작 시 미리 생성된 드라이버를 재사용하여 성능 향상
"""

from queue import Queue, Empty
import threading
import time
import logging

logger = logging.getLogger(__name__)


class DriverPool:
    """Chrome 드라이버 풀 관리 클래스"""

    def __init__(self, size=3):
        """
        Args:
            size: 풀에 유지할 드라이버 개수 (기본 3개)
        """
        self.pool = Queue(maxsize=size)
        self.size = size
        self.lock = threading.Lock()
        self.initialized = False

    def initialize(self):
        """
        서버 시작 시 드라이버 풀 초기화
        각 드라이버를 생성하고 BlogDex에 로그인까지 완료
        """
        if self.initialized:
            print("[INFO] 드라이버 풀이 이미 초기화되어 있습니다")
            return

        with self.lock:
            if self.initialized:
                return

            print(f"[INFO] 드라이버 풀 초기화 시작... (크기: {self.size})")

            from crawler import create_undetected_driver, load_cookies, verify_login_status, save_cookies, login_google
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys

            for i in range(self.size):
                try:
                    print(f"[INFO] 드라이버 {i+1}/{self.size} 생성 중...")

                    # 드라이버 생성
                    driver = create_undetected_driver()
                    if not driver:
                        print(f"[ERROR] 드라이버 {i+1} 생성 실패")
                        continue

                    # BlogDex 접속
                    driver.get("https://blogdex.space/")
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                    # 쿠키 로드 및 로그인 확인
                    cookie_loaded = load_cookies(driver, "cookies.pkl")
                    logged_in = False

                    if cookie_loaded:
                        driver.refresh()
                        time.sleep(1)

                        if verify_login_status(driver):
                            logged_in = True
                            print(f"[INFO] 드라이버 {i+1} 쿠키 로그인 성공")
                            time.sleep(2)  # 페이지 안정화

                    # 로그인 안 되어있으면 스킵 (첫 드라이버만 로그인 시도)
                    if not logged_in and i == 0:
                        print(f"[WARNING] 드라이버 {i+1} 로그인 필요 - 수동 로그인 후 재시작 필요")
                        # 첫 드라이버는 로그인 안 되어도 풀에 추가 (나중에 수동 로그인 가능)

                    # 메인 페이지로 이동
                    driver.get("https://blogdex.space/")
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                    # 풀에 추가
                    self.pool.put(driver)
                    print(f"[INFO] 드라이버 {i+1}/{self.size} 초기화 완료")

                except Exception as e:
                    print(f"[ERROR] 드라이버 {i+1} 초기화 실패: {e}")
                    import traceback
                    traceback.print_exc()

            self.initialized = True
            print(f"[INFO] 드라이버 풀 초기화 완료 (사용 가능: {self.pool.qsize()}/{self.size})")

    def get(self, timeout=30):
        """
        풀에서 드라이버 가져오기

        Args:
            timeout: 대기 시간 (초)

        Returns:
            driver: Chrome 드라이버 인스턴스

        Raises:
            TimeoutError: 타임아웃 시
        """
        if not self.initialized:
            raise RuntimeError("드라이버 풀이 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")

        try:
            driver = self.pool.get(timeout=timeout)
            print(f"[INFO] 드라이버 풀에서 가져옴 (남은 개수: {self.pool.qsize()}/{self.size})")
            return driver
        except Empty:
            raise TimeoutError(f"드라이버 풀에서 드라이버를 가져오는 데 {timeout}초 동안 실패했습니다")

    def put(self, driver):
        """
        드라이버를 풀에 반환

        Args:
            driver: 반환할 드라이버
        """
        try:
            # 드라이버 상태 확인
            driver.current_url  # 연결 확인용

            # 메인 페이지로 이동 (다음 사용을 위해)
            try:
                driver.get("https://blogdex.space/")
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC

                # 🔥 Phase 4: 메인 검색 필드만 정확히 타겟팅 (디버그 스크립트 결과 기반)
                url_input_selectors = [
                    "input[placeholder='블로그 주소/아이디를 입력하세요.']",
                    "input.h-14[type='text']",
                    "input[type='text'][placeholder*='블로그 주소/아이디']",
                    "main section input[type='text']"
                ]

                input_found = False
                for selector in url_input_selectors:
                    try:
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if element.is_displayed() and element.is_enabled():
                            input_found = True
                            logger.info(f"✅ 드라이버 풀 반환: 페이지 준비 완료")
                            break
                    except:
                        continue

                if not input_found:
                    logger.warning(f"⚠️ 드라이버 풀 반환: URL 입력 필드 대기 타임아웃 (fallback to body)")
                    # Fallback: body 태그만이라도 확인
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                # 🔥 Codex 제안: 드라이버 반환 전 로그인 상태 확인 (필수!)
                from crawler import verify_login_status
                if not verify_login_status(driver):
                    logger.error("❌ 드라이버 풀 반환: 로그인 세션 만료 감지 - 드라이버 폐기")
                    raise Exception("로그인 세션 만료")

                logger.info("✅ 드라이버 풀 반환: 로그인 상태 정상")

            except Exception as e:
                logger.warning(f"⚠️ 드라이버 풀 반환: 페이지 이동 실패 - {str(e)[:50]}")
                # 로그인 세션 만료 시 드라이버 손상으로 처리 (재생성 트리거)
                raise Exception(f"드라이버 반환 실패: {str(e)[:30]}")

            self.pool.put(driver)
            logger.info(f"✅ 드라이버 풀에 반환 (현재 개수: {self.pool.qsize()}/{self.size})")

        except Exception as e:
            print(f"[ERROR] 드라이버 손상 감지: {e}")
            # 손상된 드라이버는 정리하고 새로 생성
            try:
                driver.quit()
            except:
                pass

            # 새 드라이버 생성 시도
            try:
                print("[INFO] 새 드라이버 생성 중...")
                from crawler import create_undetected_driver, load_cookies, verify_login_status
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC

                new_driver = create_undetected_driver()

                if new_driver:
                    # 🔥 중요: BlogDex 접속 및 쿠키 로그인
                    new_driver.get("https://blogdex.space/")
                    WebDriverWait(new_driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                    # 쿠키 로드 및 로그인 확인
                    cookie_loaded = load_cookies(new_driver, "cookies.pkl")
                    logged_in = False

                    if cookie_loaded:
                        new_driver.refresh()
                        time.sleep(1)

                        if verify_login_status(new_driver):
                            logged_in = True
                            print(f"[INFO] 새 드라이버 쿠키 로그인 성공")
                            time.sleep(2)  # 페이지 안정화

                    if not logged_in:
                        print("[WARNING] 새 드라이버 로그인 실패 - 인증되지 않은 드라이버는 풀에 추가하지 않음")
                        new_driver.quit()
                        print("[ERROR] 새 드라이버 폐기 - 풀 크기 감소")
                        return

                    # 메인 페이지로 이동 및 URL 입력 필드 대기
                    new_driver.get("https://blogdex.space/")

                    # 🔥 Phase 4: 메인 검색 필드만 정확히 타겟팅 (디버그 스크립트 결과 기반)
                    url_input_selectors = [
                        "input[placeholder='블로그 주소/아이디를 입력하세요.']",
                        "input.h-14[type='text']",
                        "input[type='text'][placeholder*='블로그 주소/아이디']",
                        "main section input[type='text']"
                    ]
                    input_found = False
                    for selector in url_input_selectors:
                        try:
                            element = WebDriverWait(new_driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            if element.is_displayed() and element.is_enabled():
                                input_found = True
                                logger.info(f"✅ 새 드라이버: URL 입력 필드 준비 완료")
                                break
                        except:
                            continue

                    if not input_found:
                        logger.warning("⚠️ 새 드라이버: URL 입력 필드 대기 타임아웃 (fallback to body)")
                        # Fallback
                        WebDriverWait(new_driver, 5).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )

                    self.pool.put(new_driver)
                    print("[INFO] 새 드라이버 생성 및 풀에 추가 완료")
                else:
                    print("[ERROR] 새 드라이버 생성 실패 - 풀 크기 감소")
            except Exception as e2:
                print(f"[ERROR] 새 드라이버 생성 실패: {e2}")
                import traceback
                traceback.print_exc()

    def cleanup(self):
        """
        서버 종료 시 모든 드라이버 정리
        """
        print("[INFO] 드라이버 풀 정리 시작...")

        cleaned = 0
        while not self.pool.empty():
            try:
                driver = self.pool.get_nowait()
                driver.quit()
                cleaned += 1
                print(f"[INFO] 드라이버 {cleaned} 정리 완료")
            except Exception as e:
                print(f"[ERROR] 드라이버 정리 실패: {e}")

        print(f"[INFO] 드라이버 풀 정리 완료 (총 {cleaned}개)")
        self.initialized = False


# 글로벌 드라이버 풀 인스턴스
driver_pool = DriverPool(size=3)
