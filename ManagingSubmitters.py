import webbrowser
from datetime import datetime
import os
import tkinter as tk
from tkinter import Text, Scrollbar, ttk, filedialog, filedialog, messagebox
import pyautogui as p
import pickle
from screeninfo import get_monitors
import requests
import sys
import subprocess
from ttkthemes import ThemedTk

# INFO
OWNER = 'YOUR_NAME'
REPO = 'YOUT_REPO'
API_SERVER_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"

MY_API_KEY = 'YOUR_TOKEN'

res = requests.get(f"{API_SERVER_URL}/releases/latest",
                   auth=(OWNER, MY_API_KEY))
git_json = res.json()

# File Path
total_members = 'total_members.txt'
categories = 'categories_list.txt'

# Version
version_info = git_json["name"]
lastupdate = git_json["created_at"][:10]

# 자동 업데이트
application_path = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    update_exe_path = os.path.join(application_path, "update.exe")
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    update_exe_path = os.path.join(application_path, "update.exe")


def create_version_file():
    version_file_path = os.path.join(application_path, "version")
    if not os.path.exists(version_file_path):
        with open(version_file_path, "w") as f:
            f.write(f"{lastupdate}")


def auto_update():
    create_version_file()
    with open(os.path.join(application_path, "version"), "r") as f:
        now_version = f.read()

    if git_json["name"] != now_version:
        MsgBox = messagebox.askyesno(
            "업데이트 확인", f'{git_json["name"]}버전 업데이트를 진행하시겠습니까?')
        if MsgBox:
            messagebox.showinfo("알림", "업데이트가 완료되면 프로그램이 재시작 됩니다.")
            if res.status_code != 200:
                messagebox.showinfo("에러 발생", "업데이트 체크 실패")
                return
            os.chdir(application_path)
            subprocess.run([update_exe_path], shell=True)


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


# Menu
def show_github_address():
    url = "https://github.com/keejuneman/Managing-Submitters"
    webbrowser.open(url)


def notion_manual():
    url = "https://equable-gold-734.notion.site/LM-Managing-Program-Manual-0ca45d68b2884614b312d28aad5a3d00?pvs=4"
    webbrowser.open(url)


def bug_report():
    url = "https://equable-gold-734.notion.site/LM-Managing-Program-Manual-0ca45d68b2884614b312d28aad5a3d00?pvs=4"
    webbrowser.open(url)


def suggestions():
    url = "https://equable-gold-734.notion.site/LM-Managing-Program-Manual-0ca45d68b2884614b312d28aad5a3d00?pvs=4"
    webbrowser.open(url)


# TK
app = ThemedTk(theme="yaru")
app.title(f"LM JARVIS")
app.resizable(False, False)
app.iconbitmap('C:/Users/rlwns/Desktop/FASTCAMPUS AI 6/fc_icon.ico')


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
version_menu.add_command(label="패치내역", command=None)


menu_bar.add_cascade(label="정보", menu=info_menu)
menu_bar.add_cascade(label="버전", menu=version_menu)

app.config(menu=menu_bar)


# TAB
notebook = ttk.Notebook(app)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)


notebook.add(tab1, text="제출인원관리")
notebook.add(tab2, text="카운트")
notebook.add(tab3, text="화면캡쳐")

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
radio_var_frame.grid(row=1, column=0, padx=15, pady=15, rowspan=2, sticky="n")

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
select_folder_button = tk.Button(tab3, text="스크린샷", command=lambda: attendance_check(
    today_text.get("1.0", "end-1c").strip(), text_box))
select_folder_button.grid(row=0, column=3, padx=15, pady=0, sticky="w")

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

auto_update()
load_folder_path()
app.mainloop()
