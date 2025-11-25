"""
현재 열려있는 Chrome 브라우저의 blogdex.space 쿠키를 저장
"""
import pickle
import sqlite3
import os
import shutil
from pathlib import Path

def get_chrome_cookies():
    """Chrome 브라우저의 쿠키 DB에서 blogdex.space 쿠키 추출"""
    # Chrome 쿠키 DB 경로 (Windows)
    chrome_cookie_path = Path(os.environ['LOCALAPPDATA']) / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Network' / 'Cookies'

    if not chrome_cookie_path.exists():
        # 다른 경로 시도
        chrome_cookie_path = Path(os.environ['LOCALAPPDATA']) / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Cookies'

    if not chrome_cookie_path.exists():
        print(f"Chrome 쿠키 파일을 찾을 수 없습니다: {chrome_cookie_path}")
        return None

    # 임시 복사본 만들기 (Chrome이 사용 중이므로)
    temp_cookie_path = Path('temp_cookies.db')
    shutil.copy2(chrome_cookie_path, temp_cookie_path)

    try:
        conn = sqlite3.connect(temp_cookie_path)
        cursor = conn.cursor()

        # blogdex.space 관련 쿠키만 추출
        cursor.execute("""
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies
            WHERE host_key LIKE '%blogdex%'
        """)

        cookies = []
        for row in cursor.fetchall():
            cookie = {
                'domain': row[0],
                'name': row[1],
                'value': row[2],
                'path': row[3],
                'expiry': row[4] // 1000000 - 11644473600 if row[4] else None,
                'secure': bool(row[5]),
                'httpOnly': bool(row[6])
            }
            cookies.append(cookie)
            print(f"쿠키 발견: {row[1]} = {row[2][:20]}...")

        conn.close()
        return cookies
    except Exception as e:
        print(f"쿠키 읽기 오류: {e}")
        return None
    finally:
        if temp_cookie_path.exists():
            temp_cookie_path.unlink()

if __name__ == "__main__":
    print("=" * 60)
    print("Chrome 브라우저에서 blogdex.space 쿠키 추출")
    print("=" * 60)

    cookies = get_chrome_cookies()

    if cookies:
        # cookies.pkl로 저장
        with open('cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)
        print(f"\n총 {len(cookies)}개의 쿠키를 cookies.pkl에 저장했습니다.")
    else:
        print("\n쿠키를 찾을 수 없습니다.")
        print("브라우저에서 blogdex.space에 로그인되어 있는지 확인하세요.")
