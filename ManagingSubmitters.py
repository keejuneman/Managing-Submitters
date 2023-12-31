import webbrowser
from datetime import datetime
import os
import tkinter as tk
from tkinter import Text, Scrollbar, ttk, filedialog, filedialog, messagebox, Toplevel
import pyautogui as p
import pickle
from screeninfo import get_monitors
import requests
import sys
import subprocess
from ttkthemes import ThemedTk
import random
import keyboard
import threading
import configparser
import time

# INFO
setting_ini_path = os.path.join(
    'C:\\Users\\rlwns\\Desktop\\FASTCAMPUS AI 6\\new', 'setting.ini')
SETTING = configparser.ConfigParser()
SETTING.read(setting_ini_path)

OWNER = SETTING["SETTING"]['OWNER']
REPO = SETTING["SETTING"]['REPO']
MY_API_KEY = SETTING["SETTING"]['MY_API_KEY']
ICON_PATH = SETTING["SETTING"]['ICON_PATH']

UPDATE_URL = SETTING["SETTING"]["UPDATE_URL"]
API_SERVER_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"

git_res = requests.get(f"{API_SERVER_URL}/releases/latest",
                       auth=(OWNER, MY_API_KEY))
git_json = git_res.json()

update_res = requests.get(UPDATE_URL,
                          auth=(OWNER, MY_API_KEY))
update_json = update_res.json()

total_members = 'total_members.txt'
categories = 'categories_list.txt'

# Version
version_info = git_json["name"]
lastupdate = git_json["created_at"][:10]

# 자동 업데이트
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    update_exe_path = os.path.join(application_path, "update.exe")
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    update_exe_path = os.path.join(application_path, "update.exe")


def create_version_file():
    global version_file_path
    version_file_path = os.path.join(application_path, "version")
    if not os.path.exists(version_file_path):
        with open(version_file_path, "w") as f:
            f.write(f"{lastupdate}T")


def version_definition():
    create_version_file()
    with open(os.path.join(application_path, "version"), "r") as f:
        global now_version
        global update_TF
        version_text = f.read()
        now_version = version_text[:-1]
        update_TF = version_text[-1]


version_definition()


def update_yes():
    messagebox.showinfo("알림", "업데이트가 완료되면 프로그램이 재시작 됩니다.")
    if git_res.status_code != 200:
        messagebox.showinfo("에러 발생", "업데이트 체크 실패")
        return
    os.chdir(application_path)
    if os.path.exists(update_exe_path):
        subprocess.run([update_exe_path], shell=True)
    else:
        pass


def update_progress(progress_bar, progress_window, percent):
    progress_bar["value"] = percent
    progress_window.update()


def show_progress_window():
    progress_window = Toplevel()
    progress_window.title("Update Progress")
    progress_window.geometry("300x100")
    progress_window.iconbitmap(
        'C:/Users/rlwns/Desktop/FASTCAMPUS AI 6/fc_icon.ico')
    label = tk.Label(progress_window, text="update 파일을 다운로드 중입니다..")
    label.pack()

    progress_bar = ttk.Progressbar(
        progress_window, orient="horizontal", length=250, mode="determinate")
    progress_bar.pack(pady=10)

    progress_window.update()
    return progress_window, progress_bar


def update_yes():
    download_url = update_json["assets"][0]["browser_download_url"]

    contents = requests.get(download_url, auth=(OWNER, MY_API_KEY), headers={
        'Accept': 'application/octet-stream'}, stream=True)
    progress_window, progress_bar = show_progress_window()
    update_file_path = os.path.join(application_path, "update.exe")

    if os.path.exists("update.exe"):
        messagebox.showinfo("알림", "업데이트가 완료되면 프로그램이 재시작 됩니다.")
        subprocess.run(["update.exe"], shell=True)
    else:
        if update_res.status_code == 200:
            messagebox.showinfo("알림", "업데이트 프로그램이 없어 프로그램을 다운로드 합니다.")
            time.sleep(1)
            try:
                with open(update_file_path, "wb") as f:
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
            os.chdir(application_path)
            update_yes()

        else:
            messagebox.showinfo("에러 발생", "업데이트 체크 실패")


