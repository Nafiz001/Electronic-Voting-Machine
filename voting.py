from tkinter import *
from PIL import Image, ImageTk
from gpiozero import Button
import serial
import time

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
    {"name": "Alice", "image": "candidate1.jpg", "gpio": 17},
    {"name": "Bob", "image": "candidate2.jpg", "gpio": 27},
    {"name": "Charlie", "image": "candidate3.jpg", "gpio": 22}
]

# Create GPIO buttons
buttons = {c["name"]: Button(c["gpio"]) for c in candidates}

# -----------------------------
# Tkinter setup
# -----------------------------
root = Tk()
root.title("Electronic Voting Machine")
root.configure(bg="#ffffff")

# 5-inch display position
screen_width = 1024
screen_height = 768
x_offset = 1024
y_offset = 0
root.geometry(f"{screen_width}x{screen_height}+{x_offset}+{y_offset}")
root.attributes('-topmost', True)
root.resizable(False, False)

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
    ser.write(b'CHECK\n')
    while True:
        # Read Arduino responses
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response:
                print(f"Arduino → {response}")
                if response.startswith("MATCH"):
                    voter_id = response.split(":")[1]
                    print(f"Fingerprint matched: {voter_id}")
                    show_candidates_screen()
                    return
                elif response == "NO_MATCH":
                    print("Fingerprint not recognized. Try again.")
                    ser.write(b'CHECK\n')
        root.update()

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
        # Highlight selection
        for name, lbl in candidate_labels.items():
            lbl.config(fg="black")
        candidate_labels[candidate_name].config(fg="red")

        print(f"Vote recorded for {candidate_name}")
        with open("votes.csv", "a") as f:
            f.write(f"{candidate_name}\n")

        # Show thank you message
        for widget in root.winfo_children():
            widget.destroy()
        Label(root, text="Thank you for voting!", font=("Arial", 24, "bold"), bg="#ffffff").pack(expand=True)

        root.update()
        root.after(3000, show_fingerprint_screen)  # back to fingerprint screen

    # -----------------------------
    # Check buttons
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
