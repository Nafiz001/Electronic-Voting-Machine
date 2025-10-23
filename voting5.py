#!/usr/bin/env python3  # Shebang for running as executable
from tkinter import *  # Import Tkinter for GUI
from tkinter import ttk  # Import ttk for styled widgets
from PIL import Image, ImageTk  # Import PIL for image handling
from gpiozero import Button, Buzzer  # Import gpiozero for GPIO control
import serial  # Import serial for Arduino communication
import time  # Import time for delays
import requests  # Import requests for Firebase API
from datetime import datetime  # Import datetime for timestamps

# -----------------------------
# Firebase setup
# -----------------------------
DB_URL = "https://e-vm-f7bdf-default-rtdb.firebaseio.com"  # Firebase database URL

def push_vote(candidate_name, voter_id=None):  # Function to push vote to Firebase
    payload = {  # Prepare vote data
        "candidate": candidate_name,  # Candidate name
        "voter_id": voter_id,  # Voter ID
        "timestamp": datetime.utcnow().isoformat()  # UTC timestamp
    }
    try:
        response = requests.post(f"{DB_URL}/votes.json", json=payload)  # POST to votes endpoint
        if response.status_code == 200:  # Check success
            print(f"✅ Vote for {candidate_name} pushed to Firebase")  # Success message
        else:
            print(f"❌ Failed to push vote: {response.text}")  # Error message
    except Exception as e:  # Handle exceptions
        print(f"❌ Exception while pushing vote: {e}")  # Exception message

def get_voter_name(voter_id):  # Function to get voter name from Firebase
    try:
        res = requests.get(f"{DB_URL}/voters/{voter_id}.json")  # GET voter data
        if res.status_code == 200 and res.json():  # Check success and data
            return res.json().get("name", "Unknown Voter")  # Return name or default
        else:
            return "Unknown Voter"  # Default if not found
    except Exception as e:  # Handle exceptions
        print(f"❌ Failed to fetch voter name: {e}")  # Exception message
        return "Unknown Voter"  # Default

def has_already_voted(voter_id):  # Function to check if voter already voted
    """Check if voter already cast a vote."""
    try:
        res = requests.get(f"{DB_URL}/votes.json")  # GET all votes
        if res.status_code == 200 and res.json():  # Check success and data
            for key, val in res.json().items():  # Iterate through votes
                if val.get("voter_id") == str(voter_id):  # Check if voter_id matches
                    return True  # Already voted
        return False  # Not voted
    except Exception as e:  # Handle exceptions
        print(f"❌ Error checking previous votes: {e}")  # Exception message
        return False  # Assume not voted

# -----------------------------
# Serial setup
# -----------------------------
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)  # Open serial to Arduino
time.sleep(2)  # Wait for connection

while True:  # Wait for sensor ready
    if ser.in_waiting > 0:  # Check for data
        msg = ser.readline().decode().strip()  # Read message
        print(msg)  # Print message
        if "FINGERPRINT_READY" in msg:  # If ready
            print("✅ Sensor ready!")  # Confirmation
            break  # Exit loop
        elif "FINGERPRINT_ERROR" in msg:  # If error
            print("❌ Sensor error")  # Error
            exit()  # Exit

# -----------------------------
# Candidate setup
# -----------------------------
candidates = [  # List of candidates with details
    {"name": "Alice", "image": "candidate1.jpg", "gpio": 17},  # Alice details
    {"name": "Bob", "image": "candidate2.jpg", "gpio": 27},    # Bob details
    {"name": "Charlie", "image": "candidate3.jpg", "gpio": 22} # Charlie details
]

# -----------------------------
# GPIO Buttons and Buzzer
# -----------------------------
try:
    buttons = {c["name"]: Button(c["gpio"], pull_up=True, bounce_time=0.2) for c in candidates}  # Setup buttons
    buzzer = Buzzer(18, active_high=True, initial_value=False)  # Setup buzzer on GPIO 18
except Exception as e:  # Handle GPIO errors
    print("❌ GPIO setup failed. Run with sudo")  # Error message
    print(e)  # Print exception
    exit()  # Exit

# -----------------------------
# Tkinter setup
# -----------------------------
root = Tk()  # Create main window
root.title("Electronic Voting Machine")  # Set title
root.configure(bg="#F4F7FA")  # Set background color

screen_width = 800  # Screen width
screen_height = 500  # Screen height
root.geometry(f"{screen_width}x{screen_height}+0+0")  # Set geometry
root.resizable(False, False)  # Disable resizing

style = ttk.Style()  # Create style object
style.configure("TLabel", background="#F4F7FA", foreground="#222", font=("Arial", 20))  # Configure labels
style.configure("Title.TLabel", background="#F4F7FA", foreground="#0056b3", font=("Arial", 28, "bold"))  # Title style
style.configure("Message.TLabel", background="#F4F7FA", foreground="#007700", font=("Arial", 22, "bold"))  # Message style

last_voter_id = None  # Global variable for last voter ID
last_voter_name = None  # Global variable for last voter name

# -----------------------------
# Screens
# -----------------------------
def show_fingerprint_screen():  # Function to show fingerprint screen
    for w in root.winfo_children():  # Clear previous widgets
        w.destroy()
    frame = Frame(root, bg="#F4F7FA")  # Create frame
    frame.pack(expand=True, fill=BOTH)  # Pack frame
    ttk.Label(frame, text="Place your finger on the sensor", style="Title.TLabel").pack(pady=60)  # Title label
    ttk.Label(frame, text="Waiting for fingerprint...", style="TLabel").pack(pady=20)  # Subtitle
    root.update()  # Update GUI
    wait_for_fingerprint()  # Call wait function

