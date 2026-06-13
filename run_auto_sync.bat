@echo off
chcp 65001 > nul
echo ==================================================
echo   Git 자동 동기화(Watcher) 백그라운드 프로세스 시작
echo   종료하려면 이 창에서 Ctrl+C를 누르십시오.
echo ==================================================
echo.
.venv\Scripts\python.exe auto_git_sync.py
pause
