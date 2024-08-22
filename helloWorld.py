from flask import Flask

# Create an instance of the Flask class.
# The first argument is the name of the application's module or package.
# __name__ is a special variable in Python that holds the name of the current module.
# Flask uses this argument to determine the root path for the application.
app = Flask(__name__)

# Define a route for the root URL ('/').
# A route is a URL pattern that is linked to a specific function in your application.
# The route() decorator tells Flask to call the following function when someone visits this URL.
@app.route('/')
def hello_world():
    # This is the function that is called when the root URL is accessed.
    # It returns the string 'Hello, World!', which will be displayed in the browser.
    return 'Hello, World!'

# This block ensures that the Flask application runs only if this script is executed directly.
# The condition checks if the script is being run as the main program.
# If the script is imported as a module in another script, the block will not be executed.
if __name__ == '__main__':
    # app.run() starts the Flask development server.
    # The server is provided by Flask and is intended for use during development.
    # The debug=True argument enables debug mode, which provides detailed error messages
    # and automatically reloads the server when code changes are detected.
    app.run(debug=True)
