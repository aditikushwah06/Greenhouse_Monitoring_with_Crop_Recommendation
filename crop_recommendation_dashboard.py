import streamlit as st
import requests
import pandas as pd

# CONFIG
st.set_page_config(page_title="Greenhouse Crop Recommender", layout="wide")
st.title("🌱 Greenhouse Crop Recommendation Dashboard")

# 🌦️ External Weather Forecast
st.subheader("🌤️ External Weather Forecast (via OpenWeatherMap)")

# Enter your OpenWeatherMap API key and city
WEATHER_API_KEY = "bd1eea61abef93db6cce5bc84364e272"
CITY = "Gwalior"
weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"

try:
    weather_data = requests.get(weather_url).json()
    weather_temp = weather_data['main']['temp']
    weather_humidity = weather_data['main']['humidity']
    weather_condition = weather_data['weather'][0]['description'].title()
    
    colA, colB, colC = st.columns(3)
    colA.metric("🌡️ Outside Temp", f"{weather_temp} °C")
    colB.metric("💧 Outside Humidity", f"{weather_humidity} %")
    colC.metric("⛅ Condition", weather_condition)

except Exception as e:
    st.warning("⚠️ Unable to fetch weather data. Check your API key or internet connection.")

# 🌿 ThingSpeak Sensor Data
st.subheader("🌿 Current Sensor Readings with Crop Recommendations")

# Fetch Data from ThingSpeak
url = f'https://api.thingspeak.com/channels/2925486/feeds.json?api_key=Y0GUWEIJUUF8RT1R&results=10'
response = requests.get(url)
data = response.json()

# Convert to DataFrame
feeds = data['feeds']
df = pd.DataFrame(feeds)
df = df[['created_at', 'entry_id', 'field1', 'field2', 'field3', 'field4']]
df.columns = ['created_at', 'entry_id', 'temperature', 'humidity', 'soil_moisture_raw', 'light']

# Type conversion
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
df['soil_moisture_raw'] = pd.to_numeric(df['soil_moisture_raw'], errors='coerce')
df['light'] = pd.to_numeric(df['light'], errors='coerce')
df['soil_moisture'] = 1024 - df['soil_moisture_raw']

# Crop database (same as before)
crop_database = [
    {"crop": "Tomato", "temp_range": (18, 30), "humidity_range": (40, 70), "moisture_range": (400, 700), "light": 1, "priority": 1},
    {"crop": "Cucumber", "temp_range": (20, 32), "humidity_range": (45, 80), "moisture_range": (400, 700), "light": 1, "priority": 2},
    {"crop": "Lettuce", "temp_range": (10, 20), "humidity_range": (40, 70), "moisture_range": (600, 900), "light": 0, "priority": 3},
    {"crop": "Spinach", "temp_range": (10, 22), "humidity_range": (40, 70), "moisture_range": (600, 900), "light": 0, "priority": 4},
    {"crop": "Bell Pepper", "temp_range": (18, 28), "humidity_range": (40, 80), "moisture_range": (500, 800), "light": 1, "priority": 5},
    {"crop": "Brinjal", "temp_range": (20, 35), "humidity_range": (40, 70), "moisture_range": (400, 750), "light": 1, "priority": 6},
    {"crop": "Carrot", "temp_range": (16, 25), "humidity_range": (45, 80), "moisture_range": (700, 950), "light": 0, "priority": 7},
    {"crop": "Mint", "temp_range": (15, 25), "humidity_range": (45, 80), "moisture_range": (700, 950), "light": 0, "priority": 8},
    {"crop": "Okra", "temp_range": (22, 35), "humidity_range": (42, 70), "moisture_range": (400, 700), "light": 1, "priority": 9},
    {"crop": "Chilli", "temp_range": (20, 30), "humidity_range": (44, 70), "moisture_range": (500, 800), "light": 1, "priority": 10},
]

# Recommendation function
def recommend_crops(row):
    temp = row['temperature']
    hum = row['humidity']
    soil = row['soil_moisture']
    light = row['light']
    
    suitable_crops = []
    for crop in crop_database:
        if (
            crop["temp_range"][0] <= temp <= crop["temp_range"][1] and
            crop["humidity_range"][0] <= hum <= crop["humidity_range"][1] and
            crop["moisture_range"][0] <= soil <= crop["moisture_range"][1] and
            crop["light"] == light
        ):
            suitable_crops.append({
                "crop": crop["crop"],
                "priority": crop["priority"]
            })
    
    suitable_crops.sort(key=lambda x: x["priority"])
    return [c["crop"] for c in suitable_crops[:3]] if suitable_crops else ["No crops match current conditions"]

# Apply recommendation
df['Recommended Crops'] = df.apply(recommend_crops, axis=1)

# Display
for index, row in df.sort_values(by='created_at', ascending=False).iterrows():
    with st.expander(f"📅 {row['created_at']} - {', '.join(row['Recommended Crops']) if isinstance(row['Recommended Crops'], list) else row['Recommended Crops']}"):
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("🌡️ Temp", f"{row['temperature']}°C")
        with col2: st.metric("💧 Humidity", f"{row['humidity']}%")
        with col3: st.metric("🌱 Soil Moisture", f"{row['soil_moisture']}/1024")
        with col4: st.metric("💡 Light", "High" if row['light'] == 1 else "Low")
        
        if isinstance(row['Recommended Crops'], list):
            st.subheader("Top 3 Recommended Crops:")
            for crop in row['Recommended Crops']:
                st.success(f"✅ {crop}")
        else:
            st.warning("⚠️ No crops match current conditions")

# Footer
st.caption("ℹ️ Data updates on page refresh. External weather helps correlate with internal greenhouse conditions.")
