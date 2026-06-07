# 🗳️ Electronic Voting Machine (EVM) with Fingerprint Authentication & IoT

A biometric Electronic Voting Machine built on a **Raspberry Pi**, an **Arduino + FPM10A fingerprint sensor**, a **5-inch HDMI touch display**, and **physical push buttons**. Votes are authenticated by fingerprint, recorded both locally and to a **Firebase Realtime Database (cloud / IoT)**, and streamed live to a **React web dashboard**.

🔗 **Live dashboard:** https://evm-rho.vercel.app/

---

## 🎥 Demo

<video src="https://res.cloudinary.com/dvvbtopri/video/upload/v1780869198/evm_video_tg23uf.mp4" controls width="600"></video>

> If the player doesn't load, [watch the demo video here](https://res.cloudinary.com/dvvbtopri/video/upload/v1780869198/evm_video_tg23uf.mp4).

---

## ✨ Features

- **Biometric authentication** — each voter is identified by fingerprint via the FPM10A sensor, preventing impersonation.
- **Double-voting prevention** — the system checks Firebase before allowing a vote; repeat voters get an on-screen warning and an audible double-buzz, and the attempt is logged.
- **Physical voting interface** — a touchscreen GUI shows candidates while three push buttons map directly to the candidates for tactile selection.
- **IoT / cloud sync** — votes, voters, and vote attempts are pushed to Firebase over HTTP REST in real time.
- **Live web dashboard** — a React app reads from Firebase to display voters, candidates, live vote counts, and statistics from any internet-connected device.
- **Local backup** — every vote is also appended to a local `votes.csv` file on the Pi.

---

## 🧩 Hardware

| Component | Role |
|-----------|------|
| Raspberry Pi (Wi-Fi/Ethernet) | Central controller — GUI, GPIO, cloud sync |
| Arduino Uno/Nano | Drives the fingerprint sensor |
| FPM10A Fingerprint Sensor | Captures & matches fingerprints (UART @ 57600 baud) |
| 5-inch HDMI Display | Voter-facing touchscreen UI |
| 3× Push Buttons | Candidate selection (GPIO 17 / 27 / 22) |
| Buzzer | Audible feedback (GPIO 18) |
| Breadboard, jumper wires, 5V supplies | Prototyping & power |

### Wiring summary

```
[FPM10A Sensor]                 [Raspberry Pi]
  TX  → Arduino D2 (RX)           GPIO17 → Button: Alice    → GND
  RX  → Arduino D3 (TX)           GPIO27 → Button: Bob      → GND
  VCC → Arduino 5V                GPIO22 → Button: Charlie  → GND
  GND → Arduino GND               GPIO18 → Buzzer (+)       → GND
                                  HDMI   → 5" Display
[Arduino Uno]                     USB    → Arduino (/dev/ttyACM0 @ 9600)
  USB → Raspberry Pi (/dev/ttyACM0)
```

A full pin map and an editable circuit diagram are in [Project_Explanation.md](Project_Explanation.md) and [circuit_diagram.drawio](circuit_diagram.drawio).

---

## 🏗️ Architecture

```
┌────────────────┐   serial    ┌──────────────────┐   HTTP REST   ┌──────────────┐   HTTP   ┌──────────────────┐
│ Arduino + FPM10A│ ──────────▶ │   Raspberry Pi    │ ────────────▶ │   Firebase   │ ◀─────── │  React Dashboard  │
│ (fingerprint)   │  9600 baud  │  Tkinter GUI +    │   (votes,     │  Realtime DB │  (live)  │   (Vercel)        │
└────────────────┘             │  GPIO + buzzer    │   voters)     └──────────────┘          └──────────────────┘
                               └──────────────────┘
                                        │ append
                                        ▼
                                   votes.csv (local backup)
```

1. **Hardware layer** — Arduino + sensor capture/match fingerprints.
2. **Control layer** — Raspberry Pi runs the GUI, reads buttons, drives the buzzer, and talks to the cloud.
3. **Cloud / IoT layer** — Firebase Realtime Database stores voters and votes and synchronizes in real time.
4. **Presentation layer** — React web app visualizes live results.

