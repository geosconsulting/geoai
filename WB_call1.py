import requests
import json # Optional: for pretty printing the response

# --- Configuration ---
BASE_URL = "http://api.worldbank.org/v2"
INDICATOR = "SP.POP.TOTL"  # Total Population
# Use ISO 3166-1 alpha-2 codes (e.g., US, CA, GB, DE, CN, IN, BR)
# Use 'all' for all countries (be careful, can be large!)
COUNTRIES = "US;CA;MX"
DATE_RANGE = "2018:2020"
# Other params
PARAMS = {
    "format": "json",   # Request JSON format
    "date": DATE_RANGE,
    "per_page": 100     # Adjust if expecting more data points per page
}

# --- Construct the Request URL ---
# Example: http://api.worldbank.org/v2/country/US;CA;MX/indicator/SP.POP.TOTL?format=json&date=2018:2020
request_url = f"{BASE_URL}/country/{COUNTRIES}/indicator/{INDICATOR}"

print(f"Requesting URL: {request_url}")
print(f"With Params: {PARAMS}")

# --- Make the API Request ---
try:
    response = requests.get(request_url, params=PARAMS)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

    # --- Process the Response ---
    data = response.json()

    # The World Bank API often returns a list where:
    # data[0] is pagination/metadata
    # data[1] is the actual list of data points

    if not data or len(data) < 2 or not data[1]:
        print("No data received or data format is unexpected.")
        # print("Full response:", json.dumps(data, indent=2)) # Uncomment to see raw response
    else:
        metadata = data[0]
        data_list = data[1]

        print("\n--- Metadata ---")
        print(f"Page: {metadata.get('page')}")
        print(f"Pages: {metadata.get('pages')}")
        print(f"Per Page: {metadata.get('per_page')}")
        print(f"Total Records: {metadata.get('total')}")

        print("\n--- Data ---")
        for item in data_list:
            country_name = item.get('country', {}).get('value', 'N/A')
            country_iso = item.get('countryiso3code', 'N/A')
            year = item.get('date', 'N/A')
            value = item.get('value', 'N/A')
            indicator_name = item.get('indicator', {}).get('value', 'N/A')

            # Handle potential None values for population before formatting
            population_str = f"{value:,}" if value is not None else "N/A"

            print(f"Country: {country_name} ({country_iso}), Year: {year}, Population: {population_str}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred during the API request: {e}")
except json.JSONDecodeError:
    print("Failed to decode JSON response. Response text:")
    print(response.text)
except IndexError:
    print("Received data format does not match expected structure (list with metadata and data).")
    print("Full response:", json.dumps(data, indent=2)) # Print the actual structure received
except Exception as e:
    print(f"An unexpected error occurred: {e}")