def auto_update_check():
    if git_json["name"] != now_version:
        MsgBox = Toplevel(app)
        MsgBox.title("업데이트 알림")
        MsgBox.geometry("300x80")
        MsgBox.resizable(False, False)
        MsgBox.transient(app)
        MsgBox.grab_set()
        MsgBox.iconbitmap(ICON_PATH)
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        modal_width = 300
        modal_height = 80
        x = (screen_width - modal_width) // 2
        y = (screen_height - modal_height) // 2
        MsgBox.geometry("+%d+%d" % (x, y))

        label = tk.Label(MsgBox, text=f'{git_json["name"]}버전 업데이트를 진행하시겠습니까?')
        label.pack()

        auto_update_check_TOP = tk.IntVar()
        checkbox = tk.Checkbutton(
            MsgBox, text='업데이트 알림 끄기', variable=auto_update_check_TOP)
        checkbox.pack()

        yes_button = tk.Button(
            MsgBox, text="예", command=lambda: (MsgBox.destroy(), update_yes()))
        yes_button.place(relx=0.35, rely=1.0, anchor='s')

        no_button = tk.Button(MsgBox, text="아니오",
                              command=lambda: MsgBox.destroy())
        no_button.place(relx=0.65, rely=1.0, anchor='s')

        checkbox.config(command=lambda: (
            auto_update_check_var.set(0), write_version_F()))


def write_version_F():
    with open(version_file_path, "w") as f:
        f.write(f"{now_version}F")


def write_version_T():
    with open(version_file_path, "w") as f:
        f.write(f"{now_version}T")


def on_auto_update_checked():
    if auto_update_check_var.get() == 1:
        write_version_T()
    else:
        write_version_F()

# def auto_update():
#     if git_json["name"] != now_version:
#         MsgBox = messagebox.askyesno(
#             "업데이트 확인", f'{git_json["name"]}버전 업데이트를 진행하시겠습니까?')
#         if MsgBox:
#             messagebox.showinfo("알림", "업데이트가 완료되면 프로그램이 재시작 됩니다.")
#             if res.status_code != 200:
#                 messagebox.showinfo("에러 발생", "업데이트 체크 실패")
#                 return
#             os.chdir(application_path)
#             subprocess.run([update_exe_path], shell=True)
#         else:
#             messagebox.showinfo("알림", "상단 메뉴바 수동 업데이트 눌러서 진행하시길 바랍니다.")
#             with open(version_file_path, "w") as f:
#                 f.write(f"{now_version}F")
#             auto_update_check_var.set(0)


def lastest_version():
    MsgBox = messagebox.showinfo(
        "업데이트 확인", f'이미 최신 버전입니다.')


# def auto_update_check():
#     if
# 공통


def load_data(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding="cp949") as f:
            total_members = f.read().split('\n')
    else:
        total_members = []
    return total_members


def save_data(data, file_path):
    save_data = data.get("1.0", "end-1c")
    with open(file_path, 'w', encoding="cp949") as f:
        f.write(save_data)


# TAB 1
# Frame 2
def submit_participants(text_widget, clipboard_text_widget):
    participants = text_widget.get('1.0', 'end-1c').split('\n')
    absentees = list(set(load_data(total_members)) - set(participants))
    absentees_with_at = [f"@{name}" for name in absentees if name]

    result_text = "참여하지 않은 인원: "
    line = ""
    for absentee in absentees_with_at:
        if len(line + absentee) > 20:
            result_text += line.strip() + "\n"
            line = ""
        else:
            line += absentee + " "
    result_text += line.strip()

    app.clipboard_clear()
    app.clipboard_append(' '.join(absentees_with_at))
    clipboard_text_widget.delete('1.0', tk.END)
    clipboard_text_widget.insert('1.0', ' '.join(absentees_with_at))
    # messagebox.showinfo("복사 완료", "참여하지 않은 인원이 클립보드에 복사되었습니다.")


