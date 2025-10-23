#include <Adafruit_Fingerprint.h>  // Include library for FPM10A fingerprint sensor
#include <SoftwareSerial.h>  // Include library for software serial communication

SoftwareSerial mySerial(2, 3); // RX, TX for fingerprint sensor - Pin 2 is RX (receive from sensor), Pin 3 is TX (transmit to sensor)
Adafruit_Fingerprint finger(&mySerial);  // Create fingerprint sensor object using software serial

void setup() {
  Serial.begin(9600);       // Initialize hardware serial at 9600 baud for communication with Raspberry Pi
  finger.begin(57600);      // Initialize fingerprint sensor at 57600 baud
  delay(100);               // Wait 100ms for sensor to initialize

  if (finger.verifyPassword()) {  // Check if sensor is responding correctly
    Serial.println("FINGERPRINT_READY");  // Send ready signal to Raspberry Pi
  } else {
    Serial.println("FINGERPRINT_ERROR");  // Send error signal if sensor fails
    while (1);  // Halt execution on error
  }
}

void loop() {
  // Wait for commands from Raspberry Pi
  if (Serial.available()) {  // Check if data is available on serial port
    String command = Serial.readStringUntil('\n');  // Read command until newline
    command.trim();  // Remove any whitespace

    if (command == "CHECK") {  // If command is CHECK (scan fingerprint)
      int result = getFingerprintID();  // Call function to get fingerprint ID
      if (result >= 0) {  // If match found
        Serial.print("MATCH:");  // Send match prefix
        Serial.println(result);  // Send the matched ID
      } else {
        Serial.println("NO_MATCH");  // Send no match signal
      }
    }
    else if (command.startsWith("ENROLL:")) {  // If command starts with ENROLL:
      int id = command.substring(7).toInt();  // Extract ID from command (after "ENROLL:")
      if (id <= 0) {  // Validate ID
        Serial.println("ERROR: Invalid ID");  // Send error if invalid
      } else {
        enrollFingerprint(id);  // Call enrollment function
      }
    }
  }
}

// Function to get fingerprint ID
int getFingerprintID() {
  uint8_t p = finger.getImage();  // Capture fingerprint image
  if (p != FINGERPRINT_OK) return -1;  // Return -1 if capture failed

  p = finger.image2Tz();  // Convert image to template
  if (p != FINGERPRINT_OK) return -1;  // Return -1 if conversion failed

  p = finger.fingerFastSearch();  // Search for match in stored templates
  if (p != FINGERPRINT_OK) return -1;  // Return -1 if search failed

  return finger.fingerID;  // Return the matched ID
}

// Function to enroll a fingerprint
void enrollFingerprint(int id) {
  Serial.print("Place finger for enrollment ID ");  // Prompt user to place finger
  Serial.println(id);  // Print the ID

  // Step 1: Capture image
  int p = -1;  // Initialize status
  while (p != FINGERPRINT_OK) {  // Loop until image is captured
    p = finger.getImage();  // Attempt to capture image
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image taken");  // Success message
        break;
      case FINGERPRINT_NOFINGER:
        // Keep waiting for finger - no message needed
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error, try again");  // Error message
        break;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error, try again");  // Error message
        break;
      default:
        Serial.println("Unknown error");  // Default error
        break;
    }
  }

  // Step 2: Convert image to template 1
  p = finger.image2Tz(1);  // Convert to first template
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to convert image to template 1");  // Error if failed
    return;  // Exit function
  }

  Serial.println("Remove finger");  // Prompt to remove finger
  delay(2000);  // Wait 2 seconds

  // Step 3: Capture second image
  p = -1;  // Reset status
  while (p != FINGERPRINT_OK) {  // Loop for second capture
    p = finger.getImage();  // Capture second image
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Second image taken");  // Success
        break;
      case FINGERPRINT_NOFINGER:
        break;  // Wait
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error, try again");  // Error
        break;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error, try again");  // Error
        break;
      default:
        Serial.println("Unknown error");  // Error
        break;
    }
  }

  // Step 4: Convert image to template 2
  p = finger.image2Tz(2);  // Convert to second template
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to convert image to template 2");  // Error
    return;  // Exit
  }

  // Step 5: Create model
  p = finger.createModel();  // Create fingerprint model from templates
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to create fingerprint model");  // Error
    return;  // Exit
  }

  // Step 6: Store model in ID
  p = finger.storeModel(id);  // Store model at given ID
  if (p == FINGERPRINT_OK) {
    Serial.print("Enrollment successful! Stored at ID ");  // Success
    Serial.println(id);  // Print ID
  } else {
    Serial.println("Failed to store fingerprint model");  // Error
  }
}