import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

BOOK_URLS = [
    "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
    "http://books.toscrape.com/catalogue/soumission_998/index.html",
]

CSV_HEADERS = ["Timestamp", "Title", "Price", "Availability", "URL"]

def ensure_csv_headers(file_path="price_history.csv"):
    """
    Ensures the CSV file exists with the correct headers.
    If the file does not exist, it creates it and writes the headers.
    """
    try:
        with open(file_path, 'x', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
            print(f"Created '{file_path}' with headers.")
    except FileExistsError:
        # File already exists, no need to do anything
        pass
    except IOError as e:
        print(f"Error ensuring CSV headers in '{file_path}': {e}")

def append_to_csv(data, file_path="price_history.csv"):
    """
    Appends a new row of data to the CSV file.
    """
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerow(data)
            print(f"Appended data for '{data.get("Title", "N/A")}' to '{file_path}'.")
    except IOError as e:
        print(f"Error appending data to '{file_path}': {e}")

def scrape_book_data(url):
    """
    Scrapes the title, price, and availability from a given book URL.
    Returns a dictionary with the scraped data, or None if an error occurs.
    """
    print(f"Attempting to scrape: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    scraped_data = {"Title": "N/A", "Price": "N/A", "Availability": "N/A", "URL": url}

    try:
        # Title
        title_tag = soup.find('h1')
        if title_tag:
            scraped_data["Title"] = title_tag.get_text(strip=True)

        # Price
        price_tag = soup.find('p', class_='price_color')
        if price_tag:
            price_string = price_tag.get_text(strip=True)
            # Clean the price string (remove currency symbols and convert to float)
            clean_price = float(''.join(filter(str.isdigit or str == '.', price_string)))
            scraped_data["Price"] = f"{clean_price:.2f}"

        # Availability
        availability_tag = soup.find('p', class_='instock availability')
        if availability_tag:
            availability_string = availability_tag.get_text(strip=True)
            scraped_data["Availability"] = availability_string

    except (AttributeError, ValueError) as e:
        print(f"Error parsing content from {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while parsing {url}: {e}")
        return None
    
    return scraped_data

def track_prices():
    """
    Main function to track prices for a list of book URLs and store them in a CSV.
    """
    ensure_csv_headers()

    for url in BOOK_URLS:
        scraped_data = scrape_book_data(url)
        if scraped_data:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            scraped_data["Timestamp"] = timestamp
            append_to_csv(scraped_data)
        time.sleep(1)  # Be polite and wait 1 second between requests

if __name__ == "__main__":
    track_prices()