def normalize_names(names_list):
    stripped_names = [name.strip() for name in names_list]
    return [name for name in stripped_names if name]


def total_member_changed(event):
    event.widget.edit_modified(0)  # 수정 작업 완료 시 Modified flag 초기화
    total_members = event.widget.get('1.0', 'end-1c').split('\n')
    total_members = normalize_names(total_members)

    total_members_count.set(f"전체 인원: {len(total_members)} 명")


# TAB2
# Count
def submit_feedback(text_widget, categories, clipboard_text_widget):
    main_categories = set(load_data(categories))
    input_categories = text_widget.get('1.0', 'end-1c').split('\n')
    input_categories = [item.strip()
                        for sublist in input_categories for item in sublist.split(', ')]

    main_dict = {}
    other_dict = {}

    for c in input_categories:
        if c not in main_categories:
            other_dict[c] = other_dict.get(c, 0) + 1
        else:
            main_dict[c] = main_dict.get(c, 0) + 1

    count_msesage = ""
    for i, count in main_dict.items():
        count_msesage += f"{i} : {count}\n"
    if other_dict:
        count_msesage += f"기타 : {sum(other_dict.values())}\n기타 내용 : {', '.join(other_dict.keys())}"

    app.clipboard_clear()
    app.clipboard_append(count_msesage)
    clipboard_text_widget.delete('1.0', tk.END)
    clipboard_text_widget.insert('1.0', count_msesage)


# TAB3
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        selected_folder_var.set(folder_path)
        save_folder_path(folder_path)


def save_folder_path(folder_path):
    with open('folder_path.txt', 'wb') as f:
        pickle.dump(folder_path, f)


def load_folder_path():
    if os.path.isfile('folder_path.txt'):
        with open('folder_path.txt', 'rb') as f:
            folder_path = pickle.load(f)
            selected_folder_var.set(folder_path)


def open_folder():
    folder_path = selected_folder_var.get()
    if folder_path and os.path.exists(folder_path):
        if not os.path.exists(f'{folder_path}/{today_text.get("1.0", "end-1c").strip()}'):
            os.mkdir(f'{folder_path}/{today_text.get("1.0", "end-1c").strip()}')
        os.startfile(
            f'{folder_path}/{today_text.get("1.0", "end-1c").strip()}')


def attendance_check(today, text_box):
    folder_path = selected_folder_var.get()
    selected_monitor = monitor_var.get()
    input_text = None
    if text_box:
        input_text = text_box.get().strip()

    if not os.path.exists(f'{folder_path}/{today}'):
        os.mkdir(f'{folder_path}/{today}')

    selected_value = radio_var.get()
    file_base = None
    options = {1: ' 입실', 2: ' 중간', 3: ' 퇴실', 4: ' 실강', 5: ' 프로젝트'}
    if selected_value in options:
        file_base = today + options[selected_value]
    elif selected_value == 6 and input_text:
        file_base = today + input_text

    if file_base:
        count = 0
        file_path = f"{file_base}.png"
        while os.path.exists(f'{folder_path}/{today}/{file_path}'):
            count += 1
            file_path = f"{file_base}({count}).png"

        open(f'{folder_path}/{today}/{file_path}', 'w').close()

        monitors = get_monitors()
        if len(monitors) > 1:
            main_monitor = monitors[0]
            sub_monitor = monitors[1]
            main_box = (main_monitor.x, main_monitor.y,
                        main_monitor.width, main_monitor.height)
            sub_box = (sub_monitor.x, sub_monitor.y,
                       sub_monitor.width, sub_monitor.height)

        if selected_monitor == 1:
            if len(monitors) > 1:
                screenshot = p.screenshot(region=main_box)
            else:
                screenshot = p.screenshot()
        else:
            screenshot = p.screenshot(region=sub_box)

        screenshot.save(f'{folder_path}/{today}/{file_path}')


