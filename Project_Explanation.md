# Electronic Voting Machine (EVM) with Fingerprint Authentication - Detailed Explanation

## Project Overview
This project implements an Electronic Voting Machine (EVM) that uses fingerprint authentication to verify voters, prevent double voting, and record votes in a cloud database. It combines embedded hardware (Arduino + fingerprint sensor) with a Raspberry Pi for orchestration, GUI, and networking, plus a web dashboard for real-time results visualization. The system is designed for small-scale elections, demonstrating IoT principles through cloud connectivity and remote monitoring.

## Hardware Components and Connections

### Components List
- **Arduino Uno/Nano**: Microcontroller for fingerprint sensor control.
- **FPM10A Fingerprint Reader**: Optical sensor for capturing and matching fingerprints.
- **Raspberry Pi (with Wi-Fi/Ethernet)**: Central controller for GUI, GPIO, and cloud communication.
- **5-inch HDMI Display**: Touchscreen interface for voters.
- **Push Buttons (3x)**: Physical inputs for candidate selection.
- **Buzzer**: Audible feedback for user interactions.
- **Breadboard and Jumper Wires**: For prototyping connections.
- **Power Supplies**: 5V for Arduino/sensor, stable power for Raspberry Pi.

### Wiring Diagram and Pin Connections

#### Fingerprint Sensor (FPM10A) to Arduino
- **Sensor TX** → Arduino Pin 2 (SoftwareSerial RX)
- **Sensor RX** → Arduino Pin 3 (SoftwareSerial TX)
- **Sensor VCC** → Arduino 5V pin
- **Sensor GND** → Arduino GND pin
- **Sensor EN** → Arduino 5V pin (if applicable, enable pin)

The sensor communicates via UART at 57600 baud using SoftwareSerial library.

#### Arduino to Raspberry Pi
- **Arduino USB** → Raspberry Pi USB port
- Serial communication appears as `/dev/ttyACM0` on Raspberry Pi at 9600 baud.

#### Raspberry Pi GPIO Connections
- **Button 1 (Alice)**: GPIO 17 → Button switch (one side), other side to GND
- **Button 2 (Bob)**: GPIO 27 → Button switch (one side), other side to GND
- **Button 3 (Charlie)**: GPIO 22 → Button switch (one side), other side to GND
- **Buzzer**: GPIO 18 → Buzzer positive terminal, negative to GND
- All buttons use pull-up resistors internally via gpiozero library.

#### Display Connection
- **HDMI Cable**: Raspberry Pi HDMI port → 5-inch HDMI Display
- **Touch USB (if touch-enabled)**: Display USB → Raspberry Pi USB port

#### Power Connections
- Arduino: Powered via USB from Raspberry Pi or external 5V supply.
- Raspberry Pi: 5V micro-USB or GPIO pins.
- Fingerprint Sensor: 5V from Arduino.
- Buzzer: 3.3V/5V from Raspberry Pi GPIO (with resistor if needed).

### ASCII Wiring Diagram
```
[FPM10A Sensor]
├── TX  → Arduino D2 (RX)
├── RX  → Arduino D3 (TX)
├── VCC → Arduino 5V
├── GND → Arduino GND
└── EN  → Arduino 5V

[Arduino Uno]
├── USB → Raspberry Pi USB (/dev/ttyACM0)
├── 5V  → Sensor VCC
└── GND → Sensor GND

[Raspberry Pi]
├── GPIO17 → Button1 (Alice) → GND
├── GPIO27 → Button2 (Bob)   → GND
├── GPIO22 → Button3 (Charlie)→ GND
├── GPIO18 → Buzzer (+)     → GND
├── HDMI   → 5" Display
└── USB    → Arduino USB
```

## Software Structure and Architecture

### System Architecture
The system follows a layered architecture:
1. **Hardware Layer**: Arduino + sensor for biometric input.
2. **Control Layer**: Raspberry Pi for logic, UI, and data persistence.
3. **Cloud Layer**: Firebase Realtime Database for storage and synchronization.
4. **Presentation Layer**: React web app for dashboards.

