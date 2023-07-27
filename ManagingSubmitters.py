import os
import tkinter as tk
from collections import Counter
from tkinter import messagebox, Text, Scrollbar

categories = ['강사의 강의 진행 속도', '강의 자료', '강의 내용', '강사의 강의 전달력', '강사의 피드백']


def load_total_members():
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            total_members = [line.strip() for line in f.readlines()]
    else:
        total_members = []
    return total_members


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


app = tk.Tk()
app.title("LM 자동화 시스템")
app.resizable(False, False)

filename = 'total_members.txt'

total_members_frame = tk.Frame(app)
total_members_frame.grid(row=0, column=0, padx=15, pady=15)
total_members_label = tk.Label(total_members_frame, text="전체 인원")
total_members_label.pack(side="top")

loaded_total_members = '\n'.join(load_total_members())
total_members = Text(total_members_frame, width=40, height=20)
total_members.insert('1.0', loaded_total_members)
total_members.pack(side="left")

scrollbar_total_members = Scrollbar(
    total_members_frame, command=total_members.yview)
scrollbar_total_members.pack(side="left", fill='y')
total_members.config(yscrollcommand=scrollbar_total_members.set)

submit_total_members_button = tk.Button(
    total_members_frame, text="전체 인원 저장", command=lambda: submit_total_members(total_members))
submit_total_members_button.pack(side="bottom")

participants_frame = tk.Frame(app)
participants_frame.grid(row=1, column=0, padx=15, pady=15)
participants_label = tk.Label(participants_frame, text="참여 인원")
participants_label.pack(side="top")

participants = Text(participants_frame, width=40, height=20)
participants.pack(side="left")

scrollbar_participants = Scrollbar(
    participants_frame, command=participants.yview)
scrollbar_participants.pack(side="left", fill='y')
participants.config(yscrollcommand=scrollbar_participants.set)

submit_participants_button = tk.Button(
    participants_frame, text="참여 인원 확인", command=lambda: submit_participants(participants))
submit_participants_button.pack(side="bottom")

feedback_frame = tk.Frame(app)
feedback_frame.grid(row=0, column=1, padx=15, pady=15)
feedback_label = tk.Label(feedback_frame, text="피드백")
feedback_label.pack(side="top")
feedback = Text(feedback_frame, width=40, height=20)
feedback.pack(side="left")

scrollbar_feedback = Scrollbar(feedback_frame, command=feedback.yview)
scrollbar_feedback.pack(side="left", fill='y')
feedback.config(yscrollcommand=scrollbar_feedback.set)

submit_feedback_button = tk.Button(
    feedback_frame, text="피드백 확인", command=lambda: submit_feedback(feedback, categories))
submit_feedback_button.pack(side="bottom")

result_label = tk.Label(app, text="")
result_label.grid(row=2, column=0)

app.mainloop()
