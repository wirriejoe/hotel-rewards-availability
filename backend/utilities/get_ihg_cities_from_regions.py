import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

# Function to scrape IHG page and return a list of URLs within the specified element
def scrape_ihg_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        container = soup.find('div', {'class': 'countryListingContainer col-xs-12'})
        links = [a['href'] for a in container.find_all('a', href=True)]
        return links
    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return []

# Function to process a single URL
def process_url(i, url):
    print(f"Processing URL {i + 1} of {len(urls_to_scrape)}: {url}")
    links = scrape_ihg_page(url)
    if links:
        print(f"Successfully scraped {len(links)} links from {url}")
    else:
        print(f"Failed to scrape links from {url}")
        links = [url]  # Return URL as link on failure

    return [(link, url) for link in links]  # Return as list of tuples

# Read the URLs to scrape from the CSV file
urls_to_scrape = pd.read_csv("ihg_regions.csv", header=None)[0].tolist()

# Initialize variables for tracking
scraped_links = []
failed_count = 0
start_time = time.time()  # Record the start time

# Using ThreadPoolExecutor to parallelize the scraping, limit to 5 threads
with ThreadPoolExecutor(max_workers=20) as executor:
    future_to_url = {executor.submit(process_url, i, url): url for i, url in enumerate(urls_to_scrape)}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            link_tuples = future.result()
            scraped_links.extend(link_tuples)
        except Exception as e:
            print(f"An error occurred: {e}")
            failed_count += 1

# Measure the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time

# Write the scraped links to a new CSV file
with open('ihg_cities.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Link", "Region URL"])
    for link, region_url in scraped_links:
        writer.writerow([link, region_url])

# Print summary information
print(f"Scraping completed in {elapsed_time:.2f} seconds.")
print(f"Total URLs processed: {len(urls_to_scrape)}")
print(f"Total failed: {failed_count}")