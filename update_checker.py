import requests
import os
import sys
import time
import shutil

LATEST_VERSION_URL = "https://raw.githubusercontent.com/yourrepo/labelprinting/main/version.txt"
LATEST_EXE_URL = "https://github.com/earningbeat/labelprinting/releases/latest/download/local.exe"
INSTALL_PATH = "C:\\Program Files\\LabelPrinting\\local.exe"
CURRENT_VERSION = "1.0"

def check_for_updates():
    """GitHub에서 최신 버전 확인"""
    try:
        response = requests.get(LATEST_VERSION_URL, timeout=5)
        latest_version = response.text.strip()

        if latest_version != CURRENT_VERSION:
            print(f"🔄 새 버전({latest_version})이 있습니다. 업데이트를 진행합니다...")
            update_program()
        else:
            print("✅ 최신 버전입니다.")
    except Exception as e:
        print(f"⚠ 업데이트 확인 실패: {e}")

def update_program():
    """최신 실행 파일 다운로드 및 교체"""
    temp_exe = os.path.join(os.path.dirname(INSTALL_PATH), "local_new.exe")
    response = requests.get(LATEST_EXE_URL, stream=True)
    
    with open(temp_exe, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print("✅ 업데이트 완료! 프로그램을 다시 실행합니다...")

    # 기존 실행 파일 백업 후 교체
    backup_exe = os.path.join(os.path.dirname(INSTALL_PATH), "local_old.exe")
    if os.path.exists(INSTALL_PATH):
        os.rename(INSTALL_PATH, backup_exe)  # 기존 파일 백업
    shutil.move(temp_exe, INSTALL_PATH)  # 새 버전으로 교체

    os.system(f'start "" "{INSTALL_PATH}"')  # 새 버전 실행
    sys.exit()  # 기존 프로세스 종료

if __name__ == "__main__":  # ✅ `update_checker.py`는 독립 실행 가능해야 하므로 여기에 위치
    check_for_updates()
