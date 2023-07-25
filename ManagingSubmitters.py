import os
import tkinter as tk
from tkinter import messagebox, Text, Scrollbar


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
    result_label.config(text=f"참여하지 않은 인원: {' '.join(absentees_with_at)}")
    app.clipboard_clear()
    app.clipboard_append(' '.join(absentees_with_at))
    messagebox.showinfo("복사 완료", "참여하지 않은 인원이 클립보드에 복사되었습니다.")


app = tk.Tk()
app.title("참여자 관리")

filename = 'total_members.txt'

total_members_frame = tk.Frame(app)
total_members_frame.pack(padx=15, pady=15)
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
participants_frame.pack(padx=15, pady=15)
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

result_label = tk.Label(app, text="")
result_label.pack(side="bottom")

app.mainloop()
