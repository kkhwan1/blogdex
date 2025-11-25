"""
BlogDex 사이트 로그인 자동화 스크립트
undetected-chromedriver를 사용하여 Cloudflare 우회 및 탐지 방지
구글 로그인부터 블로그 등급 수집까지 완전 자동화
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

# 환경변수 로드
load_dotenv()

# 등급 매핑 데이터 (결과.json 기반)
GRADE_MAPPING = {
    "일반": {
        "level": "스타터1",
        "level_en": "Starter1",
        "tier": "스타터 블로거",
        "tier_en": "Starter Blogger",
        "tier_rank": 1
    },
    "준최1": {
        "level": "스타터2",
        "level_en": "Starter2",
        "tier": "스타터 블로거",
        "tier_en": "Starter Blogger",
        "tier_rank": 2
    },
    "준최2": {
        "level": "스타터3",
        "level_en": "Starter3",
        "tier": "스타터 블로거",
        "tier_en": "Starter Blogger",
        "tier_rank": 3
    },
    "준최3": {
        "level": "스타터4",
        "level_en": "Starter4",
        "tier": "스타터 블로거",
        "tier_en": "Starter Blogger",
        "tier_rank": 4
    },
    "준최4": {
        "level": "스타터5",
        "level_en": "Starter5",
        "tier": "스타터 블로거",
        "tier_en": "Starter Blogger",
        "tier_rank": 5
    },
    "준최5": {
        "level": "엘리트1",
        "level_en": "Elite1",
        "tier": "엘리트 블로거",
        "tier_en": "Elite Blogger",
        "tier_rank": 1
    },
    "준최6": {
        "level": "엘리트2",
        "level_en": "Elite2",
        "tier": "엘리트 블로거",
        "tier_en": "Elite Blogger",
        "tier_rank": 2
    },
    "준최7": {
        "level": "엘리트3",
        "level_en": "Elite3",
        "tier": "엘리트 블로거",
        "tier_en": "Elite Blogger",
        "tier_rank": 3
    },
    "최적1": {
        "level": "엘리트4",
        "level_en": "Elite4",
        "tier": "엘리트 블로거",
        "tier_en": "Elite Blogger",
        "tier_rank": 4
    },
    "최적2": {
        "level": "엘리트5",
        "level_en": "Elite5",
        "tier": "엘리트 블로거",
        "tier_en": "Elite Blogger",
        "tier_rank": 5
    },
    "최적3": {
        "level": "엑스퍼트1",
        "level_en": "Expert1",
        "tier": "엑스퍼트 블로거",
        "tier_en": "Expert Blogger",
        "tier_rank": 1
    },
    "최적1+": {
        "level": "엑스퍼트2",
        "level_en": "Expert2",
        "tier": "엑스퍼트 블로거",
        "tier_en": "Expert Blogger",
        "tier_rank": 2
    },
    "최적2+": {
        "level": "엑스퍼트3",
        "level_en": "Expert3",
        "tier": "엑스퍼트 블로거",
        "tier_en": "Expert Blogger",
        "tier_rank": 3
    },
    "최적3+": {
        "level": "엑스퍼트4",
        "level_en": "Expert4",
        "tier": "엑스퍼트 블로거",
        "tier_en": "Expert Blogger",
        "tier_rank": 4
    },
    "최적4+": {
        "level": "엑스퍼트5",
        "level_en": "Expert5",
        "tier": "엑스퍼트 블로거",
        "tier_en": "Expert Blogger",
        "tier_rank": 5
    }
}

def get_level_info(grade):
    """등급을 기반으로 레벨 정보 반환"""
    try:
        if grade in GRADE_MAPPING:
            level_info = GRADE_MAPPING[grade].copy()
            print(f"📊 등급 '{grade}' → 레벨 '{level_info['level']}' ({level_info['tier']})")
            return level_info
        else:
            print(f"⚠️ 알 수 없는 등급: {grade}")
            return {
                "level": "알 수 없음",
                "level_en": "Unknown",
                "tier": "알 수 없음",
                "tier_en": "Unknown",
                "tier_rank": 0
            }
    except Exception as e:
        print(f"❌ 레벨 정보 조회 중 오류: {e}")
        return None

def create_undetected_driver():
    """undetected-chromedriver로 Chrome 드라이버 생성 (open_blogdex.py 기반)"""
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

def wait_and_click(driver, selector, wait_time=10, step_name="요소"):
    """요소를 기다린 후 클릭"""
    try:
        print(f"🔍 {step_name} 찾는 중... (선택자: {selector})")
        
        # 요소가 클릭 가능할 때까지 대기
        element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        
        # 요소 클릭
        element.click()
        print(f"✅ {step_name} 클릭 완료")
        return True
        
    except TimeoutException:
        print(f"❌ {step_name} 찾기 실패 (타임아웃: {wait_time}초)")
        return False
    except Exception as e:
        print(f"❌ {step_name} 클릭 중 오류: {e}")
        return False

def click_with_retry(driver, selectors, max_retries=3, wait_time=5, step_name="요소"):
    """여러 선택자로 재시도하며 클릭"""
    for attempt in range(max_retries):
        print(f"🔄 {step_name} 시도 {attempt + 1}/{max_retries}")
        
        for i, selector in enumerate(selectors):
            try:
                print(f"  선택자 {i+1}: {selector}")
                
                # 요소가 클릭 가능할 때까지 대기
                element = WebDriverWait(driver, wait_time).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                # JavaScript 클릭 우선 시도
                try:
                    driver.execute_script("arguments[0].click();", element)
                    print(f"✅ {step_name} JavaScript 클릭 성공")
                    return True
                except Exception as js_error:
                    print(f"  JavaScript 클릭 실패: {js_error}")
                    
                    # 일반 클릭 시도
                    element.click()
                    print(f"✅ {step_name} 일반 클릭 성공")
                    return True
                    
            except TimeoutException:
                print(f"  선택자 {i+1} 실패 (타임아웃)")
                continue
            except Exception as e:
                print(f"  선택자 {i+1} 실패: {e}")
                continue
        
        if attempt < max_retries - 1:
            print(f"  ⏳ {wait_time}초 대기 후 재시도...")
            time.sleep(wait_time)
    
    print(f"❌ {step_name} 모든 시도 실패")
    return False

def wait_and_check(driver, selector, wait_time=10, step_name="체크박스"):
    """체크박스를 기다린 후 체크"""
    try:
        print(f"🔍 {step_name} 찾는 중... (선택자: {selector})")
        
        # 요소가 클릭 가능할 때까지 대기
        element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        
        # 체크박스 상태 확인 후 클릭
        if not element.is_selected():
            element.click()
            print(f"✅ {step_name} 체크 완료")
        else:
            print(f"ℹ️ {step_name} 이미 체크됨")
        return True
        
    except TimeoutException:
        print(f"❌ {step_name} 찾기 실패 (타임아웃: {wait_time}초)")
        return False
    except Exception as e:
        print(f"❌ {step_name} 체크 중 오류: {e}")
        return False

def wait_and_input(driver, selector, text, wait_time=10, step_name="입력 필드"):
    """입력 필드를 기다린 후 텍스트 입력"""
    try:
        print(f"🔍 {step_name} 찾는 중... (선택자: {selector})")
        
        # 요소가 클릭 가능할 때까지 대기
        element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        
        # 기존 텍스트 지우고 새 텍스트 입력
        element.clear()
        element.send_keys(text)
        print(f"✅ {step_name}에 '{text}' 입력 완료")
        return True
        
    except TimeoutException:
        print(f"❌ {step_name} 찾기 실패 (타임아웃: {wait_time}초)")
        return False
    except Exception as e:
        print(f"❌ {step_name} 입력 중 오류: {e}")
        return False

def wait_and_get_text(driver, selector, wait_time=10, step_name="텍스트"):
    """요소를 기다린 후 텍스트 추출"""
    try:
        print(f"🔍 {step_name} 찾는 중... (선택자: {selector})")
        
        # 요소가 존재할 때까지 대기
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        
        text = element.text.strip()
        print(f"✅ {step_name} 추출 완료: '{text}'")
        return text
        
    except TimeoutException:
        print(f"❌ {step_name} 찾기 실패 (타임아웃: {wait_time}초)")
        return None
    except Exception as e:
        print(f"❌ {step_name} 추출 중 오류: {e}")
        return None

def mouse_scroll(driver, scroll_count=3):
    """마우스 위아래 스크롤 동작"""
    try:
        print("🖱️ 마우스 스크롤 동작 실행")
        actions = ActionChains(driver)
        
        # 위아래 스크롤 반복
        for i in range(scroll_count):
            actions.move_by_offset(0, 50).perform()  # 아래로
            time.sleep(0.5)
            actions.move_by_offset(0, -50).perform()  # 위로
            time.sleep(0.5)
        
        print("✅ 마우스 스크롤 동작 완료")
        return True
        
    except Exception as e:
        print(f"❌ 마우스 스크롤 동작 중 오류: {e}")
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
        
        # 간단한 방법: 페이지 소스에 로그인 관련 키워드 확인
        page_source = driver.page_source
        
        # "로그인" 버튼만 있고 "로그아웃"이 없으면 비로그인 상태
        if "로그인" in page_source and "로그아웃" not in page_source:
            print("⚠️ 비로그인 상태 감지")
            return False
        
        print("✅ 로그인 상태 확인됨")
        return True
        
    except Exception as e:
        print(f"❌ 로그인 상태 확인 실패: {e}")
        return False

def login_google(driver):
    """구글 로그인 처리 (open_blogdex.py 기반)"""
    try:
        print("\n=== 구글 로그인 자동화 시작 ===")
        
        # 환경변수에서 구글 계정 정보 읽기
        google_email = os.getenv("GOOGLE_EMAIL")
        google_password = os.getenv("GOOGLE_PASSWORD")
        
        if not google_email or not google_password:
            print("❌ 환경변수에서 구글 계정 정보를 찾을 수 없습니다.")
            print("   .env 파일에 GOOGLE_EMAIL과 GOOGLE_PASSWORD를 설정해주세요.")
            return False
        
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
            
            # 다음 버튼 클릭 (안정적인 선택자 사용)
            print("다음 버튼 클릭 중...")
            
            # 이메일 다음 버튼 선택자들
            email_next_selectors = [
                "#identifierNext button",  # 단순화된 선택자
                "#identifierNext > div > button",  # 중간 단계
                "#identifierNext > div > button > div.VfPpkd-RLmnJb",  # 기존 선택자
                "button:has(div.VfPpkd-RLmnJb)"  # 클래스 기반
            ]
            
            if click_with_retry(driver, email_next_selectors, max_retries=2, wait_time=5, step_name="이메일 다음 버튼"):
                print("✅ 이메일 다음 버튼 클릭 성공")
            else:
                # 마지막 수단: Enter 키 사용
                print("Enter 키로 시도 중...")
                email_input.send_keys(Keys.RETURN)
                print("✅ Enter 키로 다음 버튼 클릭 완료")
            
            # 비밀번호 페이지 로딩 대기 (대기 시간 증가)
            print("비밀번호 페이지 로딩 대기 중... (6초)")
            time.sleep(6)

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

                        # 방법 3: 사용자 제공 셀렉터
                        print("3단계: 사용자 제공 셀렉터로 비밀번호 필드 찾기...")
                        try:
                            password_input = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, "#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input"))
                            )
                            print("✅ 사용자 제공 셀렉터로 비밀번호 필드 발견")
                        except Exception as e3:
                            print(f"사용자 제공 셀렉터 실패: {e3}")

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
                        
                        # 비밀번호 다음 버튼 클릭 (안정적인 선택자 사용)
                        print("비밀번호 다음 버튼 클릭 중...")
                        
                        # 비밀번호 다음 버튼 선택자들
                        password_next_selectors = [
                            "#passwordNext button",  # 단순화된 선택자
                            "#passwordNext > div > button",  # 중간 단계
                            "button:has(div.VfPpkd-RLmnJb)",  # 클래스 기반
                            "#passwordNext > div > button > span"  # 기존 선택자
                        ]
                        
                        if click_with_retry(driver, password_next_selectors, max_retries=2, wait_time=5, step_name="비밀번호 다음 버튼"):
                            print("✅ 비밀번호 다음 버튼 클릭 성공")
                        else:
                            # 마지막 수단: Enter 키 사용
                            print("Enter 키로 제출 시도...")
                            password_input.send_keys(Keys.RETURN)
                            print("✅ Enter 키로 비밀번호 제출 완료")

                        # 비밀번호 다음 버튼 클릭 후 대기 (대기 시간 증가)
                        print("\n⏳ 비밀번호 다음 버튼 클릭 후 대기 중... (6초)")
                        time.sleep(6)
                        
                        # 로그인 완료 대기 (BlogDex URL로 돌아올 때까지)
                        print("\n⏳ 로그인 완료 대기 중...")
                        print("   (2단계 인증이 있다면 자동으로 처리되거나 실패할 수 있습니다)")
                        login_success = False
                        try:
                            WebDriverWait(driver, 30).until(  # 타임아웃 증가
                                lambda d: "blogdex.space" in d.current_url
                            )
                            print("✅ BlogDex로 리다이렉트 완료")
                            
                            # 세션 안정화를 위한 추가 대기 (대기 시간 증가)
                            print("⏳ 세션 안정화 대기 중... (7초)")
                            time.sleep(7)
                            
                            # 현재 URL 로그 출력
                            print(f"현재 URL: {driver.current_url}")
                            login_success = True
                            
                        except TimeoutException:
                            print("❌ 로그인 대기 시간 초과")
                            print(f"현재 URL: {driver.current_url}")
                            
                            # 현재 페이지가 구글 로그인 페이지인지 확인
                            if "accounts.google.com" in driver.current_url:
                                print("❌ 여전히 구글 로그인 페이지에 있습니다.")
                                print("❌ 로그인 실패 - 프로그램을 종료합니다.")
                                return False
                            else:
                                print("⚠️ 알 수 없는 페이지, 계속 진행합니다...")
                                login_success = True
                        
                        # 로그인 성공 확인
                        if not login_success:
                            print("❌ 로그인 실패 - 프로그램을 종료합니다.")
                            return False

                        print("✅ 구글 로그인 프로세스 완료!")
                        return True

                    except Exception as e:
                        print(f"❌ 비밀번호 입력 중 오류 발생: {e}")
                        print(f"⚠️ 로그인 실패 - 자동화를 계속 시도합니다...")
                        return False

                else:
                    print("❌ 비밀번호 입력 필드를 찾을 수 없습니다.")
                    print("❌ 로그인 실패 - 프로그램을 종료합니다.")
                    return False

            except Exception as e:
                print(f"❌ 비밀번호 처리 중 오류: {e}")
                print("⚠️ 로그인 단계를 건너뛰고 계속 진행합니다...")
                return False
            
            print("✅ 구글 로그인 프로세스 완료!")
            return True

        except Exception as e:
            print(f"❌ 이메일 입력 중 오류 발생: {e}")
            print("⚠️ 로그인 실패 - 자동화를 계속 시도합니다...")
            return False
        
    except Exception as e:
        print(f"❌ 구글 로그인 중 오류: {e}")
        return False

def search_blog(driver, blog_url):
    """블로그 검색 및 등급 추출 (open_blogdex.py의 개선된 방식 사용)"""
    try:
        print(f"\n📍 블로그 검색 시작: {blog_url}")
        
        # 마우스 스크롤 동작
        mouse_scroll(driver)
        
        # URL 입력 필드 찾기 (visibility 체크 - open_blogdex.py 방식)
        print("URL 입력 필드 로딩 대기 중... (5초)")
        time.sleep(5)
        
        print("URL 입력 필드를 찾는 중...")
        url_input = None
        try:
            # 기본 선택자
            url_input = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR,
                    "#__next > div > main > section.space-y-6.pb-12.pt-8.lg\\:py-28 > div > div.flex.flex-col.items-center > div.flex.animate-fade-up.justify-center.space-x-2.opacity-0.md\\:space-x-4 > div > div > input"))
            )
            print("✅ URL 입력 필드 발견")
        except Exception as e:
            print(f"기본 선택자 실패: {e}")
            # 대안 선택자들 시도
            alternative_selectors = [
                "input[placeholder*='URL'], input[placeholder*='url'], input[placeholder*='블로그']",
                "input[type='text']",
                "input",
                "[class*='input'] input"
            ]
            
            for i, selector in enumerate(alternative_selectors, 1):
                try:
                    print(f"대안 선택자 {i} 시도 중...")
                    url_input = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ URL 입력 필드 발견 (대안 선택자 {i})")
                    break
                except Exception as e2:
                    print(f"대안 선택자 {i} 실패: {e2}")
                    if i == len(alternative_selectors):
                        print("❌ 모든 선택자 실패")
                        return None

        # 스크롤하여 요소를 뷰포트 중앙으로
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", url_input)
        time.sleep(1)

        # 필드 클리어 및 포커스
        url_input.clear()
        time.sleep(0.3)
        url_input.click()
        time.sleep(0.3)
        
        # URL 입력
        print("URL 입력 중...")
        url_input.send_keys(blog_url)
        time.sleep(0.5)
        
        # React 이벤트 트리거
        driver.execute_script("""
            const element = arguments[0];
            const inputEvent = new Event('input', { bubbles: true });
            element.dispatchEvent(inputEvent);
            const changeEvent = new Event('change', { bubbles: true });
            element.dispatchEvent(changeEvent);
        """, url_input)
        time.sleep(1)
        
        # Enter 키로 검색 실행
        print("Enter 키로 검색 실행 중...")
        from selenium.webdriver.common.keys import Keys
        url_input.send_keys(Keys.RETURN)
        time.sleep(3)
        
        print("✅ URL 입력 및 검색 실행 완료")
        
        # 검색 결과 로딩 대기
        print("검색 결과 로딩 대기 중...")
        time.sleep(6)
        
        # 등급 텍스트 추출 (JavaScript 방식 - open_blogdex.py의 extract_blog_grade 사용)
        print("등급 데이터 추출 중...")
        grade_text = None
        
        # 방법 1: JavaScript로 SVG text 요소 찾기
        try:
            grade_text = driver.execute_script("""
                const svgTexts = document.querySelectorAll('svg text');
                for (let elem of svgTexts) {
                    const text = elem.textContent.trim();
                    if (text && (text.includes('최') || text.includes('준'))) {
                        return text;
                    }
                }
                return null;
            """)
            if grade_text:
                print(f"✅ JavaScript로 지수 발견: {grade_text}")
        except Exception as e1:
            print(f"JavaScript 방식 실패: {e1}")

        # 방법 2: 정규식으로 페이지 전체 스캔
        if not grade_text:
            try:
                import re
                page_text = driver.execute_script("return document.body.innerText;")
                pattern = r'(준?최[적상하]?\d\+?)'
                matches = re.findall(pattern, page_text)
                if matches:
                    grade_text = matches[0]
                    print(f"✅ 정규식으로 지수 발견: {grade_text}")
            except Exception as e2:
                print(f"정규식 스캔 실패: {e2}")
        
        if grade_text:
            print(f"✅ 등급 추출 완료: {grade_text}")
            return grade_text
        else:
            print("❌ 등급 텍스트를 찾을 수 없습니다.")
            return None
            
    except Exception as e:
        print(f"❌ 블로그 검색 중 오류: {e}")
        return None

def save_result_json(blog_url, grade, result_dir="data/json_results"):
    """결과를 JSON 파일로 저장 (등급 레벨 정보 포함)"""
    try:
        # 결과 디렉토리 생성
        Path(result_dir).mkdir(parents=True, exist_ok=True)
        
        # 블로그 ID 추출 (URL에서 도메인명 추출)
        parsed_url = urlparse(blog_url)
        blog_id = parsed_url.netloc.replace('blog.naver.com', 'naver').replace('.', '_')
        
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 파일명 생성
        filename = f"{blog_id}_grade_{timestamp}.json"
        filepath = os.path.join(result_dir, filename)
        
        # 등급에 따른 레벨 정보 조회
        level_info = get_level_info(grade)
        
        # JSON 데이터 생성 (레벨 정보 포함)
        data = {
            "blog_url": blog_url,
            "grade": grade,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 레벨 정보가 있으면 추가
        if level_info:
            data.update(level_info)
        
        # 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON 파일 저장 완료: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ JSON 파일 저장 중 오류: {e}")
        return None

def go_home(driver):
    """홈으로 이동 (로그인 상태 유지)"""
    try:
        print("🏠 홈으로 이동")
        driver.get("https://blogdex.space/")
        time.sleep(2)
        print("✅ 홈 이동 완료")
        return True
    except Exception as e:
        print(f"❌ 홈 이동 중 오류: {e}")
        return False

def validate_url(url):
    """URL 유효성 검사"""
    url = url.strip()
    
    # 빈 문자열 체크
    if not url:
        return False, "빈 URL"
    
    # 기본 URL 형식 체크
    if not (url.startswith('http://') or url.startswith('https://')):
        return False, "URL은 http:// 또는 https://로 시작해야 합니다"
    
    # 네이버 블로그 URL 체크 (선택사항)
    if 'blog.naver.com' not in url:
        return False, "네이버 블로그 URL만 지원합니다 (blog.naver.com)"
    
    return True, "유효한 URL"

def get_blog_urls_from_user():
    """사용자로부터 블로그 URL 리스트를 입력받기 (명령줄 인자 우선)"""
    import sys
    
    # 명령줄 인자로 URL이 전달된 경우 먼저 확인
    if len(sys.argv) > 1:
        print("\n✅ 명령줄 인자로 URL이 전달되었습니다:")
        urls = []
        invalid_urls = []
        
        for url in sys.argv[1:]:
            url = url.strip()
            if url:
                is_valid, message = validate_url(url)
                if is_valid:
                    urls.append(url)
                    print(f"  ✓ {url}")
                else:
                    invalid_urls.append((url, message))
                    print(f"  ✗ {url}: {message}")
        
        if invalid_urls:
            print("\n⚠️ 유효하지 않은 URL:")
            for url, msg in invalid_urls:
                print(f"  • {url}: {msg}")
        
        if urls:
            print(f"\n✅ 총 {len(urls)}개의 URL이 입력되었습니다.\n")
            return urls
        else:
            print("\n❌ 유효한 URL이 없습니다. 대화형 입력으로 전환합니다.\n")
    
    # 대화형 입력
    print("\n" + "=" * 50)
    print("📝 분석할 블로그 URL을 입력하세요")
    print("=" * 50)
    print("• 한 줄에 하나씩 URL을 입력하세요")
    print("• 빈 줄을 입력하면 URL 입력이 완료됩니다")
    print("• 'q' 또는 'quit'을 입력하면 프로그램을 종료합니다")
    print("• 예시: https://blog.naver.com/username")
    print("-" * 50)
    
    urls = []
    invalid_urls = []
    
    while True:
        try:
            url_input = input("> ").strip()
            
            # 종료 조건
            if url_input.lower() in ['q', 'quit']:
                print("프로그램을 종료합니다.")
                return []
            
            # 빈 줄 입력 시 입력 완료
            if not url_input:
                break
            
            # URL 검증
            is_valid, message = validate_url(url_input)
            
            if is_valid:
                if url_input not in urls:
                    urls.append(url_input)
                    print(f"✅ 추가됨: {url_input}")
                else:
                    print(f"⚠️ 중복된 URL: {url_input}")
            else:
                invalid_urls.append((url_input, message))
                print(f"❌ {message}: {url_input}")
                
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            return []
        except EOFError:
            break
    
    # 결과 출력
    print("\n" + "=" * 50)
    print("📋 입력 결과")
    print("=" * 50)
    
    if urls:
        print("✅ 유효한 URL 목록:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
    else:
        print("❌ 유효한 URL이 없습니다.")
    
    if invalid_urls:
        print("\n⚠️ 무효한 URL:")
        for url, reason in invalid_urls:
            print(f"  • {url} ({reason})")
    
    print(f"\n총 {len(urls)}개의 블로그를 처리합니다.")
    
    if not urls:
        print("❌ 처리할 URL이 없어 프로그램을 종료합니다.")
        return []
    
    # 계속 진행 여부 확인
    while True:
        try:
            confirm = input("\n계속하시겠습니까? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', '예', 'ㅇ']:
                print("✅ 브라우저를 시작합니다...")
                return urls
            elif confirm in ['n', 'no', '아니오', 'ㄴ']:
                print("프로그램을 종료합니다.")
                return []
            else:
                print("y 또는 n을 입력해주세요.")
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            return []
        except EOFError:
            # 자동화된 환경에서 기본값으로 진행
            print("\n✅ 자동 모드로 진행합니다...")
            print("✅ 브라우저를 시작합니다...")
            return urls

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("BlogDex 완전 자동화 시작")
    print("=" * 50)
    
    # 1단계: URL 입력 받기 (브라우저 시작 전)
    blog_urls = get_blog_urls_from_user()
    if not blog_urls:
        print("❌ URL 입력 없이 프로그램을 종료합니다.")
        return
    
    # 2단계: 드라이버 생성
    driver = create_undetected_driver()
    if not driver:
        print("❌ 드라이버 생성 실패로 종료")
        return
    
    try:
        # 1단계: BlogDex 페이지 접속
        print("BlogDex 사이트를 여는 중...")
        driver.get("https://blogdex.space/")
        
        # 페이지 로딩 대기
        print("페이지 로딩 대기 중... (3초)")
        time.sleep(3)
        
        print("BlogDex 사이트가 성공적으로 열렸습니다!")
        print(f"현재 페이지 제목: {driver.title}")
        print(f"현재 URL: {driver.current_url}")
        
        # 쿠키 로드 시도 (로그인 건너뛰기)
        print("\n=== 쿠키 로드 시도 ===")
        cookie_loaded = load_cookies(driver, "cookies.pkl")
        skip_login = False
        
        if cookie_loaded:
            # 쿠키 로드 후 페이지 새로고침
            print("쿠키 로드 후 페이지 새로고침...")
            driver.refresh()
            time.sleep(3)
            
            # 로그인 상태 확인
            if verify_login_status(driver):
                print("✅ 쿠키로 로그인 성공! 구글 로그인 건너뛰기")
                print(f"현재 URL: {driver.current_url}")
                skip_login = True
                
                # 쿠키 로그인 후 페이지 안정화 대기 (중요!)
                print("⏳ 쿠키 로그인 후 페이지 안정화 대기 중... (5초)")
                time.sleep(5)
            else:
                print("⚠️ 쿠키가 만료되었거나 유효하지 않음, 구글 로그인 진행")
                # 쿠키 파일 삭제 (만료된 쿠키)
                try:
                    Path("cookies.pkl").unlink()
                    print("만료된 쿠키 파일 삭제")
                except:
                    pass
        else:
            print("⚠️ 저장된 쿠키 없음, 구글 로그인 진행")
        
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
            
            # 구글 로그인 버튼 클릭 (5단계) - 안정적인 선택자 사용
            print("\n🔐 구글 로그인 버튼 클릭 시도...")
            
            # 안정적인 구글 로그인 버튼 선택자들
            google_selectors = [
                "button:has(svg[data-icon='google'])",  # SVG 아이콘 기반
                "button.bg-primary:has(svg)",  # 클래스 + SVG
                "button.bg-primary.text-white",  # 클래스 조합
                "button:contains('Google')",  # 텍스트 기반
                "#__next > div > main > div > div > div.grid.gap-2 > button:nth-child(1)"  # 기존 선택자
            ]
            
            if click_with_retry(driver, google_selectors, max_retries=3, wait_time=7, step_name="구글 로그인 버튼"):
                print("✅ 구글 로그인 버튼 클릭 성공!")
                print("구글 로그인 창으로 이동합니다...")
                print("구글 로그인 버튼 클릭 후 대기 중... (7초)")
                time.sleep(7)  # 대기 시간 증가
            else:
                print("❌ 구글 로그인 버튼 클릭 실패")
                print("⚠️ 구글 로그인 단계를 건너뛰고 계속 진행합니다...")
            
            # 구글 로그인 처리 (6-10단계)
            if not login_google(driver):
                print("❌ 구글 로그인 실패로 종료")
                return
            
            # 쿠키 저장 (다음 실행 시 로그인 건너뛰기)
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
            time.sleep(3)  # 3초 대기
        
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
        
        # 입력받은 URL 리스트 사용
        print(f"\n📍 총 {len(blog_urls)}개의 블로그 URL을 처리합니다.")
        
        # 각 블로그 URL 처리
        for i, blog_url in enumerate(blog_urls, 1):
            print(f"\n{'='*60}")
            print(f"📍 {i}/{len(blog_urls)}: 블로그 처리 중 - {blog_url}")
            print(f"{'='*60}")
            
            # 블로그 검색 및 등급 추출
            grade = search_blog(driver, blog_url)
            
            if grade:
                # JSON 파일로 저장
                save_result_json(blog_url, grade)
            else:
                print(f"❌ {blog_url} 등급 추출 실패")
            
            # 마지막 URL이 아니면 홈으로 이동
            if i < len(blog_urls):
                go_home(driver)
        
        print("\n" + "=" * 50)
        print("🎉 모든 블로그 처리 완료!")
        print("💡 수동으로 창을 닫으려면 브라우저 창을 닫거나 Ctrl+C를 누르세요.")
        print("=" * 50)
        
        # 브라우저를 열린 채로 유지
        input("Enter를 눌러 종료하세요...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
    finally:
        print("\n🔚 브라우저 종료 중...")
        driver.quit()
        print("✅ 브라우저 종료 완료")

if __name__ == "__main__":
    main()
