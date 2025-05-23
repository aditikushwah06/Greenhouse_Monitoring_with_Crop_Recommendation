#include <ESP8266WiFi.h>
#include <ThingSpeak.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "Poco M2 Pro";            // 🔁 Replace with your WiFi SSID
const char* password = "jalaj@2426";    // 🔁 Replace with your WiFi Password

// ThingSpeak credentials
unsigned long channelID = 2925486;         // 🔁 Replace with your ThingSpeak Channel ID
const char* apiKey = "3X99YH0PM79NEYY8"; // 🔁 Replace with your Write API Key

// Sensor pins (based on ESP8266 NodeMCU)
#define DHTPIN D4                // DHT22 data pin connected to D4 (GPIO2)
#define DHTTYPE DHT11           // Use DHT22 sensor
#define soilMoisturePin A0      // Soil Moisture sensor on analog pin A0
#define lightSensorPin D3       // LDR connected to D3 (GPIO0) - digital pin

DHT dht(DHTPIN, DHTTYPE);
WiFiClient client;

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(lightSensorPin, INPUT);  // LDR as digital input

  // Connect to Wi-Fi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Initialize ThingSpeak
  ThingSpeak.begin(client);
}

void loop() {
  // Read temperature and humidity from DHT22
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Read soil moisture
  int soilMoisture = analogRead(soilMoisturePin); // Value between 0–1023

  // Read light condition (digital)
  int lightLevel = digitalRead(lightSensorPin); // 0 = dark, 1 = bright

  // Debugging in Serial Monitor
  Serial.print("Temperature: "); Serial.print(temperature); Serial.println(" °C");
  Serial.print("Humidity: "); Serial.print(humidity); Serial.println(" %");
  Serial.print("Soil Moisture: "); Serial.println(soilMoisture);
  Serial.print("Light Condition: "); Serial.println(lightLevel == 1 ? "Bright" : "Dark");

  // Send to ThingSpeak
  ThingSpeak.setField(1, temperature);     // Field 1 - Temperature
  ThingSpeak.setField(2, humidity);        // Field 2 - Humidity
  ThingSpeak.setField(3, soilMoisture);    // Field 3 - Soil Moisture
  ThingSpeak.setField(4, lightLevel);      // Field 4 - Light (0/1)

  // Write to ThingSpeak
  int response = ThingSpeak.writeFields(channelID, apiKey);
  if (response == 200) {
    Serial.println("✅ Data sent to ThingSpeak successfully!");
  } else {
    Serial.print("❌ Error sending data: ");
    Serial.println(response);
  }

  delay(15000); // Wait 15 seconds before sending next set of data
}
