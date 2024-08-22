# add_coordinates.py

def add_lat_lng(latitude, longitude):
    """
    Function to add latitude and longitude values.

    Args:
        latitude (float): The latitude value.
        longitude (float): The longitude value.

    Returns:
        float: The sum of latitude and longitude.
    """
    try:
        # Convert latitude and longitude to floats and add them
        result = float(latitude) + float(longitude)
        return result
    except ValueError:
        return "Invalid input: Latitude and Longitude must be numbers."
