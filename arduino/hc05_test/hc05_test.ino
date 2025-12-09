// HC-05 Unit Test Sketch
// Uses ArduinoUnit for testing and SoftwareSerial for HC-05 communication
// Pin assignments: HC-05 RX -> Arduino pin 10, HC-05 TX -> Arduino pin 11

#include <ArduinoUnit.h>
#include <SoftwareSerial.h>

// Pin definitions (adjust if needed)
const uint8_t HC05_RX_PIN = 10; // Arduino receives from HC-05 TX
const uint8_t HC05_TX_PIN = 11; // Arduino transmits to HC-05 RX

SoftwareSerial hc05(HC05_RX_PIN, HC05_TX_PIN); // RX, TX

// Helper: send AT command and wait for response
String sendATCommand(const String &cmd, unsigned long timeout = 2000) {
  hc05.println(cmd);
  unsigned long start = millis();
  String resp = "";
  while (millis() - start < timeout) {
    if (hc05.available()) {
      char c = hc05.read();
      resp += c;
    }
  }
  return resp;
}

// Helper: read any pending response (used after data echo test)
String readResponse(unsigned long timeout = 2000) {
  unsigned long start = millis();
  String resp = "";
  while (millis() - start < timeout) {
    if (hc05.available()) {
      char c = hc05.read();
      resp += c;
    }
  }
  return resp;
}

void setup() {
  // Serial monitor for test output
  Serial.begin(9600);
  // Give the HC-05 time to power up
  delay(1000);
  // Initialise SoftwareSerial at 9600 baud (default HC-05 AT mode speed)
  hc05.begin(9600);

  // Register tests
  Test::run();
}

void loop() {
  // Nothing – tests run in setup()
}

// ---------- Test Cases ----------

test(test_initialization) {
  String resp = sendATCommand("AT");
  assertTrue(resp.indexOf("OK") != -1);
}

test(test_set_name) {
  String resp = sendATCommand("AT+NAME=TestDevice");
  assertTrue(resp.indexOf("OK") != -1);
}

// In loopback mode (AT+ROLE=0) the module echoes data back.
// This test assumes the module is already set to loopback or is in command mode that echoes.

test(test_data_echo) {
  // Ensure we are in data mode – send a dummy character to exit AT mode if needed
  hc05.println("AT");
  delay(100);
  // Send data
  const String payload = "HelloHC05";
  hc05.print(payload);
  String echo = readResponse();
  assertEqual(echo, payload);
}
