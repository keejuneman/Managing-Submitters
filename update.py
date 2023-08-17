import os
import requests
import sys
import shutil
import subprocess
from tkinter import messagebox
from tkinter import messagebox, Tk, Label, ttk
import configparser
import time

setting_ini_path = os.path.join(
    'setting.ini_PATH', 'setting.ini')
SETTING = configparser.ConfigParser()
SETTING.read(setting_ini_path)

OWNER = SETTING["SETTING"]['OWNER']
REPO = SETTING["SETTING"]['REPO']
MY_API_KEY = SETTING["SETTING"]['MY_API_KEY']
ICON_PATH = SETTING["SETTING"]['ICON_PATH']

API_SERVER_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"

res = requests.get(f"{API_SERVER_URL}/releases/latest",
                   auth=(OWNER, MY_API_KEY))
git_json = res.json()

# application_path = os.path.dirname(os.path.abspath(__file__))
lastupdate = git_json["created_at"][:10]


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


def create_version_file():
    version_file_path = os.path.join(application_path, "version")
    if not os.path.exists(version_file_path):
        with open(version_file_path, "w") as f:
            f.write(f"{lastupdate}")


def terminate_program(program_name):
    try:
        output = subprocess.check_output(["tasklist"]).decode("cp949")
        if program_name in output:
            subprocess.run(["taskkill", "/f", "/im", program_name])
            print(f"{program_name} has been terminated.")
        else:
            print(f"{program_name} is not running.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


def show_progress_window():
    progress_window = Tk()
    progress_window.title("Update Progress")
    progress_window.geometry("300x100")
    progress_window.iconbitmap(
        'C:/Users/rlwns/Desktop/FASTCAMPUS AI 6/fc_icon.ico')
    label = Label(progress_window, text="Updating... Please wait.")
    label.pack()

    progress_bar = ttk.Progressbar(
        progress_window, orient="horizontal", length=250, mode="determinate")
    progress_bar.pack(pady=10)

    progress_window.update()
    return progress_window, progress_bar


def update_progress(progress_bar, progress_window, percent):
    progress_bar["value"] = percent
    progress_window.update()


def auto_update():
    create_version_file()
    with open(os.path.join(application_path, "version"), "r") as f:
        now_version = f.read()

    if git_json["name"] != now_version:
        if res.status_code != 200:
            messagebox.showinfo("에러 발생", "업데이트 체크 실패")
            return

        file_name = "LM_JARVIS.exe"
        download_url = git_json["assets"][0]["browser_download_url"]

        contents = requests.get(download_url, auth=(OWNER, MY_API_KEY), headers={
            'Accept': 'application/octet-stream'}, stream=True)

        progress_window, progress_bar = show_progress_window()

        os.makedirs(os.path.join(application_path, "update"), exist_ok=True)

        temp_file_path = os.path.join(
            application_path, 'update', file_name)

        try:
            with open(temp_file_path, "wb") as f:
                total_size = int(contents.headers['Content-Length'])
                downloaded_size = 0
                for chunk in contents.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    percent = (downloaded_size / total_size) * 100
                    update_progress(progress_bar, progress_window, percent)

        except Exception as e:
            messagebox.showinfo("에러 발생", f"다음 오류가 발생했습니다:\n{e}")
            return
        progress_window.destroy()

        try:
            with open(os.path.join(application_path, "version"), "w") as f:
                f.write(str(git_json["name"]+"T"))
        except Exception as e:
            messagebox.showinfo("에러 발생", f"버전 파일 업데이트 중 오류가 발생했습니다:\n{e}")

        try:
            terminate_program("LM_JARVIS.exe")
            time.sleep(1)
        except Exception as e:
            messagebox.showinfo("에러발생", f"프로세스 종료 중 오류가 발생했습니다. \n{e}")

        try:
            target_file_path = os.path.join(application_path, "LM_JARVIS.exe")

            shutil.copy(temp_file_path, target_file_path)

            subprocess.Popen([target_file_path])

        except Exception as e:
            messagebox.showinfo("에러 발생", f"파일 복사 중 오류가 발생했습니다:\n{e}")
            return

        update_folder_path = os.path.join(application_path, "update")
        try:
            shutil.rmtree(update_folder_path)
        except Exception as e:
            messagebox.showinfo("에러 발생", f"폴더 삭제 중 오류가 발생했습니다:\n{e}")

        sys.exit()


auto_update()
