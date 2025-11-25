"""
BlogDex 크롤링 모듈 - API 서버용
blogdex_selenium_login.py의 핵심 로직을 재사용
"""

import sys
import io
import logging

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from pathlib import Path
from dotenv import load_dotenv
import pickle

# result_store 모듈 import (등급 매핑 및 저장 기능)
from result_store import persist_result, enrich_result, get_level_info, GRADE_MAPPING

# 로거 설정
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()

def create_undetected_driver():
    """undetected-chromedriver로 Chrome 드라이버 생성"""
    try:
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Chrome 141 버전에 맞는 드라이버 사용
        driver = uc.Chrome(
            options=options,
            use_subprocess=False,
            version_main=141  # Chrome 버전 명시
        )

        return driver
    except Exception as e:
        print(f"[ERROR] 드라이버 생성 실패: {e}")
        return None

def save_cookies(driver, filepath="cookies.pkl"):
    """로그인 후 쿠키를 파일로 저장"""
    try:
        cookies = driver.get_cookies()
        with open(filepath, 'wb') as f:
            pickle.dump(cookies, f)
        return True
    except Exception as e:
        print(f"[ERROR] 쿠키 저장 실패: {e}")
        return False

def load_cookies(driver, filepath="cookies.pkl"):
    """저장된 쿠키를 로드"""
    if not Path(filepath).exists():
        return False
    
    try:
        driver.get("https://blogdex.space/")
        time.sleep(1)
        
        with open(filepath, 'rb') as f:
            cookies = pickle.load(f)
        
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass
        
        return True
    except Exception as e:
        print(f"[ERROR] 쿠키 로드 실패: {e}")
        return False

def verify_login_status(driver):
    """로그인 상태 확인 - 쿠키 기반으로 개선"""
    try:
        current_url = driver.current_url

        if "login" in current_url:
            return False

        # 쿠키 기반 로그인 확인 (user-token 또는 session-token)
        cookies = driver.get_cookies()
        cookie_names = [c.get('name', '') for c in cookies]

        # NextAuth 인증 쿠키 확인
        has_user_token = any('user-token' in name for name in cookie_names)
        has_session_token = any('session-token' in name for name in cookie_names)

        if has_user_token or has_session_token:
            print(f"[INFO] 로그인 쿠키 확인됨: user-token={has_user_token}, session-token={has_session_token}")
            return True

        print("[WARNING] 로그인 쿠키 없음")
        return False
    except Exception as e:
        print(f"[ERROR] 로그인 상태 확인 실패: {e}")
        return False

def retry_with_backoff(func, max_retries=3, backoff_factor=2, exceptions=(Exception,)):
    """
    재시도 로직 with exponential backoff

    Args:
        func: 실행할 함수 (인자 없는 람다)
        max_retries: 최대 재시도 횟수
        backoff_factor: 대기 시간 배수 (1초, 2초, 4초)
        exceptions: 재시도할 예외 타입

    Returns:
        func의 반환값

    Raises:
        마지막 시도의 예외
    """
    import time

    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries - 1:
                # 마지막 시도 실패
                raise

            wait_time = backoff_factor ** attempt
            print(f"[RETRY] {attempt + 1}/{max_retries} 실패. {wait_time}초 후 재시도... (오류: {str(e)[:50]})")
            time.sleep(wait_time)

def click_with_retry(driver, selectors, max_retries=3, wait_time=5, step_name="요소"):
    """여러 선택자로 클릭 시도"""
    for retry in range(max_retries):
        for idx, selector in enumerate(selectors, 1):
            try:
                try:
                    element = WebDriverWait(driver, wait_time).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    element.click()
                    return True
                except:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].click();", element)
                    return True
            except:
                continue
    return False

def login_google(driver):
    """구글 로그인 처리"""
    try:
        email = os.getenv('GOOGLE_EMAIL')
        password = os.getenv('GOOGLE_PASSWORD')
        
        if not email or not password:
            print("[ERROR] 구글 계정 정보가 .env 파일에 없습니다")
            return False
        
        # 이메일 입력
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(2)
        
        # 다음 버튼
        next_selectors = ["#identifierNext button", "button[jsname='LgbsSe']"]
        if not click_with_retry(driver, next_selectors, max_retries=2, step_name="이메일 다음 버튼"):
            return False
        
        time.sleep(6)
        
        # 비밀번호 입력
        try:
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            driver.execute_script(f"arguments[0].value = '{password}';", password_input)
            time.sleep(2)
        except:
            return False
        
        # 다음 버튼
        next_pw_selectors = ["#passwordNext button", "button[jsname='LgbsSe']"]
        if not click_with_retry(driver, next_pw_selectors, max_retries=2, step_name="비밀번호 다음 버튼"):
            return False
        
        time.sleep(6)
        
        # BlogDex로 리다이렉트 대기
        for _ in range(20):
            if "blogdex.space" in driver.current_url:
                time.sleep(7)
                return True
            time.sleep(1)
        
        return False
    except Exception as e:
        print(f"[ERROR] 구글 로그인 실패: {e}")
        return False