def on_radio_selected():
    selection = radio_var.get()
    if selection == 6:
        text_box.config(state=tk.NORMAL)
    else:
        text_box.delete(0, tk.END)
        text_box.config(state=tk.DISABLED)


def update_today(event):
    global today
    global new_today
    new_today = today_text.get("1.0", "end-1c").strip()
    today = new_today


def on_key_press():
    attendance_check(today_text.get("1.0", "end-1c").strip(), text_box)


def global_hotkey_listener():
    keyboard.add_hotkey('ctrl+shift+d', on_key_press)
    keyboard.wait()


# Tab4
def shuffle_teams():
    members = total_member.get("1.0", "end-1c").split('\n')
    members = [member.strip() for member in members if member.strip()]

    selected_value = int(team_count.get())  # 선택된 값을 가져옴

    if team_radio_var.get() == 1:  # 조 단위
        random.shuffle(members)
        teams = [members[i:i+selected_value]
                 for i in range(0, len(members), selected_value)]
    else:  # 명 단위
        random.shuffle(members)
        teams = []

        while members:
            for i in range(min(selected_value, len(members))):
                if len(teams) <= i:
                    teams.append([])
                teams[i].append(members.pop(0))

    result_text = ""
    # 생성된 조 정보를 문자열로 생성
    for i, team in enumerate(teams):
        result_text += f"{i+1}조: {' '.join(team)}\n"

    # 생성된 결과를 클립보드에 복사
    app.clipboard_clear()
    app.clipboard_append(result_text)
    clipboard_text3.delete("1.0", "end")
    clipboard_text3.insert("1.0", result_text)

# Menu


def show_github_address():
    url = "https://github.com/keejuneman/Managing-Submitters"
    webbrowser.open(url)


def notion_manual():
    url = "https://equable-gold-734.notion.site/LM-Managing-Program-Manual-0ca45d68b2884614b312d28aad5a3d00?pvs=4"
    webbrowser.open(url)


def bug_report():
    url = "https: // github.com/keejuneman/Managing-Submitters/issues"
    webbrowser.open(url)


def suggestions():
    url = "https://github.com/keejuneman/Managing-Submitters/issues"
    webbrowser.open(url)


def update_history():
    url = f"https://github.com/{OWNER}/{REPO}/releases/latest"
    webbrowser.open(url)


# TK
app = ThemedTk(theme="yaru")
app.title(f"LM JARVIS")
app.resizable(False, False)
app.iconbitmap(ICON_PATH)


# style
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12))
style.configure('TLabel', font=('Helvetica', 12))

# Menu
menu_bar = tk.Menu(app)

info_menu = tk.Menu(menu_bar, tearoff=0)
info_menu.add_command(label="메뉴얼", command=notion_manual)
info_menu.add_command(label="Github", command=show_github_address)
info_menu.add_command(label="버그제보", command=bug_report)
info_menu.add_command(label="건의사항", command=suggestions)
info_menu.insert_separator(2)
info_menu.insert_separator(6)

info_menu.add_command(label="종료", command=app.quit)

version_menu = tk.Menu(menu_bar, tearoff=0)
version_menu.add_command(label=f"버전: {version_info}", command=None)
version_menu.add_command(label=f"마지막 업데이트: {lastupdate}", command=None)
version_menu.add_command(label="업데이트 내역", command=update_history)

auto_update_check_var = tk.IntVar()

if update_TF == "T":
    auto_update_check_var.set(1)
else:
    auto_update_check_var.set(0)
version_menu.add_checkbutton(
    label="자동업데이트", variable=auto_update_check_var, command=on_auto_update_checked)

menu_bar.add_cascade(label="정보", menu=info_menu)
menu_bar.add_cascade(label="버전", menu=version_menu)
menu_bar.add_cascade(label="업데이트", command=lambda: auto_update_check(
) if git_json["name"] != now_version else lastest_version())


