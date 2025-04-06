from flask import Flask, jsonify
import os
import requests

app = Flask(__name__)
app.config['API_KEY'] = os.getenv('API_KEY')

API_KEY = app.config['API_KEY']
# Coordinates for New York City
LAT, LON = "40.7128", "-74.0060"

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=imperial"
    response = requests.get(url).json()
    temp = response["main"]["temp"]
    rain = response.get("rain", {}).get("1h", 0)  # Rain in last hour
    return temp, rain

def get_clothing_suggestion():
    temp, rain = get_weather()
    if temp < 40:
        return "heavy coat"
    elif temp < 60:
        return "light jacket"
    elif temp > 70:
        return "t-shirt"
    if rain > 0:
        return "rain jacket"
    return "comfortable clothes"

@app.route("/what_to_wear", methods=["GET"])
def what_to_wear():
    return jsonify({"recommendation": get_clothing_suggestion()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