---

## 📁 Project structure

```
EVM/
├── embedded.ino             # Arduino firmware: ENROLL / CHECK commands for the FPM10A sensor
├── finger3.py               # Pi admin tool: enroll voters, delete data, test scans
├── voting5.py               # Pi voting app: Tkinter GUI, GPIO buttons, buzzer, vote recording
├── voting6.py, voting*.py   # Earlier/alternate iterations of the voting app
├── display.py / finger*.py  # Hardware test & utility scripts
├── button_check.py          # GPIO button test
├── votes.csv                # Local vote log
├── candidate_*.jpg          # Candidate photos shown in the GUI
├── circuit_diagram.drawio   # Editable wiring diagram
├── Project_Explanation.md   # Detailed hardware + software writeup
├── Project_Report_EVM.txt   # Full project report
└── votingMachine/
    └── voting-website/      # React + Vite dashboard (deployed to Vercel)
        └── src/
            ├── pages/       # Dashboard, VoterList, Candidates, VoteCount, VoteStatistics
            ├── components/  # Navigation
            └── services/    # firebase.js — REST client + stats computation
```

---

## 🔧 Software

### Embedded firmware — [embedded.ino](embedded.ino)
Controls the FPM10A over `SoftwareSerial` and responds to commands from the Pi:
- `CHECK` → scans a finger and replies `MATCH:<id>` or `NO_MATCH`.
- `ENROLL:<id>` → guides a two-step capture and stores the fingerprint model at the given ID.

### Enrollment / admin tool — [finger3.py](finger3.py)
Console tool on the Pi for:
- Enrolling voters (`ENROLL:<ID>` → captures fingerprint, saves name to Firebase).
- Deleting all voters/votes (`DELETE_ALL`).
- Test scans (Enter to scan).

### Voting application — [voting5.py](voting5.py)
The main Tkinter GUI run on the 5-inch display:
- Waits for a fingerprint, recognizes the voter, and checks Firebase for prior votes.
- Shows candidate cards; a push button records the selected vote.
- Writes to `votes.csv` and pushes the vote to Firebase.
- Buzzes twice and warns on repeat-vote attempts.

### Web dashboard — [votingMachine/voting-website/](votingMachine/voting-website/)
React 19 + Vite + React Router, charts via Recharts, icons via lucide-react. `src/services/firebase.js` fetches voters/votes from Firebase over REST and computes live statistics. Pages: **Dashboard**, **Voters**, **Candidates**, **Vote Count**, **Statistics**.

---

## 🚀 Getting started

### 1. Flash the Arduino
Upload [embedded.ino](embedded.ino) to the Arduino (requires the **Adafruit Fingerprint Sensor** library).

### 2. Raspberry Pi setup
```bash
pip install pyserial requests gpiozero pillow
```
- Enroll voters: `python3 finger3.py`
- Start voting: `python3 voting5.py`  *(use `sudo` if GPIO access fails)*

### 3. Web dashboard
```bash
cd votingMachine/voting-website
npm install
npm run dev      # local dev server
npm run build    # production build (deployed to Vercel)
```

---

## 🌐 IoT in this project

- **Connectivity** — the Pi reaches Firebase over Wi-Fi/Ethernet.
- **Data exchange** — JSON over HTTP REST (`GET`/`POST`/`PUT`/`DELETE`).
- **Real-time sync** — Firebase propagates updates so the dashboard reflects live votes without manual refresh.
- **Edge processing** — fingerprint matching and UI run locally on the Pi; only results are uploaded.
- **Remote monitoring** — results are viewable from anywhere via the hosted dashboard.

> ⚠️ **Note:** the Firebase database is publicly readable for the demo dashboard. For real deployments, lock down write access with authentication and database rules.

---

## 🔮 Future enhancements

- Authenticated/secured Firebase writes.
- Offline mode with local caching and later sync.
- Accessibility and touch-gesture improvements in the GUI.

---

*For an in-depth walkthrough of the wiring, data flow, and IoT principles, see [Project_Explanation.md](Project_Explanation.md) and [Project_Report_EVM.txt](Project_Report_EVM.txt).*
