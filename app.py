from flask import Flask, render_template, request
from Implementations.script1 import add_lat_lng  # Import the function from the script

app = Flask(__name__)

# Define the route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    # Default message when the page is first loaded
    message = "Please enter your latitude and longitude below or select your position on the map."

    # Default values for latitude, longitude, and result
    latitude = None
    longitude = None
    result = None

    if request.method == 'POST':
        # Get the latitude and longitude from the form
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        # Call the add_lat_lng function from the add_coordinates script
        result = add_lat_lng(latitude, longitude)

        # Update the message with the result
        message = f"The sum of latitude {latitude} and longitude {longitude} is: {result}"

    # Render the HTML template and pass the message and coordinates to it
    return render_template('index.html', message=message, latitude=latitude, longitude=longitude)

if __name__ == '__main__':
    app.run(debug=True)
