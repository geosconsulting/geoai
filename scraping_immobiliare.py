from bs4 import BeautifulSoup
import requests
import random
import time

# User-Agent rotation (to avoid detection)
headers_list = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"},
]

# Define search URL (Example: Milan apartments)
url = "https://www.immobiliare.it/vendita-case/milano/"

# Make request with random headers
response = requests.get(url, headers=random.choice(headers_list))

# Check response
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract listings
    listings = soup.find_all("li", class_="nd-list__item")  # Adjust this class based on the website's structure

    for listing in listings:
        title = listing.find("a", class_="in-card__title").text.strip()
        price = listing.find("span", class_="nd-list__item-price").text.strip()
        size = listing.find("span", class_="in-feat__item in-feat__item--surface").text.strip() if listing.find("span", class_="in-feat__item in-feat__item--surface") else "N/A"

        print(f"Title: {title}\nPrice: {price}\nSize: {size}\n{'-'*40}")

else:
    print("Failed to retrieve the page. Status code:", response.status_code)