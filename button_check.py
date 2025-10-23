#!/usr/bin/env python3
"""
Push Button Check Script for EVM
This script tests the GPIO push buttons connected to the Raspberry Pi.
It detects button presses and prints messages to the console.
Run with: sudo python3 button_check.py
"""

from gpiozero import Button
import time
import signal
import sys

# GPIO pins for candidates (same as in voting scripts)
BUTTON_PINS = {
    "Alice": 17,
    "Bob": 27,
    "Charlie": 22
}

# Setup buttons with pull-up resistors and bounce time
buttons = {}
for name, pin in BUTTON_PINS.items():
    try:
        buttons[name] = Button(pin, pull_up=True, bounce_time=0.2)
        print(f"✅ Button {name} setup on GPIO {pin}")
    except Exception as e:
        print(f"❌ Failed to setup button {name} on GPIO {pin}: {e}")
        sys.exit(1)

# Signal handler for clean exit
def signal_handler(sig, frame):
    print("\nExiting button check script...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Button press handlers
def button_pressed(name):
    print(f"🔘 Button '{name}' pressed! (GPIO {BUTTON_PINS[name]})")

# Assign handlers
for name, btn in buttons.items():
    btn.when_pressed = lambda n=name: button_pressed(n)

print("\n" + "="*50)
print("PUSH BUTTON CHECK SCRIPT")
print("="*50)
print("Press any candidate button to test.")
print("Expected buttons: Alice (GPIO 17), Bob (GPIO 27), Charlie (GPIO 22)")
print("Press Ctrl+C to exit.")
print("="*50 + "\n")

# Keep script running
while True:
    time.sleep(0.1)