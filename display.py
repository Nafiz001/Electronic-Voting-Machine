from tkinter import *
from PIL import Image, ImageTk
from gpiozero import Button

# -----------------------------
# Step 1: Create main window
# -----------------------------
root = Tk()
root.title("Electronic Voting Machine")
root.configure(bg="#ffffff")

# Move window to 5-inch display (extended screen)
screen_width = 1024
screen_height = 768
x_offset = 1024  # offset from primary display
y_offset = 0
root.geometry(f"{screen_width}x{screen_height}+{x_offset}+{y_offset}")
root.attributes('-topmost', True)
root.resizable(False, False)

# -----------------------------
# Step 2: Header
# -----------------------------
Label(root, text="Vote for Your Candidate", font=("Arial", 24, "bold"), bg="#ffffff").pack(pady=30)

# -----------------------------
# Step 3: Candidates and images
# -----------------------------
candidates = [
    {"name": "Alice", "image": "candidate1.jpg"},
    {"name": "Bob", "image": "candidate2.jpg"},
    {"name": "Charlie", "image": "candidate3.jpg"}
]

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
# Step 4: Setup push buttons (BCM GPIO)
# -----------------------------
button_alice = Button(17)    # Alice
button_bob = Button(27)      # Bob
button_charlie = Button(22)  # Charlie

buttons = {
    "Alice": button_alice,
    "Bob": button_bob,
    "Charlie": button_charlie
}

# -----------------------------
# Step 5: Vote recording
# -----------------------------
def record_vote(candidate_name):
    # Highlight selected candidate
    for name, lbl in candidate_labels.items():
        lbl.config(fg="black")
    candidate_labels[candidate_name].config(fg="red")

    print(f"Vote recorded for {candidate_name}")

    # Save vote to file
    with open("votes.csv", "a") as f:
        f.write(f"{candidate_name}\n")

    # Show thank-you message
    label_thank = Label(root, text="Thank you for voting!", font=("Arial", 24), bg="#ffffff")
    label_thank.pack(pady=20)

    # Close GUI after 3 seconds
    root.after(3000, root.destroy)

# -----------------------------
# Step 6: Check button presses
# -----------------------------
def check_buttons():
    for name, btn in buttons.items():
        if btn.is_pressed:
            record_vote(name)
            return
    root.after(100, check_buttons)  # check again after 100ms

check_buttons()  # start checking

# -----------------------------
# Step 7: Run GUI
# -----------------------------
root.mainloop()