def extract_blog_grade(driver, blog_url):
    """블로그 URL의 등급을 추출"""
    try:
        logger.info(f"🚀 extract_blog_grade 시작: {blog_url}")

        # 🔥 중요: 명시적으로 BlogDex 홈페이지로 이동 (드라이버 풀에서 받은 드라이버는 다른 페이지에 있을 수 있음)
        if "blogdex.space" not in driver.current_url or "/blog/" in driver.current_url:
            logger.info(f"📍 현재 URL: {driver.current_url} → BlogDex 홈으로 이동")
            driver.get("https://blogdex.space/")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # 페이지 안정화 대기
            logger.info("✅ BlogDex 홈페이지 로딩 완료")

        # 마우스 스크롤
        actions = ActionChains(driver)
        actions.move_by_offset(0, 10).perform()
        time.sleep(1)

        # 🔥 Phase 4: 메인 검색 필드만 정확히 타겟팅 (디버그 스크립트 결과 기반)
        #  [Input 1] - placeholder="블로그 주소/아이디를 입력하세요.", class contains w-[310px], md:w-[450px], lg:w-[550px]
        url_input_selectors = [
            # 메인 검색 필드 - 정확한 placeholder 텍스트
            "input[placeholder='블로그 주소/아이디를 입력하세요.']",
            # 너비 클래스로 구분 (w-[310px])
            "input.h-14[type='text']",  # h-14 클래스도 메인 필드의 특징
            # placeholder 부분 일치 (두 번째 입력 필드와 구분하기 위해 더 구체적)
            "input[type='text'][placeholder*='블로그 주소/아이디']",
            # 구조 기반 백업
            "main section input[type='text']",
            "main input[placeholder]"
        ]

        url_input = None
        for selector in url_input_selectors:
            try:
                # 🔥 Codex 제안: visibility_of_element_located 사용 (hidden 요소 재시도)
                url_input = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                # 추가 확인: 상호작용 가능한지 검증
                if url_input.is_enabled():
                    logger.info(f"✅ URL 입력 필드 찾음: {selector[:50]}...")
                    break
                else:
                    url_input = None
                    continue
            except Exception as e:
                logger.debug(f"❌ URL 입력 필드 셀렉터 실패: {selector[:30]}... - {str(e)[:30]}")
                continue

        if not url_input:
            logger.error("❌ 모든 URL 입력 필드 셀렉터 실패")
            raise Exception("URL 입력 필드를 찾을 수 없음")

        url_input.clear()
        url_input.click()
        url_input.send_keys(blog_url)

        # React 이벤트 트리거
        driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, url_input)

        time.sleep(0.5)

        # 🔥 새로운 방식: Enter 키로 검색 실행 (검색 버튼 클릭 로직 제거)
        from selenium.webdriver.common.keys import Keys
        url_input.send_keys(Keys.RETURN)
        logger.info("✅ Enter 키 입력 완료 (검색 실행)")

        # 페이지 렌더링 대기 (document.readyState 확인)
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.info("✅ 페이지 렌더링 완료")
        except Exception as e:
            logger.warning(f"⚠️ 페이지 렌더링 대기 타임아웃 (계속 진행): {str(e)[:50]}")

        # 🔥 Codex 제안: 추가 안정화 대기 증가 (2초 → 5초, BlogDex React 렌더링 완료 대기)
        time.sleep(5)

        # 🔥 SVG text 셀렉터 최적화 (속성 기반)
        grade_selectors = [
            # 속성 기반 셀렉터 (가장 안정적 - Pretendard 폰트 사용)
            "svg text[font-family='Pretendard']",
            "svg text[font-weight='700']",
            "svg text[font-size='22px']",
            # nth-child 기반 (기존 방식)
            "svg > text:nth-child(2)",
            "div[class*='justify-center'] svg > text:nth-child(2)",
            # 원래 셀렉터 (백업)
            "#__next > div > main > div > div.flex.flex-col.gap-4 > div:nth-child(1) > div.p-6.pt-0 > div.flex.flex-col.justify-center.space-y-12.py-5.md\\:flex-row.md\\:justify-between.md\\:space-x-0.md\\:space-y-0.md\\:py-0 > div.flex.flex-1.justify-center.px-5 > div > svg > text:nth-child(2)",
            # 넓은 범위 (마지막 백업)
            "#__next svg > text:nth-child(2)"
        ]

        grade_element = None
        last_error = None

        logger.info(f"⏱️  등급 요소 대기 시작 (최대 30초)")
        for idx, selector in enumerate(grade_selectors, 1):
            try:
                logger.debug(f"🔍 등급 셀렉터 {idx}/{len(grade_selectors)} 시도: {selector[:50]}...")
                # 🔥 중요: 대기 시간 10초 → 30초로 증가 (BlogDex 로딩 시간 고려)
                grade_element = WebDriverWait(driver, 30, poll_frequency=0.5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"✅ 등급 셀렉터 {idx} 성공!")
                break
            except Exception as e:
                last_error = e
                logger.warning(f"❌ 등급 셀렉터 {idx} 실패: {str(e)[:80]}")
                continue

        if not grade_element:
            # 수정 3: 에러 정보를 더 상세히 보존
            import traceback
            error_detail = traceback.format_exc()
            logger.error(f"❌ 모든 등급 셀렉터 실패. 마지막 에러:\n{error_detail}")
            raise Exception(f"등급 요소를 찾을 수 없음. 마지막 에러: {str(last_error)}")

        grade = grade_element.text.strip()

        if not grade:
            raise Exception("등급 텍스트가 비어있음")

        # 등급 매핑 (get_level_info 사용)
        level_info = get_level_info(grade)
        if level_info:
            level = level_info.get("level", grade)
            print(f"[DEBUG] 추출된 등급: '{grade}' → '{level}'")
            return {
                "grade": grade,
                "level": level,
                "level_en": level_info.get("level_en"),
                "tier": level_info.get("tier"),
                "tier_en": level_info.get("tier_en"),
                "tier_rank": level_info.get("tier_rank")
            }
        else:
            # 매핑 실패 시 기본값
            print(f"[DEBUG] 추출된 등급: '{grade}' (매핑 실패)")
            return {"grade": grade, "level": grade}
    except Exception as e:
        # 수정 3: 에러 정보를 상세히 출력
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] 등급 추출 실패: {e}")
        print(f"[ERROR] 상세 에러:\n{error_detail}")
        return None

