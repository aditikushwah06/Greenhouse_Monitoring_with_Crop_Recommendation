#include <ESP8266WiFi.h>
#include <ThingSpeak.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "Poco M2 Pro";
const char* password = "jalaj@2426";

// ThingSpeak credentials
unsigned long channelID = 2925486;
const char* apiKey = "3X99YH0PM79NEYY8";

// Sensor pins
#define DHTPIN D4
#define DHTTYPE DHT11
#define soilMoisturePin A0
#define lightSensorPin D3
#define relayPin D2             // Relay module control pin

// Irrigation settings
int soilMoistureThreshold = 500; // Adjust this based on calibration

DHT dht(DHTPIN, DHTTYPE);
WiFiClient client;

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(lightSensorPin, INPUT);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);  // Relay off initially (active LOW)

  // Connect to Wi-Fi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected");

  // Initialize ThingSpeak
  ThingSpeak.begin(client);
}

void loop() {
  // Reconnect WiFi if disconnected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Reconnecting WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
    }
    Serial.println("\nWiFi reconnected");
  }

  // Read sensors
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int soilMoisture = analogRead(soilMoisturePin);
  int lightLevel = digitalRead(lightSensorPin);

  // Debug output
  Serial.println("=== Sensor Readings ===");
  Serial.print("Temperature: "); Serial.print(temperature); Serial.println(" °C");
  Serial.print("Humidity: "); Serial.print(humidity); Serial.println(" %");
  Serial.print("Soil Moisture: "); Serial.println(soilMoisture);
  Serial.print("Light: "); Serial.println(lightLevel == 1 ? "Bright" : "Dark");

  // 🌿 Automated irrigation control
  if (soilMoisture > soilMoistureThreshold) {
    digitalWrite(relayPin, LOW); // Turn pump ON
    Serial.println("💧 Soil dry - Pump ON");
  } else {
    digitalWrite(relayPin, HIGH); // Turn pump OFF
    Serial.println("🪴 Soil wet - Pump OFF");
  }

  // Send only sensor data to ThingSpeak
  ThingSpeak.setField(1, temperature);   // Field 1 - Temperature
  ThingSpeak.setField(2, humidity);      // Field 2 - Humidity
  ThingSpeak.setField(3, soilMoisture);  // Field 3 - Soil Moisture
  ThingSpeak.setField(4, lightLevel);    // Field 4 - Light (0/1)

  int response = ThingSpeak.writeFields(channelID, apiKey);
  if (response == 200) {
    Serial.println("✅ Data sent to ThingSpeak!");
  } else {
    Serial.print("❌ Error sending data: ");
    Serial.println(response);
  }

  delay(20000); // Wait 20 seconds before next update
}