### Data Flow
1. **Enrollment**: Admin uses `finger3.py` to enroll fingerprints → Arduino captures → Raspberry Pi saves to Firebase.
2. **Voting**: Voter places finger → Arduino matches → Raspberry Pi checks eligibility → GUI shows candidates → Button press records vote → Saves to Firebase and local CSV.
3. **Visualization**: Website fetches from Firebase → Displays live stats.

### IoT Working Principle
This project exemplifies IoT through:
- **Connectivity**: Raspberry Pi connects to internet via Wi-Fi/Ethernet to access Firebase cloud database.
- **Data Exchange**: REST API calls (GET/POST/PUT/DELETE) send/receive JSON data between edge device (Pi) and cloud.
- **Real-time Synchronization**: Firebase's real-time updates allow the web dashboard to reflect live voting data without manual refreshes.
- **Remote Monitoring**: Admins/operators can view results from any internet-connected device via the website.
- **Edge Processing**: Fingerprint matching and UI logic happen locally on Pi, reducing latency; only results are uploaded.
- **Security Considerations**: Public Firebase URL allows read access for dashboards, but write operations should be restricted in production.

## Code Files and Detailed Explanations

### 1. `embedded.ino` (Arduino Firmware)
This Arduino sketch controls the FPM10A sensor, handling enrollment and matching via serial commands from Raspberry Pi.

**Key Functions**:
- `setup()`: Initializes serial ports and sensor.
- `loop()`: Listens for commands ("CHECK" or "ENROLL:<id>").
- `getFingerprintID()`: Captures image, converts to template, searches for match.
- `enrollFingerprint(id)`: Guides two-step capture, creates model, stores in sensor.

### 2. `finger3.py` (Raspberry Pi Enrollment/Admin Tool)
Console-based script for enrolling voters and managing data.

**Key Sections**:
- Firebase setup with REST endpoints.
- Serial communication with Arduino.
- Main loop for user commands: enroll, delete all, check fingerprint.

### 3. `voting5.py` (Raspberry Pi Voting GUI)
Tkinter-based GUI for the voting process.

**Key Sections**:
- Firebase functions for voting and checks.
- GPIO setup for buttons and buzzer.
- Screen functions: fingerprint, recognized, candidates, already voted.
- Vote recording with local CSV and cloud push.

### 4. `votingMachine/voting-website/` (React Web Dashboard)
- `src/services/firebase.js`: REST service for fetching voters/votes and computing stats.
- Pages: Dashboard, VoterList, VoteCount, VoteStatistics – display live data from Firebase.

## How IoT Works in This Project
- **Sensors and Actuators**: Fingerprint sensor (input), buzzer/buttons (output).
- **Edge Device**: Raspberry Pi processes data locally, reduces cloud load.
- **Cloud Platform**: Firebase provides scalable, real-time database.
- **Communication Protocols**: Serial (Arduino-Pi), HTTP REST (Pi-Firebase), WebSockets implicit in Firebase for real-time.
- **Data Pipeline**: Local capture → Processing → Cloud storage → Remote visualization.
- **Benefits**: Enables remote access, scalability, and analytics without physical presence.

## Setup and Running Instructions
1. Assemble hardware as per wiring diagram.
2. Upload `embedded.ino` to Arduino.
3. Install Python libraries on Pi: `pip install pyserial requests gpiozero pillow`.
4. Run `finger3.py` for enrollment.
5. Run `voting5.py` for voting.
6. Deploy website: `npm install && npm run dev` in `votingMachine/voting-website/`.

## Troubleshooting
- Serial issues: Check `/dev/ttyACM0` permissions (run with sudo if needed).
- GPIO errors: Ensure Pi is configured for GPIO access.
- Firebase errors: Verify internet and database rules.

## Future Enhancements
- Add authentication to Firebase writes.
- Implement offline mode with local caching.
- Enhance UI with touch gestures and accessibility features.