def crawl_blog_grade(url: str) -> dict:
    """
    단일 URL의 블로그 등급을 크롤링

    Args:
        url: 블로그 URL

    Returns:
        {
            "url": str,
            "level": str,
            "success": bool,
            "error": str (optional)
        }
    """
    import time
    start_time = time.time()
    print(f"\n{'='*60}")
    print(f"[크롤링 시작] {url}")
    print(f"{'='*60}")

    driver = None
    try:
        # 드라이버 생성
        print("[1/5] Chrome 드라이버 생성 중...")
        driver = create_undetected_driver()
        if not driver:
            print("[ERROR] 드라이버 생성 실패")
            return {
                "url": url,
                "level": None,
                "success": False,
                "error": "드라이버 생성 실패"
            }
        print(f"[INFO] 드라이버 생성 완료 ({time.time()-start_time:.2f}초)")

        # BlogDex 접속
        print("[2/5] BlogDex 접속 중...")
        driver.get("https://blogdex.space/")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print(f"[INFO] 접속 완료 ({time.time()-start_time:.2f}초)")

        # 쿠키 로드 시도
        print("[3/5] 로그인 상태 확인 중...")
        cookie_loaded = load_cookies(driver, "cookies.pkl")
        skip_login = False

        if cookie_loaded:
            driver.refresh()
            time.sleep(1)

            if verify_login_status(driver):
                skip_login = True
                print(f"[INFO] 쿠키 로그인 성공 ({time.time()-start_time:.2f}초)")
                time.sleep(2)  # 페이지 안정화

        # 로그인 필요시
        if not skip_login:
            print("[INFO] 로그인 필요 - 구글 OAuth 시작")
            # 팝업 닫기
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(3)
            except:
                pass
            
            # 로그인 버튼들 클릭
            try:
                first_button_selector = "#radix-\\:R7336\\:"
                first_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, first_button_selector))
                )
                first_button.click()
                time.sleep(3)
                
                login_button_selector = "#radix-\\:R7336H1\\: > div:nth-child(5) > span"
                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_selector))
                )
                login_button.click()
                time.sleep(3)
                
                terms_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#terms"))
                )
                terms_button.click()
                time.sleep(3)
            except:
                pass
            
            # 구글 로그인
            google_selectors = [
                "button:has(svg[data-icon='google'])",
                "button.bg-primary:has(svg)",
                "#__next > div > main > div > div > div.grid.gap-2 > button:nth-child(1)"
            ]
            
            try:
                # 구글 버튼 클릭 재시도
                google_click_success = retry_with_backoff(
                    lambda: click_with_retry(driver, google_selectors, max_retries=1, wait_time=7),
                    max_retries=3,
                    backoff_factor=2
                )

                if google_click_success:
                    time.sleep(7)
                    print("[INFO] 구글 로그인 페이지 이동 완료")

                    # 로그인도 재시도 (최대 2회)
                    login_success = retry_with_backoff(
                        lambda: login_google(driver),
                        max_retries=2,
                        backoff_factor=3
                    )

                    if not login_success:
                        print(f"[ERROR] 구글 로그인 실패 (재시도 소진)")
                        return {
                            "url": url,
                            "level": None,
                            "success": False,
                            "error": "구글 로그인 실패 (2회 재시도 실패)"
                        }

                    print(f"[INFO] 로그인 완료 ({time.time()-start_time:.2f}초)")
                    save_cookies(driver, "cookies.pkl")

            except Exception as e:
                print(f"[ERROR] 로그인 프로세스 실패: {e}")
                return {
                    "url": url,
                    "level": None,
                    "success": False,
                    "error": f"로그인 실패: {str(e)}"
                }

        # 메인 페이지로 이동
        print("[4/5] 메인 페이지 이동 중...")
        driver.get("https://blogdex.space/")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print(f"[INFO] 메인 페이지 로드 완료 ({time.time()-start_time:.2f}초)")

        # 등급 추출 (재시도 로직 적용)
        print("[5/5] 등급 추출 중...")
        try:
            # 최대 3회 재시도
            result = retry_with_backoff(
                lambda: extract_blog_grade(driver, url),
                max_retries=3,
                backoff_factor=2
            )

            if result:
                elapsed = time.time() - start_time
                print(f"[SUCCESS] 등급: {result['grade']} → {result['level']} ({elapsed:.2f}초)")

                # 결과 데이터 구성
                response_data = enrich_result(
                    url=url,
                    grade=result.get('grade'),
                    success=True,
                    error=None
                )

                # 파일로 저장
                try:
                    file_path = persist_result(response_data)
                    if file_path:
                        response_data["file_path"] = file_path
                except Exception as e:
                    print(f"[WARNING] 파일 저장 실패 (결과는 반환): {e}")

                return response_data
            else:
                elapsed = time.time() - start_time
                print(f"[ERROR] 등급 추출 실패 (3회 재시도 소진) ({elapsed:.2f}초)")

                # 실패 결과 데이터 구성
                response_data = enrich_result(
                    url=url,
                    grade=None,
                    success=False,
                    error="등급 추출 실패 (3회 재시도 소진)"
                )

                # 실패도 파일로 저장
                try:
                    file_path = persist_result(response_data)
                    if file_path:
                        response_data["file_path"] = file_path
                except Exception as e:
                    print(f"[WARNING] 파일 저장 실패: {e}")

                return response_data
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[ERROR] 등급 추출 예외 ({elapsed:.2f}초): {e}")

            response_data = enrich_result(
                url=url,
                grade=None,
                success=False,
                error=f"등급 추출 실패: {str(e)}"
            )

            try:
                file_path = persist_result(response_data)
                if file_path:
                    response_data["file_path"] = file_path
            except:
                pass

            return response_data

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] 크롤링 예외 발생 ({elapsed:.2f}초): {e}")
        import traceback
        traceback.print_exc()

        response_data = enrich_result(
            url=url,
            grade=None,
            success=False,
            error=str(e)
        )

        try:
            file_path = persist_result(response_data)
            if file_path:
                response_data["file_path"] = file_path
        except:
            pass

        return response_data
    finally:
        if driver:
            # 1단계: 정상 종료 시도
            try:
                driver.quit()
                print("[INFO] Chrome 정상 종료")
            except Exception as e:
                print(f"[ERROR] driver.quit() 실패: {e}")

            # 2단계: 프로세스 강제 종료
            try:
                if hasattr(driver, 'service') and driver.service.process:
                    pid = driver.service.process.pid
                    driver.service.process.kill()
                    print(f"[INFO] Chrome 프로세스 강제 종료 (PID: {pid})")
            except Exception as e:
                print(f"[ERROR] 프로세스 kill 실패: {e}")

            # 3단계: OS 레벨 정리 (Windows)
            try:
                import os
                import subprocess
                if os.name == 'nt':  # Windows
                    subprocess.run(
                        ['taskkill', '/F', '/IM', 'chrome.exe', '/T'],
                        capture_output=True,
                        timeout=5
                    )
                    subprocess.run(
                        ['taskkill', '/F', '/IM', 'chromedriver.exe', '/T'],
                        capture_output=True,
                        timeout=5
                    )
                    print("[INFO] Chrome 프로세스 OS 레벨 정리 완료")
            except Exception as e:
                print(f"[ERROR] OS 레벨 정리 실패: {e}")


