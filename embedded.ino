#include <Adafruit_Fingerprint.h>
#include <SoftwareSerial.h>

SoftwareSerial mySerial(2, 3); // RX, TX for fingerprint sensor
Adafruit_Fingerprint finger(&mySerial);

void setup() {
  Serial.begin(9600);       // Communication with Raspberry Pi
  finger.begin(57600);      // FPM10A baud rate
  delay(100);

  if (finger.verifyPassword()) {
    Serial.println("FINGERPRINT_READY");
  } else {
    Serial.println("FINGERPRINT_ERROR");
    while (1);
  }
}

void loop() {
  // Wait for commands from Raspberry Pi
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "CHECK") {
      int result = getFingerprintID();
      if (result >= 0) {
        Serial.print("MATCH:");
        Serial.println(result);
      } else {
        Serial.println("NO_MATCH");
      }
    }
    else if (command.startsWith("ENROLL:")) {
      int id = command.substring(7).toInt();
      if (id <= 0) {
        Serial.println("ERROR: Invalid ID");
      } else {
        enrollFingerprint(id);
      }
    }
  }
}

// Function to get fingerprint ID
int getFingerprintID() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) return -1;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) return -1;

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK) return -1;

  return finger.fingerID;
}

// Function to enroll a fingerprint
void enrollFingerprint(int id) {
  Serial.print("Place finger for enrollment ID ");
  Serial.println(id);

  // Step 1: Capture image
  int p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image taken");
        break;
      case FINGERPRINT_NOFINGER:
        // Keep waiting for finger
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error, try again");
        break;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error, try again");
        break;
      default:
        Serial.println("Unknown error");
        break;
    }
  }

  // Step 2: Convert image to template 1
  p = finger.image2Tz(1);
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to convert image to template 1");
    return;
  }

  Serial.println("Remove finger");
  delay(2000);

  // Step 3: Capture second image
  p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Second image taken");
        break;
      case FINGERPRINT_NOFINGER:
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error, try again");
        break;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error, try again");
        break;
      default:
        Serial.println("Unknown error");
        break;
    }
  }

  // Step 4: Convert image to template 2
  p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to convert image to template 2");
    return;
  }

  // Step 5: Create model
  p = finger.createModel();
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to create fingerprint model");
    return;
  }

  // Step 6: Store model in ID
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.print("Enrollment successful! Stored at ID ");
    Serial.println(id);
  } else {
    Serial.println("Failed to store fingerprint model");
  }
}