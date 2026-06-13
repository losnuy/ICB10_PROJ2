@echo off
chcp 65001 > nul
echo.
echo ===================================================
echo   Streamlit 네이버 API 대시보드 서버를 시작합니다
echo ===================================================
echo.
".venv\Scripts\python.exe" naver-api-app/run_dashboard.py
pause
