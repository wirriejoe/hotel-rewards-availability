import re
import csv
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, parse_qs

sem = asyncio.Semaphore(250)  # Limit to 50 concurrent coroutines

async def check_full_list(url, index, total, session, max_retries=3):
    """Check if the page contains the full list of hotels and extract data."""
    async with sem:  # Semaphore limiting
        retries = 0
        while retries <= max_retries:
            try:
                async with session.get(url) as response:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')

                    hotel_entries = soup.find_all(id=re.compile('hotelID-'))

                    print(f"Processing region {index+1} of {total}. Found {len(hotel_entries)} hotels. URL: {url}")

                    hotels_metadata = []
                    for entry in hotel_entries:
                        hotel_code = entry['id'].split('-')[-1]
                        hotel_name_tag = soup.find(id=f"hotelDetailNameLink-{hotel_code}")
                        hotel_name = hotel_name_tag.text.strip() if hotel_name_tag else ''
                        hotel_url = hotel_name_tag['href'] if hotel_name_tag else ''
                        
                        path_parts = urlparse(hotel_url).path.strip("/").split("/")
                        hotel_destination_code = path_parts[-3]

                        address_section = soup.find(id=f"address-Section-{hotel_code}")
                        hotel_address = " ".join([div.text.strip() for div in address_section.find_all('div')]) if address_section else ''
                        
                        hotels_metadata.append([url, hotel_code, hotel_destination_code, hotel_name, hotel_url, hotel_address])

                    return hotels_metadata

            except Exception as e:
                print(f"An error occurred while checking {url}: {e}. Retrying {retries+1}/{max_retries}")
                retries += 1
                await asyncio.sleep(1)
    
        print(f"Max retries reached for {url}. Skipping.")
        return [[url, '', '', '', '', '']]

async def main():
    city_urls = pd.read_csv("ihg_cities.csv")['Link'].tolist()
    all_hotels_data = []
    total_regions = len(city_urls)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, url in enumerate(city_urls):
            task = asyncio.ensure_future(check_full_list(url, index, total_regions, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)

        for response in responses:
            all_hotels_data.extend(response)
    
    unique_hotels_data = list(set(tuple(row) for row in all_hotels_data))
    unique_hotels_data = [list(tup) for tup in unique_hotels_data]

    with open('ihg_hotels_metadata.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Region URL", "Hotel Code", "Destination Code", "Hotel Name", "Hotel URL", "Hotel Address"])
        for row in all_hotels_data:
            writer.writerow(row)
    print("Data extraction completed. Results written to 'ihg_hotels_metadata.csv'.")

if __name__ == '__main__':
    asyncio.run(main())