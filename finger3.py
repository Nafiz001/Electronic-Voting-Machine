import serial  # Import serial library for communication with Arduino
import time  # Import time for delays and timeouts
import requests  # Import requests for HTTP calls to Firebase

# -----------------------------
# Firebase REST setup
# -----------------------------
FIREBASE_URL = "https://e-vm-f7bdf-default-rtdb.firebaseio.com"  # Base URL for Firebase Realtime Database
VOTERS_NODE = "voters"  # Node for storing voter information
VOTES_NODE = "votes"  # Node for storing vote records

def save_voter(fid, name):  # Function to save a voter's fingerprint ID and name to Firebase
    """Save voter info to Firebase using REST API"""
    data = {"name": name}  # Prepare data as JSON object
    url = f"{FIREBASE_URL}/{VOTERS_NODE}/{fid}.json"  # Construct URL for specific voter ID
    try:
        response = requests.put(url, json=data)  # Send PUT request to Firebase
        if response.status_code == 200:  # Check if request was successful
            print(f"✅ Voter saved to Firebase: ID={fid}, Name={name}")  # Success message
        else:
            print(f"❌ Firebase error: {response.text}")  # Error message with response
    except Exception as e:  # Handle exceptions like network errors
        print(f"❌ Exception saving to Firebase: {e}")  # Exception message

def delete_all_data():  # Function to delete all voters and votes from Firebase
    """Delete all voters and votes from Firebase"""
    try:
        res_voters = requests.delete(f"{FIREBASE_URL}/{VOTERS_NODE}.json")  # Delete voters node
        res_votes = requests.delete(f"{FIREBASE_URL}/{VOTES_NODE}.json")  # Delete votes node

        if res_voters.status_code == 200:  # Check voters deletion success
            print("🗑️  All voters deleted from Firebase.")  # Success message
        else:
            print(f"❌ Error deleting voters: {res_voters.text}")  # Error message

        if res_votes.status_code == 200:  # Check votes deletion success
            print("🗑️  All votes deleted from Firebase.")  # Success message
        else:
            print(f"❌ Error deleting votes: {res_votes.text}")  # Error message

    except Exception as e:  # Handle exceptions
        print(f"❌ Exception deleting Firebase data: {e}")  # Exception message

# -----------------------------
# Serial setup (Arduino + fingerprint)
# -----------------------------
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)  # Open serial connection to Arduino at 9600 baud
time.sleep(2)  # Wait 2 seconds for connection to stabilize

# Wait for sensor ready
while True:  # Loop until sensor is ready
    if ser.in_waiting > 0:  # Check if data is available from Arduino
        msg = ser.readline().decode().strip()  # Read and decode message
        print(msg)  # Print the message
        if "FINGERPRINT_READY" in msg:  # If sensor is ready
            print("✅ Sensor ready!")  # Confirmation message
            break  # Exit loop
        elif "FINGERPRINT_ERROR" in msg:  # If sensor error
            print("❌ Sensor error")  # Error message
            exit()  # Exit program

# -----------------------------
# Main loop
# -----------------------------
while True:  # Infinite loop for user input
    user_input = input(  # Prompt user for input
        "\nPress Enter to scan fingerprint, type ENROLL:<ID>, DELETE_ALL, or 'exit': "
    ).strip()  # Read and strip input

    if user_input.lower() == 'exit':  # If user wants to exit
        print("Exiting...")  # Exit message
        break  # Break loop

    if user_input == "":  # If Enter pressed (scan fingerprint)
        ser.write(b'CHECK\n')  # Send CHECK command to Arduino

    elif user_input.startswith("ENROLL:"):  # If ENROLL command
        id_str = user_input.split(":")[1].strip()  # Extract ID from input
        if not id_str.isdigit():  # Validate ID is digit
            print("❌ Invalid ID")  # Error message
            continue  # Skip to next iteration
        fid = int(id_str)  # Convert to integer

        name = input("Enter voter name for this ID: ").strip()  # Prompt for name
        if not name:  # If name is empty
            print("❌ Name cannot be empty")  # Error message
            continue  # Skip

        ser.write(f'ENROLL:{fid}\n'.encode())  # Send ENROLL command to Arduino

        start_time = time.time()  # Start timeout timer
        while time.time() - start_time < 30:  # Wait up to 30 seconds
            if ser.in_waiting > 0:  # If data from Arduino
                response = ser.readline().decode().strip()  # Read response
                if response:  # If response not empty
                    print(f"Arduino → {response}")  # Print response
                    if "Enrollment successful" in response:  # If success
                        save_voter(fid, name)  # Save to Firebase
                        break  # Exit wait loop
                    elif "Failed" in response:  # If failed
                        print("❌ Enrollment failed")  # Error message
                        break  # Exit wait loop

    elif user_input == "DELETE_ALL":  # If DELETE_ALL command
        ser.write(b'DELETE_ALL\n')  # Send DELETE_ALL to Arduino
        start_time = time.time()  # Start timeout
        while time.time() - start_time < 10:  # Wait up to 10 seconds
            if ser.in_waiting > 0:  # If data from Arduino
                response = ser.readline().decode().strip()  # Read response
                if response:  # If response not empty
                    print(f"Arduino → {response}")  # Print response
                    if response == "ALL_DELETED":  # If success
                        print("✅ Fingerprint templates deleted from sensor.")  # Success message
                        delete_all_data()  # Delete from Firebase
                        break  # Exit wait loop
                    elif response == "DELETE_FAILED":  # If failed
                        print("❌ Delete failed on Arduino.")  # Error message
                        break  # Exit wait loop

    else:  # Unknown command
        print("❌ Unknown command")  # Error message

    # Wait for scan responses
    start_time = time.time()  # Start timeout for scan responses
    while time.time() - start_time < 10:  # Wait up to 10 seconds
        if ser.in_waiting > 0:  # If data from Arduino
            response = ser.readline().decode().strip()  # Read response
            if response:  # If response not empty
                print(f"Arduino → {response}")  # Print response
                if response.startswith("MATCH") or response == "NO_MATCH":  # If scan result
                    break  # Exit wait loop