def buzz_twice():  # Function to buzz twice for repeat voter
    """Buzz the buzzer twice for repeat voter."""
    for _ in range(2):  # Loop twice
        buzzer.on()  # Turn buzzer on
        time.sleep(0.3)  # Wait 0.3s
        buzzer.off()  # Turn off
        time.sleep(0.2)  # Wait 0.2s

def show_already_voted_screen():  # Function to show already voted screen
    for w in root.winfo_children():  # Clear widgets
        w.destroy()
    frame = Frame(root, bg="#FFF8E1")  # Create frame with warning color
    frame.pack(expand=True, fill=BOTH)  # Pack
    ttk.Label(frame, text="⚠️ You have already voted!", style="Title.TLabel").pack(pady=50)  # Warning title
    ttk.Label(frame, text="Multiple voting is not allowed.", style="Message.TLabel").pack(pady=20)  # Message

    # 🔊 Buzz twice
    buzz_twice()  # Call buzz function

    root.after(3000, show_fingerprint_screen)  # After 3s, go back to fingerprint screen

# -----------------------------
# Fingerprint / voter check
# -----------------------------
def wait_for_fingerprint():  # Function to wait for fingerprint
    global last_voter_id, last_voter_name  # Use global variables
    ser.write(b'CHECK\n')  # Send CHECK command
    while True:  # Loop until match or no match
        if ser.in_waiting > 0:  # If data available
            response = ser.readline().decode().strip()  # Read response
            if response:  # If not empty
                print(f"Arduino → {response}")  # Print response
                if response.startswith("MATCH"):  # If match
                    last_voter_id = response.split(":")[1]  # Extract ID
                    last_voter_name = get_voter_name(last_voter_id)  # Get name
                    print(f"Fingerprint matched: {last_voter_id} ({last_voter_name})")  # Log
                    if has_already_voted(last_voter_id):  # Check if already voted
                        print("❌ Already voted")  # Log
                        show_already_voted_screen()  # Show warning
                        return  # Exit
                    show_recognized_screen(last_voter_name)  # Show recognized
                    return  # Exit
                elif response == "NO_MATCH":  # If no match
                    print("Fingerprint not recognized. Try again.")  # Log
                    ser.write(b'CHECK\n')  # Retry CHECK
        root.update()  # Update GUI

def show_recognized_screen(voter_name):  # Function to show recognized screen
    for w in root.winfo_children():  # Clear widgets
        w.destroy()
    frame = Frame(root, bg="#E8F5E9")  # Success color frame
    frame.pack(expand=True, fill=BOTH)  # Pack
    ttk.Label(frame, text="Fingerprint recognized!", style="Title.TLabel").pack(pady=50)  # Title
    ttk.Label(frame, text=f"Mr. {voter_name}, you can now cast your vote.", style="Message.TLabel").pack(pady=20)  # Message
    root.after(2500, show_candidates_screen)  # After 2.5s, show candidates

# -----------------------------
# Candidate screen
# -----------------------------
def show_candidates_screen():  # Function to show candidates
    for w in root.winfo_children():  # Clear widgets
        w.destroy()
    ttk.Label(root, text="Vote for Your Candidate", style="Title.TLabel").pack(pady=20)  # Title
    frame = Frame(root, bg="#F4F7FA")  # Frame for candidates
    frame.pack(pady=20)  # Pack
    candidate_labels = {}  # Dict for labels

    for i, c in enumerate(candidates):  # Loop through candidates
        card = Frame(frame, bg="#FFFFFF", relief=RAISED, borderwidth=2)  # Card frame
        card.grid(row=0, column=i, padx=30, ipadx=10, ipady=10)  # Grid layout
        try:
            img = Image.open(c["image"])  # Open image
            img = img.resize((130, 130))  # Resize
            photo = ImageTk.PhotoImage(img)  # Convert to Tk image
            label_img = Label(card, image=photo, bg="#FFFFFF")  # Image label
            label_img.photo = photo  # Keep reference
            label_img.pack(pady=5)  # Pack
        except Exception as e:  # Handle image error
            print(f"Error loading {c['image']}: {e}")  # Log error
        lbl_name = Label(card, text=c["name"], bg="#FFFFFF", fg="#000", font=("Arial", 18, "bold"))  # Name label
        lbl_name.pack(pady=10)  # Pack
        candidate_labels[c["name"]] = lbl_name  # Store in dict

    def record_vote(candidate_name):  # Function to record vote
        for name, lbl in candidate_labels.items():  # Reset colors
            lbl.config(fg="#000")
        candidate_labels[candidate_name].config(fg="#E53935")  # Highlight selected
        print(f"Vote recorded for {candidate_name}")  # Log
        with open("votes.csv", "a") as f:  # Append to CSV
            f.write(f"{last_voter_id},{last_voter_name},{candidate_name},{datetime.utcnow().isoformat()}\n")
        push_vote(candidate_name, last_voter_id)  # Push to Firebase
        for w in root.winfo_children():  # Clear widgets
            w.destroy()
        ttk.Label(root, text="✅ Thank you for voting!", style="Title.TLabel").pack(expand=True)  # Thank you
        root.after(3000, show_fingerprint_screen)  # After 3s, back to start

    def check_buttons():  # Function to check button presses
        for name, btn in buttons.items():  # Loop through buttons
            if btn.is_pressed:  # If pressed
                record_vote(name)  # Record vote
                return  # Exit
        root.after(100, check_buttons)  # Check again after 100ms

    check_buttons()  # Start checking

# -----------------------------
# Start program
# -----------------------------
show_fingerprint_screen()  # Show initial screen
root.mainloop()  # Start GUI loop

