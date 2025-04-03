from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import re
import os


def scrape_idealista_properties(url, max_pages=5):
    """
    Scrape commercial property listings from idealista.it

    Args:
        url (str): URL of the search results page
        max_pages (int): Maximum number of pages to scrape

    Returns:
        pd.DataFrame: DataFrame containing property information
    """
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Add user-agent to avoid detection as a bot
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    # Initialize the webdriver
    driver = webdriver.Chrome(options=chrome_options)

    properties = []
    current_page = 1

    try:
        # Open the initial URL
        driver.get(url)

        # Accept cookies if the dialog appears
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            ).click()
            print("Accepted cookies")
        except (TimeoutException, NoSuchElementException):
            print("Cookie dialog not found or already accepted")

        while current_page <= max_pages:
            print(f"Scraping page {current_page}")

            # Wait for the property listings to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "items-container"))
            )

            # Get all property listings on the current page
            property_elements = driver.find_elements(By.CLASS_NAME, "item")

            for prop in property_elements:
                try:
                    # Extract property information
                    property_data = {}

                    # Title
                    try:
                        property_data["title"] = prop.find_element(By.CLASS_NAME, "item-link").text.strip()
                    except NoSuchElementException:
                        property_data["title"] = "N/A"

                    # Price
                    try:
                        price_text = prop.find_element(By.CLASS_NAME, "item-price").text.strip()
                        # Extract just the numeric price
                        price_match = re.search(r'(\d+\.?\d*)', price_text.replace(".", ""))
                        property_data["price"] = price_match.group(1) if price_match else price_text
                    except NoSuchElementException:
                        property_data["price"] = "N/A"

                    # Size
                    try:
                        size_element = prop.find_element(By.CSS_SELECTOR, "[data-testid='item-size']")
                        property_data["size"] = size_element.text.strip()
                    except NoSuchElementException:
                        property_data["size"] = "N/A"

                    # Location
                    try:
                        property_data["location"] = prop.find_element(By.CLASS_NAME,
                                                                      "item-detail-location").text.strip()
                    except NoSuchElementException:
                        property_data["location"] = "N/A"

                    # Description
                    try:
                        property_data["description"] = prop.find_element(By.CLASS_NAME, "item-description").text.strip()
                    except NoSuchElementException:
                        property_data["description"] = "N/A"

                    # Property URL
                    try:
                        property_data["url"] = prop.find_element(By.CLASS_NAME, "item-link").get_attribute("href")
                    except NoSuchElementException:
                        property_data["url"] = "N/A"

                    # Photo URL (if available)
                    try:
                        img_element = prop.find_element(By.CSS_SELECTOR, ".gallery-fallback > img")
                        property_data["photo_url"] = img_element.get_attribute("src")
                    except NoSuchElementException:
                        property_data["photo_url"] = "N/A"

                    properties.append(property_data)
                except Exception as e:
                    print(f"Error extracting property details: {e}")

            # Check if there's a next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.icon-arrow-right-after")
                if "disabled" in next_button.get_attribute("class"):
                    print("Reached the last page")
                    break

                # Go to next page
                next_button.click()
                current_page += 1

                # Wait to avoid being detected as a bot
                time.sleep(3)
            except NoSuchElementException:
                print("No more pages found")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    # Create DataFrame from the collected data
    df = pd.DataFrame(properties)
    return df


def save_results(df, output_file="idealista_properties.csv"):
    """
    Save the scraped results to a CSV file

    Args:
        df (pd.DataFrame): DataFrame containing property information
        output_file (str): Name of the output file
    """
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Results saved to {output_file}")

    # Also save as Excel if pandas has openpyxl
    try:
        excel_file = output_file.replace('.csv', '.xlsx')
        df.to_excel(excel_file, index=False)
        print(f"Results also saved to {excel_file}")
    except Exception as e:
        print(f"Could not save as Excel: {e}")


if __name__ == "__main__":
    # URL for commercial spaces (negozi) for rent in Rome
    url = "https://www.idealista.it/affitto-negozi/roma-roma/"

    # Scrape the data
    properties_df = scrape_idealista_properties(url, max_pages=5=)

    # Print summary
    print(f"\nScraped {len(properties_df)} properties")
    if not properties_df.empty:
        print("\nSample data:")
        print(properties_df[["title", "price", "size", "location"]].head())

    # Save results
    save_results(properties_df)