import streamlit as st
import requests
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler

# Streamlit Page 
st.set_page_config(page_title="Greenhouse Crop Recommender", layout="wide")
st.title("🌱 Greenhouse Crop Recommendation Dashboard")

# External Weather Forecast
st.subheader("🌤️ External Weather Forecast (via OpenWeatherMap)")

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

except Exception:
    st.warning("⚠️ Unable to fetch weather data. Check your API key or internet connection.")

# ThingSpeak Sensor Data
st.subheader("🌿 Current Sensor Readings with Crop Recommendations")

# Fetch latest 10 entries
url = 'https://api.thingspeak.com/channels/2925486/feeds.json?api_key=Y0GUWEIJUUF8RT1R&results=10'

try:
    response = requests.get(url)
    data = response.json()
    feeds = data['feeds']
    df = pd.DataFrame(feeds)
except Exception:
    st.error("❌ Unable to fetch ThingSpeak data.")
    st.stop()

if df.empty:
    st.warning("⚠️ No sensor data available.")
    st.stop()

# Select and rename columns
df = df[['created_at', 'entry_id', 'field1', 'field2', 'field3', 'field4']]
df.columns = ['created_at', 'entry_id', 'temperature', 'humidity', 'soil_moisture_raw', 'light']

# Data Cleaning & Preprocessing
# Convert to numeric safely
for col in ['temperature', 'humidity', 'soil_moisture_raw', 'light']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Compute derived feature
df['soil_moisture'] = 1024 - df['soil_moisture_raw']

# Drop rows with missing values
df.dropna(subset=['temperature', 'humidity', 'soil_moisture', 'light'], inplace=True)

# Clip to realistic greenhouse ranges
df['temperature'] = df['temperature'].clip(5, 40)
df['humidity'] = df['humidity'].clip(10, 90)
df['soil_moisture'] = df['soil_moisture'].clip(50, 950)

# Fill missing light values with mode
df['light'] = df['light'].fillna(df['light'].mode()[0])

# Smooth noisy sensor values
df['temperature'] = df['temperature'].rolling(window=3, min_periods=1).mean()
df['humidity'] = df['humidity'].rolling(window=3, min_periods=1).mean()
df['soil_moisture'] = df['soil_moisture'].rolling(window=3, min_periods=1).mean()

# Training Data (20+ crops + improved 'No Crop')
train_data = [
    # Tomato
    [25, 50, 600, 1, "Tomato"], [26, 55, 620, 1, "Tomato"], [24, 48, 580, 1, "Tomato"],
    # Cucumber
    [22, 55, 650, 1, "Cucumber"], [23, 58, 670, 1, "Cucumber"], [21, 53, 640, 1, "Cucumber"],
    # Lettuce
    [18, 65, 800, 0, "Lettuce"], [19, 60, 820, 0, "Lettuce"], [17, 63, 780, 0, "Lettuce"],
    # Spinach
    [20, 60, 750, 0, "Spinach"], [19, 58, 730, 0, "Spinach"], [21, 62, 770, 0, "Spinach"],
    # Bell Pepper
    [28, 45, 700, 1, "Bell Pepper"], [29, 48, 720, 1, "Bell Pepper"], [27, 44, 680, 1, "Bell Pepper"],
    # Brinjal
    [30, 50, 720, 1, "Brinjal"], [31, 52, 740, 1, "Brinjal"], [29, 48, 700, 1, "Brinjal"],
    # Carrot
    [16, 70, 900, 0, "Carrot"], [17, 68, 880, 0, "Carrot"], [15, 72, 920, 0, "Carrot"],
    # Mint
    [17, 65, 850, 0, "Mint"], [18, 63, 870, 0, "Mint"], [16, 67, 830, 0, "Mint"],
    # Okra
    [32, 50, 680, 1, "Okra"], [33, 52, 700, 1, "Okra"], [31, 48, 660, 1, "Okra"],
    # Chilli
    [26, 55, 750, 1, "Chilli"], [27, 57, 770, 1, "Chilli"], [25, 53, 730, 1, "Chilli"],
    # Peas
    [16, 55, 650, 0, "Peas"], [18, 60, 700, 0, "Peas"], [20, 70, 800, 0, "Peas"],
    # Beans
    [22, 50, 600, 1, "Beans"], [24, 55, 650, 1, "Beans"], [28, 60, 700, 1, "Beans"],
    # Strawberries
    [20, 60, 650, 1, "Strawberries"], [22, 65, 700, 1, "Strawberries"], [25, 70, 750, 1, "Strawberries"],
    # Kale
    [12, 55, 700, 0, "Kale"], [15, 60, 750, 0, "Kale"], [18, 65, 800, 0, "Kale"],
    # Radish
    [13, 60, 750, 0, "Radish"], [15, 65, 800, 0, "Radish"], [18, 70, 850, 0, "Radish"],
    # Broccoli
    [18, 60, 700, 0, "Broccoli"], [20, 62, 720, 0, "Broccoli"], [16, 58, 680, 0, "Broccoli"],
    # Cauliflower
    [17, 60, 700, 0, "Cauliflower"], [18, 62, 730, 0, "Cauliflower"], [16, 58, 680, 0, "Cauliflower"],
    # Sweet Corn
    [25, 55, 700, 1, "Sweet Corn"], [27, 57, 720, 1, "Sweet Corn"], [23, 53, 680, 1, "Sweet Corn"],
    # Spinach Baby Leaf
    [15, 65, 800, 0, "Spinach Baby Leaf"], [16, 63, 820, 0, "Spinach Baby Leaf"], [14, 67, 780, 0, "Spinach Baby Leaf"],
    # Basil
    [20, 60, 700, 1, "Basil"], [22, 62, 720, 1, "Basil"], [18, 58, 680, 1, "Basil"],
    # Lettuce Baby Leaf
    [15, 60, 780, 0, "Lettuce Baby Leaf"], [16, 62, 800, 0, "Lettuce Baby Leaf"], [14, 58, 760, 0, "Lettuce Baby Leaf"],
]

