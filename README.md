# 🌱 Greenhouse Crop Recommendation & Monitoring System

This project is an IoT-based smart greenhouse solution that monitors environmental conditions and provides intelligent crop recommendations. It also predicts watering schedules using ML and sends real-time alerts to farmers.

## 📌 Features

- 🌡️ Real-time monitoring of:
  - Temperature (via DHT11)
  - Humidity (via DHT11)
  - Soil moisture
  - Light intensity (via LDR)
- 📊 Data visualization on [ThingSpeak](https://thingspeak.com/)
- 🤖 Crop recommendation system using AI/ML
- 💧 Watering schedule prediction based on soil conditions
- 🔔 Alerts for critical conditions (e.g., high temperature, dry soil)
- 📡 **Live weather data** fetched via OpenWeatherMap API

---

## 🛠️ Hardware Components

| Component         | Description                            |
|------------------|----------------------------------------|
| ESP8266 (NodeMCU) | Microcontroller with Wi-Fi capability |
| DHT11             | Temperature and Humidity Sensor       |
| Soil Moisture     | Analog soil moisture sensor           |
| LDR               | Light Dependent Resistor              |
| Jumper Wires      | For circuit connections               |
| Power Source      | 5V power supply or USB                |

---

## 📡 Software & Tools

- Arduino IDE (for ESP8266 programming)
- ThingSpeak (IoT cloud platform)
- Python / MATLAB (for AI/ML implementation)
- Google Colab / Jupyter Notebook (for model training)
- OpenWeatherMap API (for live weather)
 ---
 
## 🔗 Weather API Integration

- Platform: [OpenWeatherMap](https://openweathermap.org/api)
- Data fetched: Current temperature, humidity, rainfall, cloud cover
- Use: Improves decision-making by merging **local sensor data** with **external weather conditions**
---

## 🧠 AI/ML Module

- Inputs: Temperature, Humidity, Soil Moisture, Light
- Output: Suitable Crop Recommendation
- Model: Decision Tree / Random Forest (customizable)
- Data Source: Pre-collected environmental datasets (custom or open-source)

---

## 📶 IoT Data Flow

1. Sensors collect real-time environmental data
2. ESP8266 uploads the data to ThingSpeak
3. AI/ML model recommends suitable crops
4. Notifications are sent in case of critical readings

## Thingspeak Dashboard:

![Thingspeak Readings](https://github.com/user-attachments/assets/05318da9-3970-4f41-ac31-11ac2fdee708)

## Crop Recommendation

![Crop Recommendation Dashboard](https://github.com/user-attachments/assets/aadf4bd6-d8bd-49fc-9205-88d6519f161f)

