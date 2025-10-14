import serial
import time

# Connect to Arduino serial
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
time.sleep(2)

# Wait for Arduino startup message
while True:
    if ser.in_waiting > 0:
        msg = ser.readline().decode().strip()
        print(msg)
        if "FINGERPRINT_READY" in msg:
            print("✅ Sensor ready!")
            break
        elif "FINGERPRINT_ERROR" in msg:
            print("❌ Sensor error")
            break

# Main loop
while True:
    user_input = input("\nPress Enter to scan fingerprint, or type ENROLL:<ID>, or 'exit': ").strip()

    if user_input.lower() == 'exit':
        break

    if user_input == "":
        # If Enter is pressed with no input, send CHECK
        ser.write(b'CHECK\n')
    else:
        # Send whatever command user typed (ENROLL:<ID>)
        ser.write((user_input + '\n').encode())

    # Wait for Arduino response
    start_time = time.time()
    while time.time() - start_time < 10:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response:
                print(f"Arduino → {response}")
                if response.startswith("MATCH") or response == "NO_MATCH" or "Enrollment successful" in response:
                    break