app.config(menu=menu_bar)


# TAB
notebook = ttk.Notebook(app)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)

notebook.add(tab1, text="제출인원관리")
notebook.add(tab2, text="카운트")
notebook.add(tab3, text="화면캡쳐")
notebook.add(tab4, text="랜덤조편성")

notebook.grid(row=0, column=0, rowspan=2)

# Tab1
# Frame 1: 전체 인원
total_members_frame = tk.LabelFrame(
    tab1, text="전체 인원", font=('Helvetica', 14))
total_members_frame.grid(row=0, column=0, padx=15, pady=15)

loaded_categories = '\n'.join(load_data(total_members))
total_member = Text(total_members_frame, width=60, height=10)
total_member.insert('1.0', loaded_categories)
total_member.pack(side="left")

total_member.bind("<<Modified>>", total_member_changed)

scrollbar_members = Scrollbar(
    total_members_frame, command=total_member.yview)
scrollbar_members.pack(side="left", fill='y')
total_member.config(yscrollcommand=scrollbar_members.set)

submit_members_button = ttk.Button(
    total_members_frame, text="전체 인원 저장", command=lambda: save_data(total_member, total_members))
submit_members_button.pack(side="bottom")

total_members_count = tk.StringVar()
total_members_count_label = tk.Label(
    total_members_frame, textvariable=total_members_count)
total_members_count_label.pack(side="top")
total_members_count.set(f"전체 인원: {len(load_data(total_members))} 명")

# Frame 2 : 제출 인원
participants_frame = tk.LabelFrame(
    tab1, text="참여 인원", font=('Helvetica', 14))
participants_frame.grid(row=1, column=0, padx=15, pady=15)

participants = Text(participants_frame, width=60, height=10)
participants.pack(side="left")

scrollbar_participants = Scrollbar(
    participants_frame, command=participants.yview)
scrollbar_participants.pack(side="left", fill='y')
participants.config(yscrollcommand=scrollbar_participants.set)

submit_participants_button = ttk.Button(
    participants_frame, text="참여 인원 확인", command=lambda: submit_participants(participants, clipboard_text))
submit_participants_button.pack(side="bottom")


# Frame 3: 결과
clipboard_checker_frame = tk.LabelFrame(
    tab1, text="결과", font=('Helvetica', 14))
clipboard_checker_frame.grid(row=2, column=0, padx=15, pady=15)

clipboard_text = Text(clipboard_checker_frame, width=77, height=10)
clipboard_text.pack(side="left")

scrollbar_clipboard = Scrollbar(
    clipboard_checker_frame, command=clipboard_text.yview)
scrollbar_clipboard.pack(side="left", fill='y')
clipboard_text.config(yscrollcommand=scrollbar_clipboard.set)


# Tab2
# Frame 1 : 카테고리
categories_frame = tk.LabelFrame(
    tab2, text="카테고리", font=('Helvetica', 14))
categories_frame.grid(row=0, column=1, padx=15, pady=15)

loaded_categories = '\n'.join(load_data(categories))
total_categories = Text(categories_frame, width=60, height=10)
total_categories.insert('1.0', loaded_categories)
total_categories.pack(side="left")

total_categories.bind("<<Modified>>", total_member_changed)

scrollbar_categories = Scrollbar(
    categories_frame, command=total_categories.yview)
scrollbar_categories.pack(side="left", fill='y')
total_categories.config(yscrollcommand=scrollbar_categories.set)

submit_categories_button = ttk.Button(
    categories_frame, text="카테고리 저장", command=lambda: save_data(total_categories, categories))
submit_categories_button.pack(side="bottom")

# Frame 2 : 카운팅
feedback_frame = tk.LabelFrame(
    tab2, text="카테고리 카운팅", font=('Helvetica', 14))
feedback_frame.grid(row=1, column=1, padx=15, pady=15)
feedback = Text(feedback_frame, width=60, height=10)
feedback.pack(side="left")

