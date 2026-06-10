"""
Streamlit 대시보드 애플리케이션을 구동하기 위한 진입점 스크립트입니다.
Windows 환경의 권한 문제(credentials.toml 접근 불가) 및 초기 이메일 입력 프롬프트를
우회하기 위해 streamlit.runtime.credentials 모듈을 패치한 후 대시보드를 실행합니다.
"""
# -*- coding: utf-8 -*-
import sys
import os
import streamlit.web.bootstrap
from streamlit.runtime.credentials import Credentials

def mock_load(self):
    """
    Streamlit의 Credentials 로딩 과정을 모킹하여 파일 읽기/쓰기를 차단하고
    이메일 프롬프트 입력을 건너뜁니다.
    """
    self._email = ""
    self._activated = True

# Credentials.load 함수를 모킹 함수로 대체
Credentials.load = mock_load

if __name__ == "__main__":
    # 실행 경로를 src/app.py로 지정하고 텔레메트리 비활성화 옵션을 전달하여 streamlit 기동
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "src", "app.py")
    sys.argv = ["streamlit", "run", app_path, "--browser.gatherUsageStats=false"]
    # streamlit.web.bootstrap.run에 필요한 4가지 인자를 전달
    streamlit.web.bootstrap.run(app_path, False, [], {})
