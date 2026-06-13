"""
Git 자동 커밋 및 푸시 스크립트

이 스크립트는 지정된 워크스페이스 내의 파일 변경(생성, 수정, 삭제)을 감시하여
변경 사항이 감지되면 자동으로 git add, git commit, git push를 수행합니다.
watchdog 라이브러리를 사용하며, 디바운스 대기 시간(3초)을 적용해
단기간에 발생하는 연속적인 파일 변경을 모아서 한 번에 처리합니다.
"""
import os
import sys
import time
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 설정
DEBOUNCE_SECONDS = 3.0
WATCH_PATH = "."  # 현재 디렉토리
IGNORE_PATTERNS = [
    ".git",
    ".venv",
    "__pycache__",
    ".streamlit",
    ".ipynb_checkpoints",
    "auto_git_sync.py",
    "run_auto_sync.bat",
]

class AutoGitSyncHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.timer = None
        self.lock = threading.Lock()

    def on_any_event(self, event):
        # 디렉토리 자체의 이벤트는 무시
        if event.is_directory:
            return

        # 무시할 경로 패턴 체크
        path = os.path.abspath(event.src_path)
        path_parts = path.split(os.sep)
        
        # 무시 패턴 디렉토리가 경로 상에 있는지 확인
        for ignore in IGNORE_PATTERNS:
            if ignore in path_parts or ignore in os.path.basename(path):
                return

        # 디버그용 출력
        print(f"[감지] 파일 변경됨: {event.event_type} - {os.path.relpath(event.src_path)}")
        self.reset_timer()

    def reset_timer(self):
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(DEBOUNCE_SECONDS, self.sync_git)
            self.timer.start()

    def sync_git(self):
        print("\n[동기화] 변경 사항 커밋 및 푸시 프로세스 시작...")
        try:
            # 1. git status 확인하여 변경사항이 있는지 검사
            status_proc = subprocess.run(
                ["git", "status", "--porcelain"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            changes = status_proc.stdout.strip()
            if not changes:
                print("[동기화] 변경된 파일이 없어 작업을 생략합니다.")
                return

            print("[동기화] 변경 내용 감지:")
            print(changes)

            # 2. git add
            print("[동기화] git add -A 실행 중...")
            subprocess.run(["git", "add", "-A"], check=True)

            # 3. 현재 브랜치 이름 조회
            branch_proc = subprocess.run(
                ["git", "symbolic-ref", "--short", "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            branch = branch_proc.stdout.strip()
            if not branch:
                # 분리된 HEAD 상태일 때
                branch = "main"

            # 4. git commit
            kst_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            commit_msg = f"Auto-commit: {kst_time} 변경사항 자동 반영"
            print(f"[동기화] git commit -m \"{commit_msg}\" 실행 중...")
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)

            # 5. git push
            print(f"[동기화] git push origin {branch} 실행 중...")
            push_proc = subprocess.run(
                ["git", "push", "origin", branch],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if push_proc.returncode == 0:
                print("[동기화] 성공적으로 원격 저장소에 반영되었습니다!\n")
            else:
                print(f"[오류] 푸시 실패 (에러 코드: {push_proc.returncode})")
                print(push_proc.stderr)
                
                # pull 및 rebase 시도
                print("[동기화] 원격 변경 사항 병합을 위해 git pull --rebase origin {} 실행 중...".format(branch))
                pull_proc = subprocess.run(["git", "pull", "--rebase", "origin", branch])
                if pull_proc.returncode == 0:
                    print("[동기화] 병합 성공. 다시 푸시를 시도합니다...")
                    subprocess.run(["git", "push", "origin", branch])
                else:
                    print("[오류] pull 및 rebase가 실패했습니다. 수동 충돌 해결이 필요합니다.")
                    
        except subprocess.CalledProcessError as e:
            print(f"[오류] Git 명령 실행 오류 발생: {e}")
        except Exception as e:
            print(f"[오류] 예외 발생: {e}")

if __name__ == "__main__":
    print("==================================================")
    print("   Git 자동 커밋 & 푸시 Watcher 시작")
    print("   감시 경로: ", os.path.abspath(WATCH_PATH))
    print("   디바운스 대기 시간: ", DEBOUNCE_SECONDS, "초")
    print("   종료하려면 Ctrl+C를 누르세요.")
    print("==================================================")
    
    event_handler = AutoGitSyncHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nWatcher를 종료합니다.")
        observer.stop()
    observer.join()