scrollbar_feedback = Scrollbar(feedback_frame, command=feedback.yview)
scrollbar_feedback.pack(side="left", fill='y')
feedback.config(yscrollcommand=scrollbar_feedback.set)

submit_feedback_button = ttk.Button(
    feedback_frame, text="카운팅 및 복사", command=lambda: submit_feedback(feedback, categories, clipboard_text2))
submit_feedback_button.pack(side="bottom")

result_label = tk.Label(app, text="")
result_label.grid(row=2, column=0)

# Frame 3: 결과
clipboard_checker_frame2 = tk.LabelFrame(
    tab2, text="결과", font=('Helvetica', 14))
clipboard_checker_frame2.grid(row=2, column=1, padx=15, pady=15)

clipboard_text2 = Text(clipboard_checker_frame2, width=77, height=10)
clipboard_text2.pack(side="left")

scrollbar_clipboard = Scrollbar(
    clipboard_checker_frame2, command=clipboard_text2.yview)
scrollbar_clipboard.pack(side="left", fill='y')
clipboard_text2.config(yscrollcommand=scrollbar_clipboard.set)


# Tab3
# 폴더 선택
folder_selection_frame = tk.LabelFrame(
    tab3, text="폴더선택", font=('Helvetica', 14), width=40, height=15)
folder_selection_frame.grid(
    row=1, column=1, padx=30, pady=15, rowspan=3, columnspan=2, sticky="nsew")


select_folder_button = tk.Button(
    folder_selection_frame, text="폴더 선택", command=select_folder)
select_folder_button.pack(pady=5)

selected_folder_var = tk.StringVar()
selected_folder_label = tk.Label(
    folder_selection_frame, textvariable=selected_folder_var)
selected_folder_label.pack(pady=5)

open_button = tk.Button(folder_selection_frame,
                        text="폴더 열기", command=open_folder)
open_button.pack(pady=5)

# 라디오 박스
radio_var_frame = tk.LabelFrame(tab3, text="시간선택", font=('Helvetica', 14))
radio_var_frame.grid(row=1, column=0, padx=15, pady=15, rowspan=2, sticky="w")

radio_var = tk.IntVar()
radio_var.set(1)
r1 = tk.Radiobutton(radio_var_frame, text="입실", value=1,
                    variable=radio_var, command=on_radio_selected)
r2 = tk.Radiobutton(radio_var_frame, text="중간", value=2,
                    variable=radio_var, command=on_radio_selected)
r3 = tk.Radiobutton(radio_var_frame, text="퇴실", value=3,
                    variable=radio_var, command=on_radio_selected)
r4 = tk.Radiobutton(radio_var_frame, text="실강", value=4,
                    variable=radio_var, command=on_radio_selected)
r5 = tk.Radiobutton(radio_var_frame, text="프로젝트", value=5,
                    variable=radio_var, command=on_radio_selected)
r6 = tk.Radiobutton(radio_var_frame, text="기타", value=6,
                    variable=radio_var, command=on_radio_selected)

r1.pack(pady=0)
r2.pack(pady=0)
r3.pack(pady=0)
r4.pack(pady=0)
r5.pack(pady=0)
r6.pack(pady=0)

text_box = tk.Entry(radio_var_frame, state=tk.DISABLED)
text_box.pack(padx=15, pady=3)

# # 스크린샷 버튼
select_folder_button = tk.Button(tab3, text="스크린샷(Ctrl+Shift+D)", command=lambda: attendance_check(
    today_text.get("1.0", "end-1c").strip(), text_box))
select_folder_button.grid(row=0, column=3, padx=15, pady=0, sticky="w")
app.focus_force()


global_hotkey_thread = threading.Thread(target=global_hotkey_listener)
global_hotkey_thread.daemon = True  # 데몬 스레드로 설정, 앱과 함께 종료
global_hotkey_thread.start()

