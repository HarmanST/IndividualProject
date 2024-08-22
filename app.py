from flask import Flask, render_template, request
from Implementations.Schemes.PairingFunctions.main import shamir_secret_sharing
import requests

app = Flask(__name__)

def get_location_info(latitude, longitude):
    """Fetch city and country based on latitude and longitude using Nominatim API."""
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    headers = {
        "User-Agent": "YourAppName/1.0 (yourname@example.com)"  # Replace with your app's name and contact info
    }

    print(f"Making API request to: {url}")

    try:
        response = requests.get(url, headers=headers)
        print(f"Received response with status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("API Response JSON:", data)
            address = data.get('address', {})
            print("Address Dictionary:", address)

            city = (address.get('city') or
                    address.get('town') or
                    address.get('village') or
                    address.get('municipality', 'Unknown'))
            country = address.get('country', 'Unknown')
            print(f"Extracted City: {city}, Country: {country}")
            return city, country
        else:
            print(f"Error: Received status code {response.status_code} from Nominatim API.")
            return "Unknown", "Unknown"
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return "Unknown", "Unknown"
    except requests.exceptions.JSONDecodeError:
        print("Error: Received invalid JSON from Nominatim API.")
        return "Unknown", "Unknown"




@app.route('/', methods=['GET', 'POST'])
def index():
    message = "Please enter your latitude and longitude below or select your position on the map."
    latitude = None
    longitude = None
    result = None
    city = None
    country = None

    if request.method == 'POST':
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        t = int(request.form['t'])
        n = int(request.form['n'])

        result = shamir_secret_sharing(latitude, longitude, t=t, n=n)

        city, country = get_location_info(latitude, longitude)
        message = "Results successfully computed."

    return render_template('index.html', message=message, result=result, latitude=latitude, longitude=longitude, city=city, country=country)

if __name__ == '__main__':
    app.run(debug=True)
