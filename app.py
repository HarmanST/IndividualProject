from flask import Flask, render_template, request, redirect, url_for, session
import requests
import time
import tracemalloc

from Implementations.Schemes.ShamirsPairing.shamirsPairing import recover_location_shamirs_pairing, create_shares_shamirs_pairing

import Implementations.Schemes.TwoPolyShamir.shamirs2poly as two_poly_shamir
from Implementations.Schemes.TwoPolyShamir.shamirs2poly import recover_location

from Implementations.Schemes.AsmuthBloom_Pairing.asmuthPairing import create_shares, reconstruct_coordinates




app = Flask(__name__)
app.secret_key = 'your_secret_key'  # for session management

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
        selected_apps = request.form.get('selected_apps')
        selected_apps_list = selected_apps.split(',') if selected_apps else []
        create_share_time = 0
        mem = 0

        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        t = int(request.form['t'])   #Threshold
        n = len(selected_apps_list)  # number of selected apps

        # Validate that n is greater than or equal to t
        if n < t:
            message = f"Error: The number of selected apps (n={n}) must be greater than or equal to the minimum shares (t={t})."
            return render_template('index.html', message=message)

        scheme = request.form['scheme']

        # Generate shares based on selected scheme
        if scheme == 'shamirs_pairing':
            start_time = time.perf_counter()
            tracemalloc.start()

            #creating shares (main task)
            result = create_shares_shamirs_pairing(latitude, longitude, t=t, n=n)

            mem = tracemalloc.get_traced_memory()
            end_time = time.perf_counter()
            tracemalloc.stop()

            create_share_time = end_time - start_time

        elif scheme == 'two_poly_shamir':
            start_time = time.perf_counter()
            tracemalloc.start()

            #creating shares (main task)
            result = two_poly_shamir.generate_location_shares(latitude, longitude, t, n)

            mem = tracemalloc.get_traced_memory()
            end_time = time.perf_counter()
            tracemalloc.stop()

            create_share_time = end_time - start_time


        elif scheme == 'Asmuths_pairing':
            start_time = time.perf_counter()
            tracemalloc.start()


            #creating shares (main task)
            result = create_shares(n, t, longitude, latitude)
            print("Moduli: ", result['moduli'])

            mem = tracemalloc.get_traced_memory()
            end_time = time.perf_counter()
            tracemalloc.stop()

            create_share_time = end_time - start_time

        else:
            result = None  # Handle other schemes

        # Save relevant data in session for later use
        session['result'] = result
        session['scheme'] = scheme
        session['selected_apps'] = selected_apps
        session['t'] = t
        session['n'] = n
        session['create_share_time'] = create_share_time
        session['create_share_mem'] = mem


        # Redirect to the page that displays the shares
        return redirect(url_for('display_shares'))

    return render_template('index.html', message=message)

@app.route('/display_shares')
def display_shares():
    result = session.get('result')
    scheme = session.get('scheme')
    selected_apps = session.get('selected_apps', "")
    selected_apps_list = selected_apps.split(',') if selected_apps else []
    create_share_time = session.get('create_share_time')
    create_share_mem = session.get('create_share_mem')

    # Zip shares with selected apps
    if scheme == 'shamirs_pairing':
        shares_with_apps = list(zip(result['shares'], selected_apps_list))
    elif scheme == 'two_poly_shamir':
        shares_with_apps = list(zip(result, selected_apps_list))
    elif scheme == 'Asmuths_pairing':
        shares_with_apps = list(zip(result['shares'], result['moduli'], selected_apps_list))
    else:
        shares_with_apps = []

    # Render appropriate template based on scheme
    if scheme == 'shamirs_pairing':
        template = 'display_shares_shamirs_pairing_func.html'
    elif scheme == 'two_poly_shamir':
        template = 'display_shares_two_poly_shamir.html'
    elif scheme == 'Asmuths_pairing':
        template = 'display_shares_asmuth_pairing.html'
    else:
        template = 'display_shares_other.html'

    return render_template(
        template,
        result={"shares": shares_with_apps},
        scheme=scheme,
        selected_apps=selected_apps_list,
        time=create_share_time,
        mem=create_share_mem
    )


@app.route('/reconstruct')
def reconstruct():
    scheme = session.get('scheme')
    result = session.get('result')
    selected_apps = session.get('selected_apps', "")
    selected_apps_list = selected_apps.split(',') if selected_apps else []
    t = session.get('t')
    n = session.get('n')
    reconstruct_time = 0
    mem = 0

    # Get the shares from the result
    if scheme == 'shamirs_pairing':
        shares = result['shares']  # Shares for Shamir's pairing scheme

        start_time = time.perf_counter()
        tracemalloc.start()

        # Recover location using the backend function
        recovered_location = recover_location_shamirs_pairing(shares[:t], t)
        recovered_latitude = recovered_location['recovered_latitude']
        recovered_longitude = recovered_location['recovered_longitude']

        mem = tracemalloc.get_traced_memory()
        end_time = time.perf_counter()

        tracemalloc.stop()
        reconstruct_time = end_time - start_time

    elif scheme == 'two_poly_shamir':
        shares = result

        lat_shares = [(share[0], share[1]) for share in shares[:t]]
        lon_shares = [(share[0], share[2]) for share in shares[:t]]

        start_time = time.perf_counter()
        tracemalloc.start()

        recovered_latitude, recovered_longitude = recover_location(lat_shares, lon_shares)

        mem = tracemalloc.get_traced_memory()
        end_time = time.perf_counter()
        tracemalloc.stop()

        reconstruct_time = end_time - start_time

    elif scheme == 'Asmuths_pairing':
        shares = result['shares']
        m = result['moduli']

        start_time = time.perf_counter()
        tracemalloc.start()

        recovered_location = reconstruct_coordinates(shares, m, t)

        mem = tracemalloc.get_traced_memory()
        end_time = time.perf_counter()
        tracemalloc.stop()

        reconstruct_time = end_time - start_time

        recovered_latitude = recovered_location['recovered_latitude']
        recovered_longitude = recovered_location['recovered_longitude']

    else:
        recovered_latitude, recovered_longitude = None, None  # Handle other schemes

    # Get recovered city and country based on latitude and longitude
    recovered_city, recovered_country = get_location_info(recovered_latitude, recovered_longitude)

    # Render the appropriate template based on the scheme
    if scheme == 'shamirs_pairing':
        template = 'reconstruct_shamirs_pairing_func.html'
    elif scheme == 'two_poly_shamir':
        template = 'reconstruct_two_poly_shamir.html'
    elif scheme == 'Asmuths_pairing':
        template = 'reconstruct_asmuth_pairing.html'
    else:
        template = 'reconstruct_other.html'  # Handle other schemes

    return render_template(
        template,
        recovered_latitude=recovered_latitude,
        recovered_longitude=recovered_longitude,
        recovered_city=recovered_city,
        recovered_country=recovered_country,
        time=reconstruct_time,
        mem=mem
    )

if __name__ == '__main__':
    app.run(debug=True)