# 오늘 날짜
today_time = datetime.today()
today = today_time.strftime("%y%m%d")

today_label = tk.Label(tab3, text="날짜 :", font=('Helvetica', 12))
today_label.grid(row=0, column=0, padx=15, pady=0)

today_text = tk.Text(tab3, width=25, height=1, font=('Helvetica', 12))
today_text.grid(row=0, column=1, padx=0, pady=0, sticky="w")
today_text.insert('1.0', today)
today_text.bind("<<Modified>>", update_today)

# 모니터 선택
monitor_var_frame = tk.LabelFrame(tab3, text="모니터 선택", font=('Helvetica', 14))
monitor_var_frame.grid(row=1, column=3, padx=15,
                       pady=15, rowspan=2, sticky="n")

monitor_var = tk.IntVar()
monitor_var.set(1)
m1 = tk.Radiobutton(monitor_var_frame, text="메인 모니터",
                    value=1, variable=monitor_var)
m2 = tk.Radiobutton(monitor_var_frame, text="서브 모니터", value=2,
                    variable=monitor_var, state=tk.DISABLED)

m1.pack()
m2.pack()


# tab4
total_members_frame2 = tk.LabelFrame(
    tab4, text="전체 인원", font=('Helvetica', 14))
total_members_frame2.grid(row=0, column=0, padx=15, pady=15, sticky='w')

loaded_categories = '\n'.join(load_data(total_members))
total_member = Text(total_members_frame2, width=60, height=10)
total_member.insert('1.0', loaded_categories)
total_member.pack(side="left")

total_member.bind("<<Modified>>", total_member_changed)

scrollbar_members = Scrollbar(
    total_members_frame2, command=total_member.yview)
scrollbar_members.pack(side="left", fill='y')
total_member.config(yscrollcommand=scrollbar_members.set)

submit_members_button = ttk.Button(
    total_members_frame2, text="전체 인원 저장", command=lambda: save_data(total_member, total_members))
submit_members_button.pack(side="bottom")

total_members_count = tk.StringVar()
total_members_count_label = tk.Label(
    total_members_frame2, textvariable=total_members_count)
total_members_count_label.pack(side="top")
total_members_count.set(f"전체 인원: {len(load_data(total_members))} 명")


# frame 2
team_setting_frame = tk.LabelFrame(
    tab4, text="조 편성 설정 및 실행", font=('Helvetica', 14))
team_setting_frame.grid(row=1, column=0, padx=15, pady=15, sticky='nwes')


team_radio_var = tk.IntVar()
team_radio_var.set(1)
team_r1 = tk.Radiobutton(team_setting_frame, text="팀 당 인원", value=1,
                         variable=team_radio_var)
team_r2 = tk.Radiobutton(team_setting_frame, text="팀 갯수", value=2,
                         variable=team_radio_var)
team_r1.pack()
team_r2.pack()

# number setting
count_combo = [int_num for int_num in range(1, 101)]
team_count = ttk.Combobox(team_setting_frame)
team_count.config(height=5, values=count_combo, state="nomal")
team_count.set(1)
team_count.pack()

# button
shuffle_teams_button = ttk.Button(
    team_setting_frame, text="조 편성", command=shuffle_teams)
shuffle_teams_button.pack(side='right')


# frame 4
clipboard_checker_frame3 = tk.LabelFrame(
    tab4, text="결과", font=('Helvetica', 14))
clipboard_checker_frame3.grid(row=3, column=0, padx=15, pady=15)

clipboard_text3 = Text(clipboard_checker_frame3, width=77, height=10)
clipboard_text3.pack(side="left")

scrollbar_clipboard = Scrollbar(
    clipboard_checker_frame3, command=clipboard_text3.yview)
scrollbar_clipboard.pack(side="left", fill='y')
clipboard_text3.config(yscrollcommand=scrollbar_clipboard.set)


if update_TF == 'T':
    auto_update_check()
load_folder_path()
app.mainloop()