def crawl_blog_grade_with_pool(url: str) -> dict:
    """
    드라이버 풀을 사용한 최적화된 크롤링 (Phase 2)

    이미 생성되고 로그인된 드라이버를 재사용하여
    Chrome 생성, 접속, 로그인 단계를 생략

    Args:
        url: 블로그 URL

    Returns:
        {
            "url": str,
            "level": str,
            "success": bool,
            "error": str (optional)
        }
    """
    from driver_pool import driver_pool
    import time

    start_time = time.time()
    print(f"\n{'='*60}")
    print(f"[크롤링 시작 - 풀 사용] {url}")
    print(f"{'='*60}")

    driver = None
    try:
        # 드라이버 풀에서 가져오기
        print("[1/2] 드라이버 풀에서 가져오는 중...")
        driver = driver_pool.get(timeout=30)
        print(f"[INFO] 드라이버 준비 완료 ({time.time()-start_time:.2f}초)")

        # 이미 BlogDex 메인 페이지에 로그인된 상태
        # 바로 등급 추출 시작
        print("[2/2] 등급 추출 중...")

        try:
            # 최대 3회 재시도
            result = retry_with_backoff(
                lambda: extract_blog_grade(driver, url),
                max_retries=3,
                backoff_factor=2
            )

            if result:
                elapsed = time.time() - start_time
                print(f"[SUCCESS] 등급: {result['grade']} → {result['level']} ({elapsed:.2f}초)")

                # 결과 데이터 구성
                response_data = enrich_result(
                    url=url,
                    grade=result.get('grade'),
                    success=True,
                    error=None
                )

                # 파일로 저장
                try:
                    file_path = persist_result(response_data)
                    if file_path:
                        response_data["file_path"] = file_path
                except Exception as e:
                    print(f"[WARNING] 파일 저장 실패 (결과는 반환): {e}")

                return response_data
            else:
                elapsed = time.time() - start_time
                print(f"[ERROR] 등급 추출 실패 (3회 재시도 소진) ({elapsed:.2f}초)")

                # 실패 결과 데이터 구성
                response_data = enrich_result(
                    url=url,
                    grade=None,
                    success=False,
                    error="등급 추출 실패 (3회 재시도 소진)"
                )

                # 실패도 파일로 저장
                try:
                    file_path = persist_result(response_data)
                    if file_path:
                        response_data["file_path"] = file_path
                except Exception as e:
                    print(f"[WARNING] 파일 저장 실패: {e}")

                return response_data
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[ERROR] 등급 추출 예외 ({elapsed:.2f}초): {e}")

            response_data = enrich_result(
                url=url,
                grade=None,
                success=False,
                error=f"등급 추출 실패: {str(e)}"
            )

            try:
                file_path = persist_result(response_data)
                if file_path:
                    response_data["file_path"] = file_path
            except:
                pass

            return response_data

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] 크롤링 예외 발생 ({elapsed:.2f}초): {e}")
        import traceback
        traceback.print_exc()

        response_data = enrich_result(
            url=url,
            grade=None,
            success=False,
            error=str(e)
        )

        try:
            file_path = persist_result(response_data)
            if file_path:
                response_data["file_path"] = file_path
        except:
            pass

        return response_data
    finally:
        # 드라이버를 풀에 반환 (quit하지 않음)
        if driver:
            try:
                driver_pool.put(driver)
                print("[INFO] 드라이버 풀에 반환 완료")
            except Exception as e:
                print(f"[ERROR] 드라이버 반환 실패: {e}")

