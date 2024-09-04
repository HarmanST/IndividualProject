from flask import Flask, render_template, request, redirect, url_for, session
import requests
import time
from Implementations.Schemes.PairingFunctions.main import recover_location_shamirs_pairing, create_shares_shamirs_pairing
import Implementations.Schemes.TwoPolyShamir.scheme2 as two_poly_shamir
from Implementations.Schemes.TwoPolyShamir.scheme2 import recover_location

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

def get_location_info(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    headers = {"User-Agent": "YourAppName/1.0 (yourname@example.com)"}

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
    message = "Please enter your latitude and longitude, choose t, apps, and select the secret sharing scheme."
    if request.method == 'POST':
        # Capture selected apps
        selected_apps = request.form.get('selected_apps')
        selected_apps_list = selected_apps.split(',') if selected_apps else []

        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        t = int(request.form['t'])
        n = len(selected_apps_list)  # Use the number of selected apps as 'n'

        # Validate that n is greater than or equal to t
        if n < t:
            message = f"Error: The number of selected apps (n={n}) must be greater than or equal to the minimum shares (t={t})."
            return render_template('index.html', message=message)

        scheme = request.form['scheme']

        # Generate shares based on selected scheme
        if scheme == 'shamirs_pairing':
            start_time = time.perf_counter()

            #creating shares with function from backend script
            result = create_shares_shamirs_pairing(latitude, longitude, t=t, n=n)

            end_time = time.perf_counter()
            create_share_time_shamirs_pairing = end_time - start_time
            print(f"Time for creating shares with Shamri's SSS w/ pairing functions {create_share_time_shamirs_pairing} ")

        elif scheme == 'two_poly_shamir':
            start_time = time.perf_counter()

            result = two_poly_shamir.generate_location_shares(latitude, longitude, t, n)

            end_time = time.perf_counter()
            create_share_time_shamirs_pairing = end_time - start_time
            print(f"Time for creating shares with Shamri's SSS w/ two polynomials {create_share_time_shamirs_pairing} ")
        else:
            result = None  # Handle other schemes

        # Save relevant data in session for later use
        #session['latitude'] = latitude
        #session['longitude'] = longitude
        session['result'] = result
        session['scheme'] = scheme
        session['selected_apps'] = selected_apps  # Store selected apps in session


        # Redirect to the page that displays the shares
        return redirect(url_for('display_shares'))

    return render_template('index.html', message=message)

@app.route('/display_shares')
def display_shares():
    #latitude = session.get('latitude')
    #longitude = session.get('longitude')
    result = session.get('result')
    scheme = session.get('scheme')
    selected_apps = session.get('selected_apps', "")
    selected_apps_list = selected_apps.split(',') if selected_apps else []

    # Zip shares with selected apps
    if scheme == 'shamirs_pairing':
        shares_with_apps = list(zip(result['shares'], selected_apps_list))
    elif scheme == 'two_poly_shamir':
        shares_with_apps = list(zip(result, selected_apps_list))
    else:
        shares_with_apps = []

    # Get inputted city and country
    #input_city, input_country = get_location_info(latitude, longitude)

    # Render appropriate template based on scheme
    if scheme == 'shamirs_pairing':
        template = 'display_shares_shamirs_pairing_func.html'
    elif scheme == 'two_poly_shamir':
        template = 'display_shares_two_poly_shamir.html'
    else:
        template = 'display_shares_other.html'  # Default or other schemes

    return render_template(
        template,
        result={"shares": shares_with_apps},
        #latitude=latitude,
        #longitude=longitude,
        #city=input_city,
        #country=input_country,
        scheme=scheme,
        selected_apps=selected_apps_list  # Pass the list of selected apps
    )


@app.route('/reconstruct')
def reconstruct():
    scheme = session.get('scheme')
    result = session.get('result')
    selected_apps = session.get('selected_apps', "")
    selected_apps_list = selected_apps.split(',') if selected_apps else []

    # Get the shares from the result
    if scheme == 'shamirs_pairing':
        shares = result['shares']  # Shares for Shamir's pairing scheme
        t = len(selected_apps_list)  # Assuming t is the number of selected apps

        # Recover location using the backend function
        recovered_location = recover_location_shamirs_pairing(shares[:t], t)
        recovered_latitude = recovered_location['recovered_latitude']
        recovered_longitude = recovered_location['recovered_longitude']

    elif scheme == 'two_poly_shamir':
        shares = result
        t = len(selected_apps_list)

        lat_shares = [(share[0], share[1]) for share in shares[:t]]
        lon_shares = [(share[0], share[2]) for share in shares[:t]]

        recovered_latitude, recovered_longitude = recover_location(lat_shares, lon_shares)

    else:
        recovered_latitude, recovered_longitude = None, None  # Handle other schemes

    # Get recovered city and country based on latitude and longitude
    recovered_city, recovered_country = get_location_info(recovered_latitude, recovered_longitude)

    # Render the appropriate template based on the scheme
    if scheme == 'shamirs_pairing':
        template = 'reconstruct_shamirs_pairing_func.html'
    elif scheme == 'two_poly_shamir':
        template = 'reconstruct_two_poly_shamir.html'
    else:
        template = 'reconstruct_other.html'  # Handle other schemes

    return render_template(
        template,
        recovered_latitude=recovered_latitude,
        recovered_longitude=recovered_longitude,
        recovered_city=recovered_city,
        recovered_country=recovered_country
    )

if __name__ == '__main__':
    app.run(debug=True)
