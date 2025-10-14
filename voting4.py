#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from gpiozero import Button
import serial
import time
import requests
from datetime import datetime

# -----------------------------
# Firebase setup
# -----------------------------
DB_URL = "https://e-vm-f7bdf-default-rtdb.firebaseio.com"

def push_vote(candidate_name, voter_id=None):
    payload = {
        "candidate": candidate_name,
        "voter_id": voter_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        response = requests.post(f"{DB_URL}/votes.json", json=payload)
        if response.status_code == 200:
            print(f"✅ Vote for {candidate_name} pushed to Firebase")
        else:
            print(f"❌ Failed to push vote: {response.text}")
    except Exception as e:
        print(f"❌ Exception while pushing vote: {e}")

def get_voter_name(voter_id):
    try:
        res = requests.get(f"{DB_URL}/voters/{voter_id}.json")
        if res.status_code == 200 and res.json():
            return res.json().get("name", "Unknown Voter")
        else:
            return "Unknown Voter"
    except Exception as e:
        print(f"❌ Failed to fetch voter name: {e}")
        return "Unknown Voter"

def has_already_voted(voter_id):
    """Check if voter already cast a vote."""
    try:
        res = requests.get(f"{DB_URL}/votes.json")
        if res.status_code == 200 and res.json():
            for key, val in res.json().items():
                if val.get("voter_id") == str(voter_id):
                    return True
        return False
    except Exception as e:
        print(f"❌ Error checking previous votes: {e}")
        return False

# -----------------------------
# Serial setup
# -----------------------------
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
time.sleep(2)

while True:
    if ser.in_waiting > 0:
        msg = ser.readline().decode().strip()
        print(msg)
        if "FINGERPRINT_READY" in msg:
            print("✅ Sensor ready!")
            break
        elif "FINGERPRINT_ERROR" in msg:
            print("❌ Sensor error")
            exit()

# -----------------------------
# Candidate setup
# -----------------------------
candidates = [
    {"name": "Alice", "image": "candidate1.jpg", "gpio": 17},
    {"name": "Bob", "image": "candidate2.jpg", "gpio": 27},
    {"name": "Charlie", "image": "candidate3.jpg", "gpio": 22}
]

# -----------------------------
# GPIO Buttons
# -----------------------------
try:
    buttons = {c["name"]: Button(c["gpio"], pull_up=True, bounce_time=0.2) for c in candidates}
except Exception as e:
    print("❌ GPIO setup failed. Run with sudo")
    print(e)
    exit()

# -----------------------------
# Tkinter setup
# -----------------------------
root = Tk()
root.title("Electronic Voting Machine")
root.configure(bg="#F4F7FA")

screen_width = 848
screen_height = 480
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.resizable(False, False)

style = ttk.Style()
style.configure("TLabel", background="#F4F7FA", foreground="#222", font=("Arial", 20))
style.configure("Title.TLabel", background="#F4F7FA", foreground="#0056b3", font=("Arial", 28, "bold"))
style.configure("Message.TLabel", background="#F4F7FA", foreground="#007700", font=("Arial", 22, "bold"))

last_voter_id = None
last_voter_name = None

# -----------------------------
# Screens
# -----------------------------
def show_fingerprint_screen():
    for w in root.winfo_children():
        w.destroy()

    frame = Frame(root, bg="#F4F7FA")
    frame.pack(expand=True, fill=BOTH)

    ttk.Label(frame, text="Place your finger on the sensor", style="Title.TLabel").pack(pady=60)
    ttk.Label(frame, text="Waiting for fingerprint...", style="TLabel").pack(pady=20)
    root.update()
    wait_for_fingerprint()

def show_already_voted_screen():
    for w in root.winfo_children():
        w.destroy()
    frame = Frame(root, bg="#FFF8E1")
    frame.pack(expand=True, fill=BOTH)
    ttk.Label(frame, text="⚠️ You have already voted!", style="Title.TLabel").pack(pady=50)
    ttk.Label(frame, text="Multiple voting is not allowed.", style="Message.TLabel").pack(pady=20)
    root.after(3000, show_fingerprint_screen)

def wait_for_fingerprint():
    global last_voter_id, last_voter_name
    ser.write(b'CHECK\n')
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response:
                print(f"Arduino → {response}")
                if response.startswith("MATCH"):
                    last_voter_id = response.split(":")[1]
                    last_voter_name = get_voter_name(last_voter_id)
                    print(f"Fingerprint matched: {last_voter_id} ({last_voter_name})")

                    # 🧠 Check if already voted
                    if has_already_voted(last_voter_id):
                        print("❌ Already voted")
                        show_already_voted_screen()
                        return

                    show_recognized_screen(last_voter_name)
                    return
                elif response == "NO_MATCH":
                    print("Fingerprint not recognized. Try again.")
                    ser.write(b'CHECK\n')
        root.update()

def show_recognized_screen(voter_name):
    for w in root.winfo_children():
        w.destroy()

    frame = Frame(root, bg="#E8F5E9")
    frame.pack(expand=True, fill=BOTH)

    ttk.Label(frame, text="Fingerprint recognized!", style="Title.TLabel").pack(pady=50)
    ttk.Label(frame, text=f"Mr. {voter_name}, you can now cast your vote.", style="Message.TLabel").pack(pady=20)
    root.after(2500, show_candidates_screen)

def show_candidates_screen():
    for w in root.winfo_children():
        w.destroy()

    ttk.Label(root, text="Vote for Your Candidate", style="Title.TLabel").pack(pady=20)
    frame = Frame(root, bg="#F4F7FA")
    frame.pack(pady=20)

    candidate_labels = {}

    for i, c in enumerate(candidates):
        card = Frame(frame, bg="#FFFFFF", relief=RAISED, borderwidth=2)
        card.grid(row=0, column=i, padx=30, ipadx=10, ipady=10)

        try:
            img = Image.open(c["image"])
            img = img.resize((130, 130))
            photo = ImageTk.PhotoImage(img)
            label_img = Label(card, image=photo, bg="#FFFFFF")
            label_img.photo = photo
            label_img.pack(pady=5)
        except Exception as e:
            print(f"Error loading {c['image']}: {e}")

        lbl_name = Label(card, text=c["name"], bg="#FFFFFF", fg="#000", font=("Arial", 18, "bold"))
        lbl_name.pack(pady=10)
        candidate_labels[c["name"]] = lbl_name

    def record_vote(candidate_name):
        for name, lbl in candidate_labels.items():
            lbl.config(fg="#000")
        candidate_labels[candidate_name].config(fg="#E53935")

        print(f"Vote recorded for {candidate_name}")
        with open("votes.csv", "a") as f:
            f.write(f"{last_voter_id},{last_voter_name},{candidate_name},{datetime.utcnow().isoformat()}\n")

        push_vote(candidate_name, last_voter_id)

        for w in root.winfo_children():
            w.destroy()
        ttk.Label(root, text="✅ Thank you for voting!", style="Title.TLabel").pack(expand=True)
        root.after(3000, show_fingerprint_screen)

    def check_buttons():
        for name, btn in buttons.items():
            if btn.is_pressed:
                record_vote(name)
                return
        root.after(100, check_buttons)

    check_buttons()

# -----------------------------
# Start
# -----------------------------
show_fingerprint_screen()
root.mainloop()
