"""
BlogDex 사이트를 여는 셀레니움 스크립트 (undetected-chromedriver 사용)
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import json
import sys
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def create_undetected_driver():
    """undetected-chromedriver로 Chrome 드라이버 생성 (Cloudflare 우회)"""
    try:
        print("undetected-chromedriver 설정 중...")
        
        options = uc.ChromeOptions()
        # options.add_argument('--headless')  # 백그라운드 실행 (필요시 주석 해제)
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # undetected-chromedriver로 드라이버 생성
        # version_main 옵션으로 버전 자동 감지 사용
        # use_subprocess=False로 변경하여 안정성 향상
        driver = uc.Chrome(
            options=options,
            use_subprocess=False,
            version_main=None  # 자동 감지
        )
        
        print("✅ undetected-chromedriver 생성 완료 (Cloudflare 우회)")
        return driver
        
    except Exception as e:
        print(f"❌ undetected-chromedriver 생성 실패: {e}")
        return None

def input_blog_url(driver, blog_url):
    """블로그 URL을 입력하고 검색"""
    try:
        print(f"블로그 URL 입력 중: {blog_url}")

        # 페이지 로딩 대기 (충분한 시간)
        print("입력 필드 로딩 대기 중... (5초)")
        time.sleep(5)

        # URL 입력 필드 찾기 (visibility 체크로 변경)
        print("URL 입력 필드를 찾는 중...")
        try:
            # 사용자 제공 셀렉터 사용
            url_input = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR,
                    "#__next > div > main > section.space-y-6.pb-12.pt-8.lg\\:py-28 > div > div.flex.flex-col.items-center > div.flex.animate-fade-up.justify-center.space-x-2.opacity-0.md\\:space-x-4 > div > div > input"))
            )
            print("✅ URL 입력 필드 발견 (사용자 제공 셀렉터)")
        except Exception as e:
            print(f"사용자 제공 셀렉터 실패: {e}")
            # 대안 셀렉터들 시도
            alternative_selectors = [
                "input[placeholder*='URL'], input[placeholder*='url'], input[placeholder*='블로그']",
                "input[type='text']",
                "input",
                "[class*='input'] input"
            ]
            
            for i, selector in enumerate(alternative_selectors, 1):
                try:
                    print(f"대안 셀렉터 {i} 시도 중...")
                    url_input = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ URL 입력 필드 발견 (대안 셀렉터 {i})")
                    break
                except Exception as e2:
                    print(f"대안 셀렉터 {i} 실패: {e2}")
                    if i == len(alternative_selectors):
                        raise Exception("모든 셀렉터 실패")

        # 스크롤하여 요소를 뷰포트 중앙으로
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", url_input)
        time.sleep(1)

        # 필드 클리어 (기존 값 제거)
        url_input.clear()
        time.sleep(0.3)

        # 필드 클릭 및 포커스
        print("URL 입력 필드 클릭 및 포커스...")
        url_input.click()
        time.sleep(0.3)
        
        # 실제 타이핑 시뮬레이션 (React state 업데이트)
        print("URL 입력 중... (실제 타이핑 방식)")
        url_input.send_keys(blog_url)
        time.sleep(0.5)
        
        # 입력 후 값 확인
        try:
            input_value = url_input.get_attribute("value")
            print(f"입력된 URL 값: {input_value}")
            
            if input_value == blog_url:
                print("✅ URL 값 검증 성공")
            else:
                print(f"⚠️ URL 값 불일치: 예상={blog_url}, 실제={input_value}")
        except Exception as e:
            print(f"입력값 확인 실패: {e}")

        # React 이벤트 트리거 (추가 보장)
        driver.execute_script("""
            const element = arguments[0];
            
            // input 이벤트
            const inputEvent = new Event('input', { bubbles: true });
            element.dispatchEvent(inputEvent);
            
            // change 이벤트
            const changeEvent = new Event('change', { bubbles: true });
            element.dispatchEvent(changeEvent);
            
            // blur 이벤트 (입력 완료)
            const blurEvent = new FocusEvent('blur', { bubbles: true });
            element.dispatchEvent(blurEvent);
        """, url_input)
        time.sleep(1)

        print("✅ URL 입력 완료 (이벤트 트리거 포함)")

        # 검색 실행 (여러 방법 시도)
        search_success = False
        
        # 방법 1: Enter 키 입력
        print("Enter 키로 검색 실행 중...")
        url_input.send_keys(Keys.RETURN)
        time.sleep(3)  # 검색 실행 대기 시간 증가
        
        # URL 변경 확인
        current_url_after_enter = driver.current_url
        print(f"Enter 키 후 현재 URL: {current_url_after_enter}")
        
        # 검색 성공 여부 확인
        if "search" in current_url_after_enter.lower() or current_url_after_enter != "https://blogdex.space/":
            print("✅ Enter 키로 검색 실행 성공")
            search_success = True
        
        # Enter 키로 검색이 안되면 버튼 클릭 시도
        if not search_success:
            print("Enter 키로 검색이 실행되지 않음, 검색 버튼 클릭 시도...")
            
            button_strategies = [
                ("button[type='submit']", "submit 버튼"),
                ("button:has(svg)", "SVG 포함 버튼"),
                ("form button", "form 내부 버튼"),
            ]
            
            for selector, description in button_strategies:
                try:
                    print(f"시도 중: {description} ({selector})")
                    search_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    # JavaScript 클릭 (더 안정적)
                    driver.execute_script("arguments[0].click();", search_button)
                    print(f"✅ {description} 클릭 완료")
                    time.sleep(3)
                    
                    # 검색 성공 확인
                    current_url = driver.current_url
                    if "search" in current_url.lower() or current_url != "https://blogdex.space/":
                        print(f"✅ {description}로 검색 실행 성공")
                        search_success = True
                        break
                    
                except TimeoutException:
                    print(f"⚠️ {description} 찾을 수 없음")
                except Exception as e:
                    print(f"⚠️ {description} 클릭 실패: {e}")
            
            # 모든 버튼 전략 실패 시 input 근처 버튼 찾기
            if not search_success:
                try:
                    print("input 필드 근처의 모든 버튼 찾기...")
                    # input의 조상 요소에서 버튼 찾기
                    parent_container = url_input.find_element(By.XPATH, "../..")
                    nearby_buttons = parent_container.find_elements(By.TAG_NAME, "button")
                    
                    if nearby_buttons:
                        print(f"발견된 버튼 수: {len(nearby_buttons)}")
                        for idx, btn in enumerate(nearby_buttons):
                            try:
                                print(f"버튼 {idx+1} 클릭 시도...")
                                driver.execute_script("arguments[0].click();", btn)
                                time.sleep(3)
                                
                                current_url = driver.current_url
                                if "search" in current_url.lower() or current_url != "https://blogdex.space/":
                                    print(f"✅ 근처 버튼 {idx+1}로 검색 실행 성공")
                                    search_success = True
                                    break
                            except Exception as e:
                                print(f"버튼 {idx+1} 클릭 실패: {e}")
                    else:
                        print("근처에 버튼이 없음")
                        
                except Exception as e:
                    print(f"근처 버튼 찾기 실패: {e}")
        
        if not search_success:
            print("⚠️ 모든 검색 실행 방법 실패")
        
        # 검색 실행 최종 확인
        final_url = driver.current_url
        print(f"최종 현재 URL: {final_url}")
        
        if not search_success:
            print("❌ 검색 실행 실패")
            return False
        
        print("✅ 블로그 URL 검색 실행 완료")
        
        # 검색 결과 페이지 로딩 대기 (여러 방법으로 확인)
        print("검색 결과 로딩 대기 중...")
        result_loaded = False
        
        # 방법 1: SVG 요소 대기
        try:
            print("SVG 요소 대기 중...")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg text"))
            )
            print("✅ SVG 요소 발견 - 결과 페이지 로딩 완료")
            result_loaded = True
        except TimeoutException:
            print("⚠️ SVG 요소 타임아웃")
        
        # 방법 2: 특정 텍스트 패턴 확인 (등급 정보)
        if not result_loaded:
            try:
                print("등급 정보 텍스트 패턴 확인 중...")
                grade_pattern_found = driver.execute_script("""
                    const bodyText = document.body.innerText;
                    return /준?최[적상하]?\\d\\+?/.test(bodyText);
                """)
                if grade_pattern_found:
                    print("✅ 등급 패턴 발견 - 결과 페이지 로딩 완료")
                    result_loaded = True
                else:
                    print("⚠️ 등급 패턴 미발견")
            except Exception as e:
                print(f"등급 패턴 확인 실패: {e}")
        
        # 방법 3: URL 변경 확인
        if not result_loaded:
            if "search" in final_url.lower() or final_url != "https://blogdex.space/":
                print("✅ URL 변경 확인 - 검색 결과 페이지로 이동")
                result_loaded = True
                # 추가 로딩 대기
                time.sleep(3)
            else:
                print("⚠️ URL 변경 없음")
        
        # 페이지 상태 로깅
        try:
            page_title = driver.title
            print(f"현재 페이지 제목: {page_title}")
            
            # SVG 요소 존재 확인
            svg_elements = driver.find_elements(By.CSS_SELECTOR, "svg")
            print(f"페이지의 SVG 요소 수: {len(svg_elements)}")
            
        except Exception as e:
            print(f"페이지 상태 확인 중 오류: {e}")
        
        if result_loaded:
            print("✅ 검색 결과 페이지 로딩 확인 완료")
            return True
        else:
            print("⚠️ 검색 결과 페이지 로딩 확인 실패 (계속 진행)")
            return True  # 경고만 하고 계속 진행

    except Exception as e:
        print(f"❌ 블로그 URL 입력 실패: {e}")
        return False

def save_cookies(driver, filepath="cookies.pkl"):
    """로그인 후 쿠키를 파일로 저장"""
    try:
        import pickle
        cookies = driver.get_cookies()
        with open(filepath, 'wb') as f:
            pickle.dump(cookies, f)
        print(f"✅ 쿠키 저장 완료: {filepath}")
        return True
    except Exception as e:
        print(f"❌ 쿠키 저장 실패: {e}")
        return False

def load_cookies(driver, filepath="cookies.pkl"):
    """저장된 쿠키를 로드"""
    import pickle
    
    if not Path(filepath).exists():
        print(f"⚠️ 쿠키 파일 없음: {filepath}")
        return False
    
    try:
        # BlogDex 도메인으로 먼저 이동 (쿠키 추가를 위해 필요)
        driver.get("https://blogdex.space/")
        time.sleep(1)
        
        with open(filepath, 'rb') as f:
            cookies = pickle.load(f)
        
        # 쿠키 추가
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                # 일부 쿠키는 추가 실패할 수 있음 (도메인 불일치 등)
                pass
        
        print(f"✅ 쿠키 로드 완료: {filepath}")
        return True
    except Exception as e:
        print(f"❌ 쿠키 로드 실패: {e}")
        return False

def verify_login_status(driver):
    """로그인 상태 확인"""
    try:
        print("로그인 상태 확인 중...")
        
        # 현재 URL 확인
        current_url = driver.current_url
        
        # 로그인 페이지면 로그인 안됨
        if "login" in current_url:
            print("⚠️ 로그인 페이지로 리다이렉트됨 - 로그인 필요")
            return False
        
        # 메인 페이지에서 로그인 상태 확인
        try:
            # 로그인된 상태에서는 특정 요소가 있는지 확인
            # 예: User menu 버튼 클릭 후 로그아웃 메뉴 확인
            page_source = driver.page_source
            
            # 간단한 방법: 페이지 소스에 로그인 관련 키워드 확인
            if "로그인" in page_source and "로그아웃" not in page_source:
                # "로그인" 버튼만 있고 "로그아웃"이 없으면 비로그인 상태
                print("⚠️ 비로그인 상태 감지")
                return False
            
            print("✅ 로그인 상태 확인됨")
            return True
            
        except Exception as e:
            print(f"⚠️ 로그인 상태 확인 중 오류: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 로그인 상태 확인 실패: {e}")
        return False

def extract_blog_grade(driver, blog_url):
    """블로그 지수 데이터를 추출"""
    try:
        print("블로그 지수 데이터 추출 중...")

        # 페이지 로딩 대기
        print("결과 페이지 로딩 확인 중... (3초)")
        time.sleep(3)

        grade_value = None

        # 방법 1: JavaScript로 SVG text 요소의 textContent 읽기 (가장 안정적)
        try:
            print("1단계: JavaScript로 SVG text 요소 찾기...")
            grade_value = driver.execute_script("""
                const svgTexts = document.querySelectorAll('svg text');
                for (let elem of svgTexts) {
                    const text = elem.textContent.trim();
                    if (text && (text.includes('최') || text.includes('준'))) {
                        return text;
                    }
                }
                return null;
            """)
            if grade_value:
                print(f"✅ JavaScript로 지수 발견: {grade_value}")
        except Exception as e1:
            print(f"JavaScript 방식 실패: {e1}")

        # 방법 2: XPath로 text 요소 찾기
        if not grade_value:
            try:
                print("2단계: XPath로 text 요소 찾기...")
                grade_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//svg//text[contains(text(), '최') or contains(text(), '준')]"))
                )
                grade_value = grade_element.get_attribute('textContent')
                if not grade_value:
                    grade_value = grade_element.text
                print(f"✅ XPath로 지수 발견: {grade_value}")
            except Exception as e2:
                print(f"XPath 실패: {e2}")

        # 방법 3: 페이지 전체 텍스트에서 정규식으로 찾기
        if not grade_value:
            try:
                print("3단계: 페이지 전체 텍스트 스캔...")
                page_text = driver.execute_script("return document.body.innerText;")
                import re
                # 패턴: "준최1", "최적2+", "최상5", "최적1" 등
                pattern = r'(준?최[적상하]?\d\+?)'
                matches = re.findall(pattern, page_text)
                if matches:
                    grade_value = matches[0]
                    print(f"✅ 정규식으로 지수 발견: {grade_value}")
            except Exception as e3:
                print(f"정규식 스캔 실패: {e3}")

        if grade_value:
            result = {
                "blog_url": blog_url,
                "grade": grade_value,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"✅ 블로그 지수 추출 완료: {grade_value}")
            return result
        else:
            print("❌ 모든 방법으로 지수를 찾을 수 없습니다.")
            return None

    except Exception as e:
        print(f"❌ 블로그 지수 데이터 추출 실패: {e}")
        return None

def get_blog_id_from_url(url):
    """URL에서 블로그 ID 추출"""
    try:
        # https://blog.naver.com/nightd/224041403656 → nightd
        parts = urlparse(url).path.split('/')
        blog_id = parts[1] if len(parts) > 1 else "unknown"
        return blog_id
    except:
        return "unknown"

def create_json_filename(blog_url):
    """개별 JSON 파일명 생성 (시간순 정렬을 위해 시간 포함)"""
    blog_id = get_blog_id_from_url(blog_url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{blog_id}_grade_{timestamp}.json"

def save_individual_json(data, filename):
    """개별 JSON 파일로 저장"""
    try:
        # 디렉토리 생성
        result_dir = Path("data/json_results")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = result_dir / filename
        
        # 개별 파일로 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 개별 JSON 저장 완료: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 개별 JSON 저장 실패: {e}")
        return False

def save_to_json(data, file_path):
    """데이터를 JSON 파일로 저장 (기존 방식 - 호환성 유지)"""
    try:
        # 디렉토리 생성
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 기존 데이터 로드 (있는 경우)
        existing_data = []
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                # 기존 데이터가 딕셔너리인 경우 리스트로 변환
                if isinstance(loaded_data, dict):
                    existing_data = [loaded_data]
                elif isinstance(loaded_data, list):
                    existing_data = loaded_data
                else:
                    existing_data = []
        
        # 새 데이터 추가
        existing_data.append(data)
        
        # 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON 저장 완료: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ JSON 저장 실패: {e}")
        return False

def process_blog_loop(driver):
    """로그인 후 반복적으로 블로그 처리 (최대 17번)"""
    MAX_SEARCHES = 17
    MAX_RETRIES = 3  # 각 URL당 최대 재시도 횟수
    search_count = 0
    
    print(f"\n🔄 반복 처리 모드 시작 (최대 {MAX_SEARCHES}번)")
    
    while search_count < MAX_SEARCHES:
        # URL 입력받기
        remaining = MAX_SEARCHES - search_count
        blog_url = input(f"\n📝 검색할 블로그 URL 입력 (남은 횟수: {remaining}, 종료: 'q'): ").strip()
        
        if blog_url.lower() == 'q':
            print(f"✅ 총 {search_count}번 검색 완료")
            break
        
        if not blog_url:
            print("⚠️ URL을 입력해주세요.")
            continue
        
        # 재시도 로직
        retry_count = 0
        success = False
        
        while retry_count < MAX_RETRIES and not success:
            if retry_count > 0:
                print(f"\n🔄 재시도 {retry_count}/{MAX_RETRIES-1}...")
            
            try:
                # 홈페이지로 이동
                print(f"\n🌐 BlogDex 메인 페이지로 이동 중...")
                driver.get("https://blogdex.space/")
                time.sleep(3)
                
                # 블로그 검색 및 데이터 추출
                print(f"\n📝 블로그 처리 중: {blog_url}")
                if input_blog_url(driver, blog_url):
                    data = extract_blog_grade(driver, blog_url)
                    if data:
                        # 개별 JSON 저장
                        filename = create_json_filename(blog_url)
                        if save_individual_json(data, filename):
                            search_count += 1
                            print(f"✅ {search_count}번째 검색 완료!")
                            success = True
                        else:
                            print(f"⚠️ JSON 저장 실패")
                    else:
                        print(f"⚠️ 데이터 추출 실패")
                else:
                    print(f"⚠️ URL 입력 실패")
                    
            except Exception as e:
                print(f"❌ 처리 중 오류 발생: {e}")
            
            if not success:
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    print(f"⏳ 3초 후 재시도합니다...")
                    time.sleep(3)
        
        if not success:
            print(f"❌ {MAX_RETRIES}번 재시도 후에도 실패했습니다. 다음 URL로 진행합니다.")
    
    if search_count >= MAX_SEARCHES:
        print(f"\n🎯 최대 검색 횟수({MAX_SEARCHES}번) 도달!")
    
    print(f"\n📊 총 {search_count}개의 블로그 데이터를 수집했습니다.")


def open_blogdex(blog_url=None):
    """BlogDex 사이트를 열고 브라우저를 실행합니다. (undetected-chromedriver 사용)"""
    
    # undetected-chromedriver로 시작 (Cloudflare 우회)
    print("=== undetected-chromedriver 설정 중 ===")
    driver = create_undetected_driver()
    
    if not driver:
        print("❌ 드라이버 생성 실패로 프로그램을 종료합니다.")
        return
    
    try:
        # BlogDex 사이트로 이동
        print("BlogDex 사이트를 여는 중...")
        driver.get("https://blogdex.space/")
        
        # 페이지 로딩 대기 (3-5초)
        print("페이지 로딩 대기 중... (3초)")
        time.sleep(3)
        
        print("BlogDex 사이트가 성공적으로 열렸습니다!")
        print(f"현재 페이지 제목: {driver.title}")
        print(f"현재 URL: {driver.current_url}")
        
        # 쿠키 로드 시도 (로그인 건너뛰기)
        print("\n=== 쿠키 로드 시도 ===")
        cookie_loaded = load_cookies(driver, "cookies.pkl")
        
        if cookie_loaded:
            # 쿠키 로드 후 페이지 새로고침
            print("쿠키 로드 후 페이지 새로고침...")
            driver.refresh()
            time.sleep(3)
            
            # 로그인 상태 확인
            if verify_login_status(driver):
                print("✅ 쿠키로 로그인 성공! 구글 로그인 건너뛰기")
                print(f"현재 URL: {driver.current_url}")
                
                # 로그인 성공, 바로 블로그 검색으로 이동
                skip_login = True
            else:
                print("⚠️ 쿠키가 만료되었거나 유효하지 않음, 구글 로그인 진행")
                skip_login = False
                # 쿠키 파일 삭제 (만료된 쿠키)
                try:
                    Path("cookies.pkl").unlink()
                    print("만료된 쿠키 파일 삭제")
                except:
                    pass
        else:
            print("⚠️ 저장된 쿠키 없음, 구글 로그인 진행")
            skip_login = False
        
        # 로그인이 필요한 경우에만 로그인 프로세스 실행
        if not skip_login:
            # 팝업 닫기 버튼 클릭
            try:
                print("\n팝업 닫기 버튼을 찾는 중...")
                # 여러 가지 방법으로 팝업 닫기 시도
                try:
                    # 첫 번째 방법: 정확한 CSS 선택자
                    popup_close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "#radix-\\:r12\\: > div.relative > div.flex.items-center.justify-between.rounded-b-lg.bg-background.p-2 > button:nth-child(1)"))
                    )
                    popup_close_button.click()
                    print("팝업 닫기 완료!")
                except:
                    try:
                        # 두 번째 방법: ESC 키로 팝업 닫기
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                        print("ESC 키로 팝업 닫기 완료!")
                    except:
                        try:
                            # 세 번째 방법: 팝업 오버레이 클릭
                            overlay = driver.find_element(By.CSS_SELECTOR, "[data-state='open']")
                            overlay.click()
                            print("오버레이 클릭으로 팝업 닫기 완료!")
                        except:
                            print("팝업을 닫을 수 없습니다. 계속 진행합니다.")
                
                print("팝업 닫기 후 대기 중... (3초)")
                time.sleep(3)  # 3초 대기
                
            except Exception as e:
                print(f"팝업 닫기 중 오류: {e}")
            
            # 첫 번째 버튼 클릭
            try:
                print("\n첫 번째 버튼을 찾는 중...")
                first_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#radix-\\:R7336\\:"))
                )
                first_button.click()
                print("첫 번째 버튼 클릭 완료!")
                print("첫 번째 버튼 클릭 후 대기 중... (3초)")
                time.sleep(3)  # 3초 대기
                
            except TimeoutException:
                print("첫 번째 버튼을 찾을 수 없습니다.")
            except Exception as e:
                print(f"첫 번째 버튼 클릭 중 오류: {e}")
        
            # 두 번째 버튼 (로그인 버튼) 클릭
            try:
                print("로그인 버튼을 찾는 중...")
                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#radix-\\:R7336H1\\: > div:nth-child(5) > span"))
                )
                login_button.click()
                print("로그인 버튼 클릭 완료!")
                print("로그인 버튼 클릭 후 대기 중... (3초)")
                time.sleep(3)  # 3초 대기
                
            except TimeoutException:
                print("로그인 버튼을 찾을 수 없습니다.")
            except Exception as e:
                print(f"로그인 버튼 클릭 중 오류: {e}")
            
            # 개인정보 동의 버튼 클릭
            try:
                print("\n개인정보 동의 버튼을 찾는 중...")
                terms_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#terms"))
                )
                terms_button.click()
                print("개인정보 동의 버튼 클릭 완료!")
                print("개인정보 동의 버튼 클릭 후 대기 중... (3초)")
                time.sleep(3)  # 3초 대기
                
            except TimeoutException:
                print("개인정보 동의 버튼을 찾을 수 없습니다.")
            except Exception as e:
                print(f"개인정보 동의 버튼 클릭 중 오류: {e}")
            
            # 구글 로그인 버튼 클릭
            try:
                print("구글 로그인 버튼을 찾는 중...")
                google_login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#__next > div > main > div > div > div.grid.gap-2 > button:nth-child(1)"))
                )
                google_login_button.click()
                print("구글 로그인 버튼 클릭 완료!")
                print("구글 로그인 창으로 이동합니다...")
                print("구글 로그인 버튼 클릭 후 대기 중... (5초)")
                time.sleep(5)
                
                # 구글 로그인 자동화 시작
                print("\n=== 구글 로그인 자동화 시작 ===")
                google_email = os.getenv("GOOGLE_EMAIL")
                google_password = os.getenv("GOOGLE_PASSWORD")
                
                if google_email and google_password:
                    # 1. 이메일 입력
                    print(f"이메일 입력 중: {google_email}")
                    try:
                        email_input = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#identifierId"))
                        )
                        email_input.clear()
                        
                        # 사람처럼 천천히 입력
                        for char in google_email:
                            email_input.send_keys(char)
                            time.sleep(0.1)
                    time.sleep(1)
                    
                    print("✅ 이메일 입력 완료")
                    
                    # 마우스 위아래로 2번 이동 (자연스러운 동작)
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_by_offset(0, 10).perform()
                    time.sleep(0.5)
                    actions.move_by_offset(0, -10).perform()
                    time.sleep(0.5)
                    actions.move_by_offset(0, 10).perform()
                    time.sleep(0.5)
                    actions.move_by_offset(0, -10).perform()
                    time.sleep(0.5)
                    print("✅ 마우스 이동 완료")
                    
                    # 2초 대기
                    print("2초 대기 중...")
                    time.sleep(2)
                    
                    # 다음 버튼 클릭 (사용자 제공 셀렉터 사용)
                    print("다음 버튼 클릭 중...")
                    try:
                        # 사용자 제공 셀렉터 사용
                        next_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "#identifierNext > div > button > div.VfPpkd-RLmnJb"))
                        )
                        next_button.click()
                        print("✅ 다음 버튼 클릭 완료 (사용자 제공 셀렉터)")
                    except Exception as e:
                        print(f"사용자 제공 셀렉터 클릭 실패: {e}")
                        try:
                            # 방법 2: JavaScript 클릭 시도
                            print("JavaScript 클릭 시도 중...")
                            driver.execute_script("arguments[0].click();", next_button)
                            print("✅ 다음 버튼 클릭 완료 (JavaScript 클릭)")
                        except Exception as e2:
                            print(f"JavaScript 클릭 실패: {e2}")
                            try:
                                # 방법 3: 다른 선택자로 시도
                                print("다른 선택자로 시도 중...")
                                next_button2 = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#identifierNext button"))
                                )
                                next_button2.click()
                                print("✅ 다음 버튼 클릭 완료 (다른 선택자)")
                            except Exception as e3:
                                print(f"다른 선택자 클릭 실패: {e3}")
                                # 방법 4: Enter 키 사용
                                print("Enter 키로 시도 중...")
                                email_input.send_keys(Keys.RETURN)
                                print("✅ Enter 키로 다음 버튼 클릭 완료")
                    
                    # 비밀번호 페이지 로딩 대기 (비밀번호 필드가 나타날 때까지)
                    print("비밀번호 페이지 로딩 대기 중... (4초)")
                    time.sleep(4)  # 페이지 전환 완료 대기

                    # 비밀번호 입력 (개선된 방법)
                    print("비밀번호 입력 시도 중...")

                    try:
                        password_input = None

                        # 방법 1: type='password'로 찾기 (가장 일반적)
                        print("1단계: type='password'로 비밀번호 필드 찾기...")
                        try:
                            password_input = WebDriverWait(driver, 15).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                            )
                            print("✅ type='password'로 비밀번호 필드 발견")
                        except Exception as e1:
                            print(f"type='password' 실패: {e1}")

                            # 방법 2: name 속성으로 찾기
                            print("2단계: name 속성으로 비밀번호 필드 찾기...")
                            try:
                                password_input = WebDriverWait(driver, 10).until(
                                    EC.visibility_of_element_located((By.NAME, "Passwd"))
                                )
                                print("✅ name='Passwd'로 비밀번호 필드 발견")
                            except Exception as e2:
                                print(f"name 속성 실패: {e2}")

                                # 방법 3: aria-label로 찾기
                                print("3단계: aria-label로 비밀번호 필드 찾기...")
                                try:
                                    password_input = WebDriverWait(driver, 10).until(
                                        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[aria-label*='password'], input[aria-label*='비밀번호']"))
                                    )
                                    print("✅ aria-label로 비밀번호 필드 발견")
                                except Exception as e3:
                                    print(f"aria-label 실패: {e3}")
                                    
                                    # 방법 4: 사용자 제공 셀렉터
                                    print("4단계: 사용자 제공 셀렉터로 비밀번호 필드 찾기...")
                                    try:
                                        password_input = WebDriverWait(driver, 10).until(
                                            EC.visibility_of_element_located((By.CSS_SELECTOR, "#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input"))
                                        )
                                        print("✅ 사용자 제공 셀렉터로 비밀번호 필드 발견")
                                    except Exception as e4:
                                        print(f"사용자 제공 셀렉터 실패: {e4}")
                                        
                                        # 방법 5: 모든 input 필드 중에서 비밀번호 관련 찾기
                                        print("5단계: 모든 input 필드 검사...")
                                        try:
                                            all_inputs = driver.find_elements(By.TAG_NAME, "input")
                                            for input_elem in all_inputs:
                                                try:
                                                    input_type = input_elem.get_attribute("type")
                                                    input_placeholder = input_elem.get_attribute("placeholder") or ""
                                                    input_aria_label = input_elem.get_attribute("aria-label") or ""
                                                    
                                                    if (input_type == "password" or 
                                                        "password" in input_placeholder.lower() or 
                                                        "password" in input_aria_label.lower() or
                                                        "비밀번호" in input_placeholder or 
                                                        "비밀번호" in input_aria_label):
                                                        
                                                        # 요소가 화면에 보이는지 확인
                                                        if input_elem.is_displayed() and input_elem.is_enabled():
                                                            password_input = input_elem
                                                            print(f"✅ 모든 input 검사로 비밀번호 필드 발견: type={input_type}, placeholder={input_placeholder}")
                                                            break
                                                except:
                                                    continue
                                            else:
                                                print("모든 input 검사에서도 비밀번호 필드를 찾지 못함")
                                        except Exception as e5:
                                            print(f"모든 input 검사 실패: {e5}")

                        # 비밀번호 입력 실행
                        if password_input:
                            print("✅ 비밀번호 필드 발견, 비밀번호 입력 시작...")
                            try:
                                # 페이지 스크롤하여 요소를 뷰포트 중앙으로
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_input)
                                time.sleep(1)

                                # JavaScript로 직접 포커스
                                driver.execute_script("arguments[0].focus();", password_input)
                                time.sleep(0.5)

                                # JavaScript로 값 설정 시도
                                print("비밀번호 입력 중... (JavaScript 방식)")
                                driver.execute_script(f"arguments[0].value = '{google_password}';", password_input)
                                time.sleep(0.5)

                                # input 이벤트 트리거
                                driver.execute_script("""
                                    var event = new Event('input', { bubbles: true });
                                    arguments[0].dispatchEvent(event);
                                """, password_input)
                                time.sleep(0.5)

                                print("✅ 비밀번호 입력 완료 (JavaScript)")
                                
                                # 2초 대기
                                print("비밀번호 입력 후 2초 대기 중...")
                                time.sleep(2)
                                
                                # 비밀번호 다음 버튼 클릭 (개선된 방법)
                                print("비밀번호 다음 버튼 클릭 중...")

                                # 방법 1: JavaScript로 버튼 찾고 클릭
                                try:
                                    print("1단계: JavaScript로 다음 버튼 클릭 시도...")
                                    password_next_btn = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, "#passwordNext button"))
                                    )
                                    # 스크롤하여 버튼을 뷰포트에 표시
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_next_btn)
                                    time.sleep(0.5)
                                    # JavaScript로 직접 클릭
                                    driver.execute_script("arguments[0].click();", password_next_btn)
                                    print("✅ 비밀번호 다음 버튼 클릭 완료 (JavaScript)")
                                except Exception as e:
                                    print(f"JavaScript 클릭 실패: {e}")

                                    # 방법 2: Enter 키 사용
                                    try:
                                        print("2단계: Enter 키로 제출 시도...")
                                        password_input.send_keys(Keys.RETURN)
                                        print("✅ Enter 키로 비밀번호 제출 완료")
                                    except Exception as e2:
                                        print(f"Enter 키 실패: {e2}")

                                        # 방법 3: 일반 클릭 시도
                                        try:
                                            print("3단계: 일반 클릭 시도...")
                                            password_next_btn = WebDriverWait(driver, 10).until(
                                                EC.element_to_be_clickable((By.CSS_SELECTOR, "#passwordNext button"))
                                            )
                                            password_next_btn.click()
                                            print("✅ 일반 클릭으로 다음 버튼 클릭 완료")
                                        except Exception as e3:
                                            print(f"⚠️ 모든 클릭 방법 실패: {e3}")
                                            print("계속 진행합니다...")

                                # 비밀번호 다음 버튼 클릭 후 대기
                                print("\n⏳ 비밀번호 다음 버튼 클릭 후 대기 중... (4초)")
                                time.sleep(4)  # 로그인 완료 및 리다이렉트 대기
                                
                                # 로그인 완료 대기 (BlogDex URL로 돌아올 때까지)
                                print("\n⏳ 로그인 완료 대기 중...")
                                print("   👉 2단계 인증(2FA)이 필요하면 60초 안에 수동으로 완료해주세요!")
                                print("   📱 휴대폰에서 승인하거나 인증 코드를 입력하세요.")
                                
                                login_success = False
                                wait_time = 60  # 2FA를 위한 대기 시간 (60초)
                                start_time = time.time()
                                
                                try:
                                    # 2FA 페이지 감지
                                    current_url = driver.current_url
                                    if "challenge" in current_url or "signin/v2/challenge" in current_url:
                                        print("🔐 2단계 인증 페이지 감지됨!")
                                        print(f"⏰ {wait_time}초 동안 대기합니다. 인증을 완료해주세요...")
                                        
                                        # 진행 상황 표시
                                        for remaining in range(wait_time, 0, -10):
                                            elapsed = time.time() - start_time
                                            current_url = driver.current_url
                                            
                                            if "blogdex.space" in current_url:
                                                print(f"\n✅ BlogDex로 리다이렉트 완료! ({int(elapsed)}초 소요)")
                                                login_success = True
                                                break
                                            
                                            print(f"   ⏳ 남은 시간: {remaining}초...")
                                            time.sleep(10)
                                    
                                    # 일반적인 로그인 완료 대기
                                    if not login_success:
                                        WebDriverWait(driver, max(5, wait_time - int(time.time() - start_time))).until(
                                            lambda d: "blogdex.space" in d.current_url
                                        )
                                        print("✅ BlogDex로 리다이렉트 완료")
                                        login_success = True
                                    
                                    # 세션 안정화를 위한 추가 대기 (쿠키 설정 시간 확보)
                                    print("⏳ 세션 안정화 대기 중... (5초)")
                                    time.sleep(5)
                                    
                                    # 현재 URL 로그 출력
                                    print(f"현재 URL: {driver.current_url}")
                                    
                                except TimeoutException:
                                    print("❌ 로그인 대기 시간 초과")
                                    print(f"현재 URL: {driver.current_url}")
                                    
                                    # 현재 페이지가 구글 로그인 페이지인지 확인
                                    if "accounts.google.com" in driver.current_url:
                                        print("❌ 여전히 구글 로그인 페이지에 있습니다.")
                                        print("❌ 2단계 인증을 완료하지 못했습니다.")
                                        print("💡 다시 실행하여 2FA 인증을 완료해주세요.")
                                        return
                                    else:
                                        print("⚠️ 알 수 없는 페이지, 계속 진행합니다...")
                                        login_success = True
                                
                                # 로그인 성공 확인
                                if not login_success:
                                    print("❌ 로그인 실패 - 프로그램을 종료합니다.")
                                    return

                                print("✅ 구글 로그인 프로세스 완료!")

                            except Exception as e:
                                print(f"❌ 비밀번호 입력 중 오류 발생: {e}")
                                print(f"⚠️ 로그인 실패 - 자동화를 계속 시도합니다...")
                                # 에러 발생해도 계속 진행 (쿠키가 있을 수 있음)

                        else:
                            print("❌ 비밀번호 입력 필드를 찾을 수 없습니다.")
                            print("❌ 로그인 실패 - 프로그램을 종료합니다.")
                            return  # 로그인 실패 시 프로그램 종료

                    except Exception as e:
                        print(f"❌ 비밀번호 처리 중 오류: {e}")
                        print("⚠️ 로그인 단계를 건너뛰고 계속 진행합니다...")
                    
                    print("✅ 구글 로그인 프로세스 완료!")

                    # 쿠키 저장 (다음 실행 시 로그인 건너뛰기 위해)
                    print("\n💾 쿠키 저장 중...")
                    save_cookies(driver, "cookies.pkl")

                    # 구글 로그인 완료 후 BlogDex 메인으로 이동 (필수!)
                    print("\n🌐 BlogDex 메인 페이지로 이동 중...")
                    
                    # 강제 메인 페이지 이동 전에 잠시 대기
                    print("메인 페이지 이동 전 대기 중... (3초)")
                    time.sleep(3)
                    
                    driver.get("https://blogdex.space/")
                    print("페이지 로딩 대기 중...")
                    
                    # 현재 URL 로그 출력
                    print(f"이동 후 URL: {driver.current_url}")
                    
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                "#__next > div > main > section.space-y-6.pb-12.pt-8.lg\\:py-28 > div > div.flex.flex-col.items-center > div.flex.animate-fade-up.justify-center.space-x-2.opacity-0.md\\:space-x-4 > div > div > input"))
                        )
                        print("✅ BlogDex 메인 페이지 로딩 완료")
                        
                        # 로그인 상태 확인 (사용자 프로필이나 로그아웃 버튼 등이 있는지 확인)
                        try:
                            # 로그인된 상태에서 나타나는 요소들 확인
                            login_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='user'], [class*='avatar'], [class*='profile'], button:contains('로그아웃'), button:contains('Logout')")
                            if login_elements:
                                print("✅ 로그인 상태 확인됨")
                            else:
                                print("⚠️ 로그인 상태 확인 실패 - 페이지를 다시 확인해주세요")
                        except Exception as e:
                            print(f"⚠️ 로그인 상태 확인 중 오류: {e}")
                            
                    except TimeoutException:
                        print("⚠️ 페이지 로딩 대기 시간 초과, 계속 진행...")
                        print("현재 페이지 제목:", driver.title)
                        print("현재 URL:", driver.current_url)
        
        # 블로그 데이터 수집 시작 (로그인 여부와 관계없이 실행)
        print("\n🔍 블로그 데이터 수집 시작...")

        # URL 결정: 명령행 인자가 있으면 첫 번째 처리 후 계속 반복 모드
        if blog_url:
            print(f"📝 첫 번째 URL 처리: {blog_url}")

            # 블로그 URL 입력
            if input_blog_url(driver, blog_url):
                # 3. 지수 데이터 추출
                data = extract_blog_grade(driver, blog_url)
                if data:
                    # 4. 개별 JSON 저장
                    filename = create_json_filename(blog_url)
                    save_individual_json(data, filename)
                    print("\n✅ 첫 번째 블로그 데이터 수집 완료!")
                else:
                    print(f"⚠️ {blog_url} 데이터 추출 실패")
            else:
                print(f"⚠️ {blog_url} URL 입력 실패")

            # 첫 번째 처리 후 반복 모드로 전환
            print("\n📝 계속해서 블로그를 검색하시겠습니까?")
            process_blog_loop(driver)
        else:
            print("📝 반복 처리 모드")
            # 반복 처리 함수 호출
            process_blog_loop(driver)

        print("\n🌐 브라우저를 유지한 채로 종료합니다.")
        print("⚠️ 수동으로 브라우저를 닫아주세요.")

        # 브라우저를 종료하지 않고 무한 대기
        print("\n✅ 모든 작업이 완료되었습니다!")
        print("💡 브라우저는 계속 열려있습니다. 수동으로 닫아주세요.")
        input("\n엔터 키를 누르면 브라우저가 종료됩니다...")

            except Exception as e:
                print(f"❌ 이메일 입력 중 오류 발생: {e}")
                print("⚠️ 로그인 실패 - 자동화를 계속 시도합니다...")
                    # 에러 발생해도 계속 진행

            else:
                print("❌ 환경변수에서 구글 계정 정보를 찾을 수 없습니다.")
                print("⚠️ 로그인 없이 계속 진행합니다 (쿠키 확인)...")

        except TimeoutException:
            print("구글 로그인 버튼을 찾을 수 없습니다.")
        except Exception as e:
            print(f"구글 로그인 버튼 클릭 중 오류: {e}")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

    finally:
        # 브라우저 종료
        driver.quit()
        print("브라우저가 종료되었습니다.")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BlogDex 자동화 스크립트")
    print("=" * 60)
    
    # 명령행 인자에서 URL 확인
    if len(sys.argv) > 1:
        blog_url = sys.argv[1]
        print(f"🔗 단일 URL 모드: {blog_url}")
        print("📝 이 URL만 처리하고 종료됩니다.")
        open_blogdex(blog_url)
    else:
        print("📝 대화형 모드 (최대 17번 반복)")
        print("💡 단일 URL 처리: python open_blogdex.py <URL>")
        print("💡 반복 처리: python open_blogdex.py")
        print("-" * 60)
        open_blogdex()
