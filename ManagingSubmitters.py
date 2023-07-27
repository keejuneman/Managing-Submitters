import os
import tkinter as tk
from collections import Counter
from tkinter import messagebox, Text, Scrollbar, ttk

categories = ['강사의 강의 진행 속도', '강의 자료', '강의 내용', '강사의 강의 전달력', '강사의 피드백']


def load_total_members(file_path='total_members.txt'):
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding="cp949") as f:
            total_members = f.read().split('\n')
    else:
        total_members = []
    return total_members


def submit_total_members(total_members_widget):
    total_members = total_members_widget.get("1.0", "end-1c")
    with open(filename, 'w', encoding="cp949") as f:
        f.write(total_members)


def save_total_members(text_widget):
    tm = text_widget.get('1.0', 'end-1c').split('\n')
    with open(filename, 'w') as f:
        for member in tm:
            f.write(member + "\n")


def submit_total_members(text_widget):
    save_total_members(text_widget)


def submit_participants(text_widget):
    participants = text_widget.get('1.0', 'end-1c').split('\n')
    absentees = list(set(load_total_members()) - set(participants))
    absentees_with_at = [f"@{name}" for name in absentees]

    result_text = "참여하지 않은 인원: "
    line = ""
    for absentee in absentees_with_at:
        if len(line + absentee) > 20:
            result_text += line.strip() + "\n"
            line = ""
        else:
            line += absentee + " "
    result_text += line.strip()

    # result_label.config(text=result_text)
    app.clipboard_clear()
    app.clipboard_append(' '.join(absentees_with_at))
    messagebox.showinfo("복사 완료", "참여하지 않은 인원이 클립보드에 복사되었습니다.")


def submit_feedback(text_widget, categories):
    feedback = text_widget.get('1.0', 'end-1c')
    feedback = [item.strip() for sublist in feedback.split('\n')
                for item in sublist.split(', ')]
    feedback_counter = Counter(feedback)
    feedback_text = ""
    for category in categories:
        count = feedback_counter[category]
        if len(feedback_text + f"{category} : {count}명") > 20:
            feedback_text += f"{category} :\n{count}명\n"
        else:
            feedback_text += f"{category} : {count}명\n"

    other_feedback = [f for f in feedback if f not in categories]
    feedback_text += f"기타 : {len(other_feedback)}명\n 기타 내용 : {', '.join(other_feedback)}"
    # feedback_label.config(text=feedback_text)
    app.clipboard_clear()
    app.clipboard_append(feedback_text)
    messagebox.showinfo("복사 완료", "피드백 결과가 클립보드에 복사되었습니다.")


def show_copied_text(text_widget):
    copied_text = app.clipboard_get()
    text_widget.delete('1.0', tk.END)
    text_widget.insert('1.0', copied_text)


def normalize_names(names_list):
    stripped_names = [name.strip() for name in names_list]
    return [name for name in stripped_names if name]


def total_member_changed(event):
    event.widget.edit_modified(0)  # 수정 작업 완료 시 Modified flag 초기화
    total_members = event.widget.get('1.0', 'end-1c').split('\n')
    total_members = normalize_names(total_members)

    total_members_count.set(f"전체 인원: {len(total_members)} 명")


app = tk.Tk()
app.title("LM 자동화 시스템 Beta 0.1v")
app.resizable(False, False)
app.iconbitmap('fc_icon.ico')

# style
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12))
style.configure('TLabel', font=('Helvetica', 12))

filename = 'total_members.txt'

# Frame 1: 전체 인원
total_members_frame = tk.LabelFrame(
    app, text="전체 인원", font=('Helvetica', 14))
total_members_frame.grid(row=0, column=0, padx=15, pady=15)

loaded_total_members = '\n'.join(load_total_members())
total_members = Text(total_members_frame, width=40, height=20)
total_members.insert('1.0', loaded_total_members)
total_members.pack(side="left")

total_members.bind("<<Modified>>", total_member_changed)

scrollbar_total_members = Scrollbar(
    total_members_frame, command=total_members.yview)
scrollbar_total_members.pack(side="left", fill='y')
total_members.config(yscrollcommand=scrollbar_total_members.set)

submit_total_members_button = ttk.Button(
    total_members_frame, text="전체 인원 저장", command=lambda: submit_total_members(total_members))
submit_total_members_button.pack(side="bottom")

total_members_count = tk.StringVar()
total_members_count_label = tk.Label(
    total_members_frame, textvariable=total_members_count)
total_members_count_label.pack(side="top")
total_members_count.set(f"전체 인원: {len(load_total_members())} 명")

# Frame 2 : 제출 인원
participants_frame = tk.LabelFrame(
    app, text="참여 인원", font=('Helvetica', 14))
participants_frame.grid(row=1, column=0, padx=15, pady=15)

participants = Text(participants_frame, width=40, height=20)
participants.pack(side="left")

scrollbar_participants = Scrollbar(
    participants_frame, command=participants.yview)
scrollbar_participants.pack(side="left", fill='y')
participants.config(yscrollcommand=scrollbar_participants.set)

submit_participants_button = ttk.Button(
    participants_frame, text="참여 인원 확인", command=lambda: submit_participants(participants))
submit_participants_button.pack(side="bottom")

# Frame 3 : 만족도 조사 결과
feedback_frame = tk.LabelFrame(
    app, text="피드백", font=('Helvetica', 14))
feedback_frame.grid(row=0, column=1, padx=15, pady=15)
feedback = Text(feedback_frame, width=40, height=20)
feedback.pack(side="left")

scrollbar_feedback = Scrollbar(feedback_frame, command=feedback.yview)
scrollbar_feedback.pack(side="left", fill='y')
feedback.config(yscrollcommand=scrollbar_feedback.set)

submit_feedback_button = ttk.Button(
    feedback_frame, text="피드백 확인", command=lambda: submit_feedback(feedback, categories))
submit_feedback_button.pack(side="bottom")

result_label = tk.Label(app, text="")
result_label.grid(row=2, column=0)

# Frame 4: 메모장
clipboard_checker_frame = tk.LabelFrame(
    app, text="복사한 텍스트 확인", font=('Helvetica', 14))
clipboard_checker_frame.grid(row=1, column=1, padx=15, pady=15)

clipboard_text = Text(clipboard_checker_frame, width=55, height=20)
clipboard_text.pack(side="left")

scrollbar_clipboard = Scrollbar(
    clipboard_checker_frame, command=clipboard_text.yview)
scrollbar_clipboard.pack(side="left", fill='y')
clipboard_text.config(yscrollcommand=scrollbar_clipboard.set)


app.mainloop()
