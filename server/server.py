from flask import Flask, jsonify
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
import google.generativeai as genai
import logging # Import logging


logging.basicConfig(level=logging.INFO)


load_dotenv()


app = Flask(__name__)


OWM_API_KEY = os.getenv('OWM_API_KEY')
if not OWM_API_KEY:
    logging.warning("OpenWeatherMap OWM_API_KEY not found in environment variables.")


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    logging.error("GOOGLE_API_KEY not found in environment variables. Gemini features will be disabled.")


LAT, LON = "40.7128", "-74.0060"


# Gemini AI Setup
gemini_model = None
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # 'gemini-2.0-flash-lite' is the free model name for Gemini
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
        logging.info("Gemini AI Model configured successfully with 'gemini-2.0-flash-lite'.")
    except Exception as e:
        logging.error(f"Error configuring Gemini AI: {e}. Gemini features will be disabled.")
        gemini_model = None
else:
    logging.warning("GOOGLE_API_KEY is missing. Gemini features are disabled.")




# Weather Fetching Logic
def get_today_forecast():
    """Fetches today's forecast from OpenWeatherMap."""
    if not OWM_API_KEY:
        logging.error("Cannot fetch forecast: OpenWeatherMap API Key is missing.")
        return None


    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={OWM_API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()


        today = datetime.now(timezone.utc).date()
        today_forecast_entries = []

        # Check if 'list' exists and is a list
        if "list" in data and isinstance(data["list"], list):
            for entry in data["list"]:
                # Basic check for expected structure
                if "dt" in entry:
                    forecast_time = datetime.fromtimestamp(entry["dt"])
                    logging.info(f"Forecast entry time: {forecast_time.date()}")
                    if forecast_time.date() == today:
                        today_forecast_entries.append(entry)
                else:
                    logging.warning(f"Skipping forecast entry due to missing 'dt': {entry}")
            return today_forecast_entries
        else:
            logging.error(f"Unexpected response format from OpenWeatherMap: 'list' key missing or not a list. Response: {data}")
            return None


    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data from OpenWeatherMap: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during forecast fetching or processing: {e}")
        return None


def get_clothing_suggestion_with_gemini():
    """Generates clothing suggestions using Gemini based on today's forecast."""
    if not gemini_model:
        logging.error("Gemini model not available for generating suggestions.")
        return "Error: AI suggestion service is unavailable."


    forecast_entries = get_today_forecast()
    if not forecast_entries:
        logging.warning("No forecast data available to generate clothing suggestion.")
        return "Could not retrieve weather data to make a suggestion."


    if not forecast_entries:
            return "No forecast entries found for today."


    # Extract temperature data
    temps = [hour['main']['temp'] for hour in forecast_entries if 'main' in hour and 'temp' in hour['main']]
    if not temps:
        logging.warning("No temperature data found in forecast entries.")
        return "Could not extract temperature data from forecast."


    max_temp = max(temps)
    min_temp = min(temps)


    will_rain = False
    will_snow = False
    rain_details = []
    snow_details = []


    # Check for rain and snow in the forecast
    for hour in forecast_entries:
        if 'rain' in hour and isinstance(hour['rain'], dict) and hour['rain'].get('3h', 0) > 0:
            will_rain = True
            rain_details.append(f"Rain volume: {hour['rain'].get('3h', 0)}mm")
        if 'snow' in hour and isinstance(hour['snow'], dict) and hour['snow'].get('3h', 0) > 0:
            will_snow = True
            snow_details.append(f"Snow volume: {hour['snow'].get('3h', 0)}mm")
        if 'weather' in hour and isinstance(hour['weather'], list) and hour['weather']:
                description = hour['weather'][0].get('description', '').lower()
                if 'rain' in description:
                    will_rain = True
                if 'snow' in description:
                    will_snow = True


    # Prepare conditions based on rain and snow
    conditions = []
    if will_rain:
        conditions.append("potential for rain")
    if will_snow:
        conditions.append("potential for snow")
    if not conditions:
            # Get a general description from the middle of the day if possible
        mid_day_entry = forecast_entries[len(forecast_entries)//2] if forecast_entries else None
        if mid_day_entry and 'weather' in mid_day_entry and mid_day_entry['weather']:
            conditions.append(mid_day_entry['weather'][0].get('description', 'clear skies'))
        else:
            conditions.append("generally clear or cloudy skies")




    # Construct the Prompt
    prompt = f"""
    Given the following weather forecast for New York City today:
    - Minimum Temperature: {min_temp:.1f}°F
    - Maximum Temperature: {max_temp:.1f}°F
    - Conditions: {', '.join(conditions)}


    Please suggest practical clothing items suitable for these conditions.
    Provide the recommendation as a concise, comma-separated list (e.g., warm jacket, hoodie,pants, scarf, waterproof boots, thermal underwear (if below 30 F)),
    any rain equipment like an umbrella if the precipitation is high or a rain jacket if the precipitation is low enough, heavy gloves if weather is around 30F,
    light gloves if the weather is around 45F.
    Do not add any extra explanation before or after the list.
    """


    logging.info(f"Sending prompt to Gemini: {prompt}") # Log the prompt being sent
    try:
        response = gemini_model.generate_content(prompt)


        suggestion = response.text.strip()
        logging.info(f"Received suggestion from Gemini: {suggestion}")
        return suggestion


    except Exception as e:
        logging.error(f"Error generating clothing suggestion with Gemini: {e}")
        try:
            # Attempt to get feedback if the error occurred after the API call
             logging.error(f"Gemini prompt feedback: {response.prompt_feedback}")
        except Exception:
             pass # Ignore if feedback isn't available
        return "Error: Could not generate AI suggestion due to an internal error."


@app.route("/what_to_wear", methods=["GET"])
def what_to_wear():
    suggestion = get_clothing_suggestion_with_gemini()
    return jsonify({"recommendation": suggestion})


if __name__ == "__main__":
    print(get_clothing_suggestion_with_gemini())