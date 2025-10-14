#!/usr/bin/env python3
from tkinter import *
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
    """Send a vote record to Firebase"""
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
    """Fetch voter name from Firebase using voter_id"""
    try:
        res = requests.get(f"{DB_URL}/voters/{voter_id}.json")
        if res.status_code == 200 and res.json():
            return res.json().get("name", "Unknown Voter")
        else:
            return "Unknown Voter"
    except Exception as e:
        print(f"❌ Failed to fetch voter name: {e}")
        return "Unknown Voter"

# -----------------------------
# Serial setup (Arduino + fingerprint)
# -----------------------------
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
time.sleep(2)

# Wait for sensor ready
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
    {"name": "Alice", "image": "candidate1.jpg", "gpio": 17},  # BCM17
    {"name": "Bob", "image": "candidate2.jpg", "gpio": 27},    # BCM27
    {"name": "Charlie", "image": "candidate3.jpg", "gpio": 22} # BCM22
]

# -----------------------------
# GPIO Buttons
# -----------------------------
try:
    buttons = {c["name"]: Button(c["gpio"], pull_up=True, bounce_time=0.2) for c in candidates}
except Exception as e:
    print("❌ GPIO setup failed. Are you running as root? sudo python3 voting.py")
    print(e)
    exit()

# -----------------------------
# Tkinter setup
# -----------------------------
root = Tk()
root.title("Electronic Voting Machine")
root.configure(bg="#ffffff")

screen_width = 1024
screen_height = 768
x_offset = 1024
y_offset = 0
root.geometry(f"{screen_width}x{screen_height}+{x_offset}+{y_offset}")
root.attributes('-topmost', True)
root.resizable(False, False)

# -----------------------------
# Global variables
# -----------------------------
last_voter_id = None
last_voter_name = None

# -----------------------------
# Fingerprint screen
# -----------------------------
def show_fingerprint_screen():
    for widget in root.winfo_children():
        widget.destroy()
    Label(root, text="Put your thumb on the fingerprint sensor",
          font=("Arial", 24, "bold"), bg="#ffffff").pack(expand=True)
    root.update()
    wait_for_fingerprint()

# -----------------------------
# Wait for fingerprint match
# -----------------------------
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
                    show_recognized_screen(last_voter_name)
                    return
                elif response == "NO_MATCH":
                    print("Fingerprint not recognized. Try again.")
                    ser.write(b'CHECK\n')
        root.update()

# -----------------------------
# Recognized screen (custom)
# -----------------------------
def show_recognized_screen(voter_name):
    for widget in root.winfo_children():
        widget.destroy()
    Label(root, text=f"Fingerprint recognized!", font=("Arial", 28, "bold"), bg="#ffffff").pack(pady=40)
    Label(root, text=f"Mr. {voter_name}, you can cast your vote now.",
          font=("Arial", 22), bg="#ffffff", fg="#007700").pack(pady=20)
    root.update()
    root.after(2500, show_candidates_screen)  # Wait 2.5 seconds then show candidates

# -----------------------------
# Candidate screen
# -----------------------------
def show_candidates_screen():
    for widget in root.winfo_children():
        widget.destroy()

    Label(root, text="Vote for Your Candidate",
          font=("Arial", 24, "bold"), bg="#ffffff").pack(pady=30)

    frame_candidates = Frame(root, bg="#ffffff")
    frame_candidates.pack(pady=50)

    candidate_labels = {}

    for i, c in enumerate(candidates):
        frame = Frame(frame_candidates, bg="#ffffff")
        frame.grid(row=0, column=i, padx=40)

        try:
            img = Image.open(c["image"])
            img = img.resize((150, 150))
            photo = ImageTk.PhotoImage(img)
            label_img = Label(frame, image=photo, bg="#ffffff")
            label_img.photo = photo
            label_img.pack()
        except Exception as e:
            print(f"Error loading image {c['image']}: {e}")

        label_name = Label(frame, text=c["name"], font=("Arial", 20), bg="#ffffff")
        label_name.pack(pady=10)
        candidate_labels[c["name"]] = label_name

    # -----------------------------
    # Record vote
    # -----------------------------
    def record_vote(candidate_name):
        for name, lbl in candidate_labels.items():
            lbl.config(fg="black")
        candidate_labels[candidate_name].config(fg="red")

        print(f"Vote recorded for {candidate_name}")
        with open("votes.csv", "a") as f:
            f.write(f"{last_voter_id},{last_voter_name},{candidate_name},{datetime.utcnow().isoformat()}\n")

        # Push vote to Firebase
        push_vote(candidate_name, last_voter_id)

        for widget in root.winfo_children():
            widget.destroy()
        Label(root, text="Thank you for voting!", font=("Arial", 24, "bold"), bg="#ffffff").pack(expand=True)

        root.update()
        root.after(3000, show_fingerprint_screen)

    # -----------------------------
    # Check GPIO buttons
    # -----------------------------
    def check_buttons():
        for name, btn in buttons.items():
            if btn.is_pressed:
                record_vote(name)
                return
        root.after(100, check_buttons)

    check_buttons()

# -----------------------------
# Start program
# -----------------------------
show_fingerprint_screen()
root.mainloop()
