import asyncio
import aiohttp
import json
import pandas as pd
from aiohttp import ClientSession
from itertools import cycle

async def fetch_info(session, lat, lon, row_index, username, retries=3):
    url = f"http://api.geonames.org/findNearbyPlaceNameJSON?lat={lat}&lng={lon}&username={username}"
    for _ in range(retries):
        try:
            async with session.get(url) as response:
                data = await response.json()
                if data.get("geonames"):
                    info = data['geonames'][0]
                    print(f"Row {row_index}: Successfully fetched data for {lat}, {lon} using {username}")
                    return {
                        'City': info.get('name'),
                        'Province/State': info.get('adminName1'),
                        'Country': info.get('countryName'),
                        'Country Code': info.get('countryCode')
                        # Add more fields as needed
                    }
                else:
                    print(f"Row {row_index}: No data for {lat}, {lon} using {username}")
                    return None
        except:
            print(f"Row {row_index}: Failed to fetch data for {lat}, {lon} using {username}, retrying...")
    return None

async def main():
    usernames = ['wirrie', 'wirrie1', 'wirrie2', 'wirrie3', 'wirrie4', 'wirrie5', 'wirrie6']
    usernames_cycle = cycle(usernames)

    # Read CSV
    df = pd.read_csv("ihg_hotels_details.csv")
    tasks = []
    async with ClientSession() as session:
        for row_index, row in df.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            username = next(usernames_cycle)
            task = fetch_info(session, lat, lon, row_index, username)
            tasks.append(task)
        
        # Limit max concurrent tasks
        sem = asyncio.Semaphore(25)
        async def bound_fetch(sem, session, lat, lon, row_index, username):
            async with sem:
                return await fetch_info(session, lat, lon, row_index, username)
        
        results = await asyncio.gather(*(bound_fetch(sem, session, row['Latitude'], row['Longitude'], row_index, next(usernames_cycle)) for row_index, row in df.iterrows()))
        
        # Update DataFrame
        new_cols = ['City', 'Province/State', 'Country', 'Country Code']
        for col in new_cols:
            df[col] = None

        for i, result in enumerate(results):
            if result:
                for col, val in result.items():
                    df.at[i, col] = val
        
        # Save updated CSV
        df.to_csv("ihg_hotels_details.csv", index=False)

# Run the program
if __name__ == "__main__":
    asyncio.run(main())