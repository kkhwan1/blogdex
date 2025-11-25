"""
공유 결과 저장 모듈
크롤링 결과를 JSON 파일로 저장하고 등급 정보를 관리
"""

import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, Optional

# 등급 매핑 데이터 (blogdex_selenium_login.py에서 이동)
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
    },
    "최적4": {
        "level": "마스터1",
        "level_en": "Master1",
        "tier": "마스터 블로거",
        "tier_en": "Master Blogger",
        "tier_rank": 1
    },
    "최적5": {
        "level": "마스터2",
        "level_en": "Master2",
        "tier": "마스터 블로거",
        "tier_en": "Master Blogger",
        "tier_rank": 2
    },
    "최적6": {
        "level": "마스터3",
        "level_en": "Master3",
        "tier": "마스터 블로거",
        "tier_en": "Master Blogger",
        "tier_rank": 3
    },
    "최적7": {
        "level": "마스터4",
        "level_en": "Master4",
        "tier": "마스터 블로거",
        "tier_en": "Master Blogger",
        "tier_rank": 4
    },
    "최적7+": {
        "level": "마스터5",
        "level_en": "Master5",
        "tier": "마스터 블로거",
        "tier_en": "Master Blogger",
        "tier_rank": 5
    }
}


def build_blog_id(url: str) -> str:
    """
    URL에서 블로그 ID 추출

    Args:
        url: 블로그 URL

    Returns:
        블로그 ID (예: "nightd", "nyang2ne")
    """
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        # blog.naver.com/{blog_id} 형식
        if 'blog.naver.com' in parsed.netloc and len(path_parts) >= 1:
            return path_parts[0]

        # 기본값: 호스트명 사용
        return parsed.netloc.replace('.', '_')
    except Exception as e:
        # 실패 시 타임스탬프 사용
        return f"unknown_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def get_level_info(grade: str) -> Optional[Dict]:
    """
    등급을 기반으로 레벨 정보 반환

    Args:
        grade: BlogDex 등급 (예: "최적2+", "준최5")

    Returns:
        레벨 정보 딕셔너리 또는 None
    """
    try:
        if grade in GRADE_MAPPING:
            level_info = GRADE_MAPPING[grade].copy()
            return level_info
        else:
            # 알 수 없는 등급
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


def persist_result(data: Dict, output_dir: str = "data/json_results") -> Optional[str]:
    """
    크롤링 결과를 JSON 파일로 저장 (원자적 쓰기)

    Args:
        data: 저장할 결과 데이터
        output_dir: 저장 디렉토리

    Returns:
        저장된 파일 경로 또는 None
    """
    try:
        # 디렉토리 생성 (존재하지 않으면)
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 블로그 ID 추출
        blog_id = data.get('blog_id') or build_blog_id(data.get('url', ''))

        # 타임스탬프 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 파일명 생성
        filename = f"{blog_id}_grade_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        # 임시 파일에 쓰기 (원자적 쓰기)
        temp_filepath = filepath + ".tmp"

        with open(temp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 임시 파일을 최종 파일로 rename (원자적 연산)
        os.replace(temp_filepath, filepath)

        print(f"💾 결과 저장 완료: {filepath}")
        return filepath

    except Exception as e:
        print(f"❌ 결과 저장 실패: {e}")
        return None


def enrich_result(url: str, grade: Optional[str], success: bool, error: Optional[str] = None) -> Dict:
    """
    크롤링 결과를 메타데이터로 보강

    Args:
        url: 블로그 URL
        grade: BlogDex 등급 (성공 시)
        success: 성공 여부
        error: 에러 메시지 (실패 시)

    Returns:
        보강된 결과 딕셔너리
    """
    result = {
        "url": url,
        "blog_id": build_blog_id(url),
        "grade": grade,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "success": success
    }

    # 성공한 경우 레벨 정보 추가
    if success and grade:
        level_info = get_level_info(grade)
        if level_info:
            result.update({
                "level": level_info.get("level"),
                "level_en": level_info.get("level_en"),
                "tier": level_info.get("tier"),
                "tier_en": level_info.get("tier_en"),
                "tier_rank": level_info.get("tier_rank")
            })
    else:
        # 실패한 경우
        result.update({
            "level": None,
            "level_en": None,
            "tier": None,
            "tier_en": None,
            "tier_rank": None
        })

    # 에러 메시지 추가
    if error:
        result["error"] = error

    return result
