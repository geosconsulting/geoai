import requests
import json

BASE_URL = "http://api.worldbank.org/v2"
ENDPOINT = "countries" # Could also be 'indicators', 'topics', etc.
PARAMS = {
    "format": "json",
    "per_page": 50 # Get the first 50 countries
}

request_url = f"{BASE_URL}/{ENDPOINT}"

print(f"Requesting URL: {request_url}")
print(f"With Params: {PARAMS}")

try:
    response = requests.get(request_url, params=PARAMS)
    response.raise_for_status() # Check for HTTP errors

    data = response.json()

    if not data or len(data) < 2 or not data[1]:
        print("No country data received or format unexpected.")
    else:
        metadata = data[0]
        countries_list = data[1]

        print("\n--- Metadata ---")
        print(f"Page: {metadata.get('page')}")
        print(f"Pages: {metadata.get('pages')}")
        print(f"Total Countries (approx): {metadata.get('total')}") # Note: 'total' might be across all pages

        print("\n--- First few Countries ---")
        for country in countries_list[:10]: # Print first 10 from this page
            name = country.get('name', 'N/A')
            iso2code = country.get('iso2Code', 'N/A')
            region = country.get('region', {}).get('value', 'N/A')
            income_level = country.get('incomeLevel', {}).get('value', 'N/A')
            print(f"- {name} ({iso2code}), Region: {region}, Income Level: {income_level}")

        # To get ALL countries, you would need to loop through the 'pages'
        # indicated in the metadata, incrementing the 'page' parameter in PARAMS.

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except json.JSONDecodeError:
    print("Failed to decode JSON response.")
    print(response.text)
except Exception as e:
    print(f"An unexpected error occurred: {e}")