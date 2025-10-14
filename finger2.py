import serial
import time
import requests

# -----------------------------
# Firebase REST setup
# -----------------------------
FIREBASE_URL = "https://e-vm-f7bdf-default-rtdb.firebaseio.com/"
VOTERS_NODE = "voters"  # store all enrolled voters here

def save_voter(fid, name):
    """Save voter info to Firebase using REST API"""
    data = {"name": name}
    url = f"{FIREBASE_URL}/{VOTERS_NODE}/{fid}.json"
    try:
        response = requests.put(url, json=data)
        if response.status_code == 200:
            print(f"✅ Voter saved to Firebase: ID={fid}, Name={name}")
        else:
            print(f"❌ Firebase error: {response.text}")
    except Exception as e:
        print(f"❌ Exception saving to Firebase: {e}")

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
# Main loop
# -----------------------------
while True:
    user_input = input(
        "\nPress Enter to scan fingerprint, type ENROLL:<ID>, DELETE_ALL, or 'exit': "
    ).strip()

    if user_input.lower() == 'exit':
        print("Exiting...")
        break

    if user_input == "":
        # Scan fingerprint
        ser.write(b'CHECK\n')

    elif user_input.startswith("ENROLL:"):
        # Extract ID
        id_str = user_input.split(":")[1].strip()
        if not id_str.isdigit():
            print("❌ Invalid ID")
            continue
        fid = int(id_str)

        # Ask for voter name
        name = input("Enter voter name for this ID: ").strip()
        if not name:
            print("❌ Name cannot be empty")
            continue

        # Send enroll command to Arduino
        ser.write(f'ENROLL:{fid}\n'.encode())

        # Wait for Arduino enrollment response
        start_time = time.time()
        while time.time() - start_time < 30:  # 30s timeout
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response:
                    print(f"Arduino → {response}")
                    if "Enrollment successful" in response:
                        # Save ID and name to Firebase via REST
                        save_voter(fid, name)
                        break
                    elif "Failed" in response:
                        print("❌ Enrollment failed")
                        break

    elif user_input == "DELETE_ALL":
        ser.write(b'DELETE_ALL\n')
        # Wait for Arduino response
        start_time = time.time()
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response:
                    print(f"Arduino → {response}")
                    if response in ["ALL_DELETED", "DELETE_FAILED"]:
                        break

    else:
        print("❌ Unknown command")

    # -----------------------------
    # Wait for CHECK (scan) response
    # -----------------------------
    start_time = time.time()
    while time.time() - start_time < 10:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response:
                print(f"Arduino → {response}")
                if response.startswith("MATCH") or response == "NO_MATCH":
                    break
