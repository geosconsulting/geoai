import time
import pandas as pd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def geocode_address(geolocator, address, retries=3):
    """Geocode an address using Nominatim API with retries."""
    for _ in range(retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return location.latitude, location.longitude
        except GeocoderTimedOut:
            time.sleep(2)  # Wait before retrying
    return None, None


def geocode_addresses(addresses):
    """Geocode a list of addresses and return a DataFrame."""
    geolocator = Nominatim(user_agent="geo_app")

    results = []
    for address in addresses:
        lat, lon = geocode_address(geolocator, address)
        print(f"{address}: {lat}, {lon}")
        results.append((address, lat, lon))
        time.sleep(1)  # Respect Nominatim's rate limits

    df = pd.DataFrame(results, columns=["Address", "Latitude", "Longitude"])
    return df


def plot_geocoded_points(df):
    """Plot geocoded points on a scatter plot."""
    df = df.dropna()
    plt.figure(figsize=(10, 6))
    plt.scatter(df["Longitude"], df["Latitude"], c='red', marker='o', alpha=0.6)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geocoded Addresses")
    plt.grid()
    plt.show()


# Run in Jupyter Notebook
if __name__ == "__main__":
    addresses = ["1600 Amphitheatre Parkway, Mountain View, CA",
                 "221B Baker Street, London",
                 "Eiffel Tower, Paris"]  # Input addresses here
    df = geocode_addresses(addresses)
    # display(df)  # Display DataFrame in Jupyter Notebook
    plot_geocoded_points(df)
