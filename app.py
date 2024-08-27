from flask import Flask, render_template, request, redirect, url_for
import requests  # Import the requests module
from Implementations.Schemes.PairingFunctions.main import shamir_secret_sharing
import Implementations.Schemes.TwoPolyShamir.scheme2 as scheme2_module
# Import other schemes as needed

app = Flask(__name__)

def get_location_info(latitude, longitude):
    # Assuming you already have this implemented, here's a placeholder
    # Replace this with your actual implementation to fetch city and country based on coordinates
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    headers = {"User-Agent": "YourAppName/1.0 (yourname@example.com)"}  # Replace with your app's name and contact info

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            city = address.get('city', 'Unknown')
            country = address.get('country', 'Unknown')
            return city, country
    except Exception as e:
        print(f"Error fetching location info: {e}")
    return "Unknown", "Unknown"

@app.route('/', methods=['GET', 'POST'])
def index():
    message = "Please enter your latitude and longitude, choose t and n, and select the secret sharing scheme."
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        t = int(request.form['t'])
        n = int(request.form['n'])
        scheme = request.form['scheme']

        # Redirect to the appropriate scheme route
        return redirect(url_for(scheme, latitude=latitude, longitude=longitude, t=t, n=n))

    return render_template('index.html', message=message)

@app.route('/scheme1')
def scheme1():
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))
    t = int(request.args.get('t'))
    n = int(request.args.get('n'))

    result = shamir_secret_sharing(latitude, longitude, t=t, n=n)

    # Get inputted city and country
    input_city, input_country = get_location_info(latitude, longitude)

    # Get recovered city and country
    recovered_city, recovered_country = get_location_info(result['recovered_latitude'], result['recovered_longitude'])

    return render_template(
        'scheme1.html',
        result=result,
        latitude=latitude,
        longitude=longitude,
        city=input_city,
        country=input_country,
        recovered_city=recovered_city,
        recovered_country=recovered_country,
        backend_info="This page is using the main.py backend script."
    )

@app.route('/scheme2')
def scheme2():
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))
    t = int(request.args.get('t'))
    n = int(request.args.get('n'))

    recovered_latitude, recovered_longitude, shares = scheme2_module.process_scheme2(latitude, longitude, t, n)

    # Get inputted city and country
    input_city, input_country = get_location_info(latitude, longitude)

    # Get recovered city and country
    recovered_city, recovered_country = get_location_info(recovered_latitude, recovered_longitude)

    result = {
        "recovered_latitude": recovered_latitude,
        "recovered_longitude": recovered_longitude,
        "shares": shares
    }

    return render_template(
        'scheme2.html',
        result=result,
        latitude=latitude,
        longitude=longitude,
        city=input_city,
        country=input_country,
        recovered_city=recovered_city,
        recovered_country=recovered_country,
        backend_info="This page is using the scheme2.py backend script."
    )

@app.route('/scheme3')
def scheme3():
    # Implement similar to scheme1 and scheme2
    pass

if __name__ == '__main__':
    app.run(debug=True)
