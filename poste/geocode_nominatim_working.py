import time
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Photon
geolocator = Photon(user_agent="measurements")


# # Global variable to store addresses
# addresses = []
#
# # # Function to read file and create a list of addresses
# # def get_addresses_from_file(filepath):
# #     with open(filepath, "r", encoding="utf-8") as file:
# #         addresses = [line.strip() for line in file if line.strip()]
# #     return addresses
#
# # Function to read file and create a list of addresses
# def get_addresses_from_file(filepath):
#     global addresses  # Ensure we modify the global variable
#     with open(filepath, "r", encoding="utf-8") as file:
#         addresses = [line.strip() for line in file if line.strip()]


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
    """Geocode a list of addresses and return a GeoDataFrame."""
    geolocator = Nominatim(user_agent="geo_app1")

    results = []
    for address in addresses:
        lat, lon = geocode_address(geolocator, address)
        print(f"{address}: {lat}, {lon}")
        results.append((address, lat, lon))
        time.sleep(1)  # Respect Nominatim's rate limits

    df = pd.DataFrame(results, columns=["Address", "Latitude", "Longitude"])
    df = df.dropna()
    df["geometry"] = df.apply(lambda row: Point(row["Longitude"], row["Latitude"]), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    return gdf


def plot_geocoded_points(gdf):
    """Plot geocoded points using GeoPandas."""
    gdf.plot(marker='o', color='red', alpha=0.6, figsize=(10, 6))
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geocoded Addresses")
    plt.grid()
    plt.show()


# # Run in Jupyter Notebook
# if __name__ == "__main__":
#     addresses = ["1600 Amphitheatre Parkway, Mountain View, CA",
#                  "221B Baker Street, London",
#                  "Eiffel Tower, Paris"]  # Input addresses here
#     gdf = geocode_addresses(addresses)
#     # display(gdf)  # Display GeoDataFrame in Jupyter Notebook
#     plot_geocoded_points(gdf)
