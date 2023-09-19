import csv
import openai
import openai.error
import json
import asyncio
import aiohttp
from aiohttp import ClientSession
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

# Function to process a chunk of addresses using the OpenAI API
async def process_chunk(session, address_chunk, headers, max_retries=5):
    print(f"Processing a chunk of {len(address_chunk)} addresses...")

    messages = [
        {"role": "system", "content": """Your responses must this exact JSON format. If there's no value, return "" for the field. Here's an example:
        [
            {
                "hotel_address": "Av Leandro N. Alem 770",
                "hotel_city": "Puerto Madero",
                "hotel_province": "Buenos Aires",
                "hotel_zipcode": "1001",
                "hotel_country": "Argentina"
            },
            {
                "hotel_address": "28 Spring St, Bondi Junction 2022",       
                "hotel_city": "Bondi Junction",
                "hotel_province": "",
                "hotel_zipcode": "2022",
                "hotel_country": "Australia"
            }
         ]
         """}
    ]
    messages.append(
        {"role": "user", "content": "Extract details from this list of hotel addresses:\n" + '\n'.join([row['Hotel Address'] for row in address_chunk])}
    )
    
    retries = 0
    while retries <= max_retries:
        try:
            print(f"Making API call for chunk...")
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo-0613",
                messages=messages
            )

            details_list = json.loads(response['choices'][0]['message']['content'])
            print(f"Successfully received API response for chunk.")
            print(details_list)

            for i, details in enumerate(details_list):
                for key in details.keys():
                    if key in headers:  # check if key is in CSV headers before updating
                        address_chunk[i][key] = details[key]
                    else:
                        print(f"Warning: Key {key} not found in CSV columns.")
                        
            return address_chunk  # Return the updated chunk

        except openai.error.ServiceUnavailableError as e:
            print(f"Server is overloaded or not ready yet. Retrying... ({retries + 1})")
            retries += 1
            await asyncio.sleep(2)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"An error occurred: {e}")
            retries += 1
            await asyncio.sleep(2)
        except asyncio.TimeoutError:
            print("Request timed out. Retrying...")
            retries += 1
            await asyncio.sleep(2)
        except IndexError as e:
            print(f"Out of index: {e}")
            retries += 1
            await asyncio.sleep(2)

async def main():
    openai.api_key = os.getenv('OPENAI_KEY')
    openai.aiosession.set(ClientSession())

    with open("ihg_hotels_details.csv", "r") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    headers = list(rows[0].keys())
    headers += ['hotel_address', 'hotel_city', 'hotel_province', 'hotel_zipcode', 'hotel_country']
    final_rows = []

    async with ClientSession() as session:
        tasks = []
        for i in range(0, len(rows), 25):
            chunk = rows[i:i + 25]
            task = process_chunk(session, chunk, headers)
            tasks.append(task)
            
            if len(tasks) >= 25:
                print(f"Reached 25 tasks, processing...")
                results = await asyncio.gather(*tasks)
                final_rows.extend([row for result in results for row in result])  # Update the final_rows list
                tasks = []

        if tasks:
            print("Processing remaining tasks...")
            results = await asyncio.gather(*tasks)
            final_rows.extend([row for result in results for row in result])

    print("Writing updated rows to new CSV file...")
    with open("ihg_hotels_final.csv", "w", newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        for row in final_rows:
            writer.writerow(row)
    
    await openai.aiosession.get().close()

if __name__ == "__main__":
    asyncio.run(main())