columns = ["temperature", "humidity", "soil_moisture", "light", "crop"]
df_train = pd.DataFrame(train_data, columns=columns)

# Add more realistic 'No Crop' samples
no_crop_samples = [
    [10, 20, 150, 0, "No Crop"],   # too dry
    [35, 90, 850, 1, "No Crop"],   # too humid
    [5, 40, 200, 0, "No Crop"],    # too cold/dry
    [38, 30, 100, 1, "No Crop"],   # too hot/dry
    [40, 50, 900, 1, "No Crop"],   # too wet
]
df_train = pd.concat([df_train, pd.DataFrame(no_crop_samples, columns=columns)], ignore_index=True)

# Model Training
X_train = df_train[["temperature", "humidity", "soil_moisture", "light"]]
y_train = df_train["crop"]

scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# Validation & Prediction Functions
def validate_sensor(row):
    """Ensure sensor data falls in realistic growing ranges."""
    if not (10 <= row['temperature'] <= 35):
        return False
    if not (30 <= row['humidity'] <= 85):
        return False
    if not (300 <= row['soil_moisture'] <= 850):
        return False
    return True

def predict_top_crops(row, top_n=3):
    features = [[row['temperature'], row['humidity'], row['soil_moisture'], row['light']]]
    features_scaled = scaler.transform(features)
    probs = rf_model.predict_proba(features_scaled)[0]
    classes = rf_model.classes_
    top_indices = probs.argsort()[-top_n:][::-1]
    return [classes[i] for i in top_indices]

# Apply Predictions

df['Recommended Crops'] = df.apply(
    lambda row: predict_top_crops(row) if validate_sensor(row) else ["No crops — sensor values invalid"],
    axis=1
)

# Display Dashboard

for index, row in df.sort_values(by='created_at', ascending=False).iterrows():
    with st.expander(f"📅 {row['created_at']} - {', '.join(row['Recommended Crops'])}"):
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("🌡️ Temp", f"{row['temperature']:.1f} °C")
        with col2: st.metric("💧 Humidity", f"{row['humidity']:.1f} %")
        with col3: st.metric("🌱 Soil Moisture", f"{row['soil_moisture']:.0f}/1024")
        with col4: st.metric("💡 Light", "High" if row['light'] == 1 else "Low")

        st.subheader("Top 3 Recommended Crops:")
        for crop in row['Recommended Crops']:
            st.success(f"✅ {crop}")


# Footer
st.caption("ℹ️ Data updates on page refresh. External weather helps correlate with internal greenhouse conditions.")
