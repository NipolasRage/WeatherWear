from flask import Flask, jsonify
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
import time

load_dotenv()

app = Flask(__name__)
app.config['API_KEY'] = os.getenv('API_KEY')

API_KEY = app.config['API_KEY']
# Coordinates for New York City
LAT, LON = "40.7128", "-74.0060"

def get_today_forecast():
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=imperial"
    response = requests.get(url).json()
    
    today = datetime.now(timezone.utc).date()
    today_forecast = []

    for entry in response["list"]:
        forecast_time = datetime.fromtimestamp(entry["dt"])
        if forecast_time.date() == today:
            today_forecast.append(entry)
    
    return today_forecast

def get_clothing_suggestion():
    forecast = get_today_forecast()
    max_temp = max(hour['main']['temp'] for hour in forecast)
    min_temp = min(hour['main']['temp'] for hour in forecast)
    will_rain = any('rain' in hour for hour in forecast)
    will_snow = any('snow' in hour for hour in forecast)
    rain_amounts = [hour.get('rain', {}).get('3h', 0) for hour in forecast if 'rain' in hour]
    heavy_rain = any(r > 5 for r in rain_amounts)

    suggestion = []

    print(f"Max Temp: {max_temp}, Min Temp: {min_temp}, Will Rain: {will_rain}, Will Snow: {will_snow}, Heavy Rain: {heavy_rain}")
    print(f"Rain Amounts: {rain_amounts}")
    if min_temp < 20:
        suggestion.append("thermal underwear")
        suggestion.append("heavy coat")
    elif min_temp < 30:
        suggestion.append("thermal underwear if biking")
        suggestion.append("heavy coat")
    elif min_temp < 40:
        suggestion.append("coat")
    elif max_temp > 75:
        suggestion.append("t-shirt")
        suggestion.append("shorts")
    elif max_temp < 65:
        suggestion.append("warm jacket")
    else:
        suggestion.append("warm-comfortable clothes")

    if will_rain:
        suggestion.append("rain jacket")
    if heavy_rain:
        suggestion.append("umbrella")
    if will_snow:
        suggestion.append("winter boots")

    return ", ".join(suggestion)



@app.route("/what_to_wear", methods=["GET"])
def what_to_wear():
    return jsonify({"recommendation": get_clothing_suggestion()})

if __name__ == "__main__":
    print(get_clothing_suggestion())
    # app.run(host="0.0.0.0", port=5000)
