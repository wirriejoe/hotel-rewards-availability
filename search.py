import json
from dotenv import load_dotenv
import os
from urllib.parse import urlencode
from selenium_profiles.webdriver import Chrome
from selenium.webdriver.common.by import By  # locate elements
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()  # take environment variables from .env.
profile = json.loads(os.getenv('SELENIUM_PROFILE'))

class AwardSearch:
    def __init__(self, driver):
        self.driver = driver

    def build_url(self, hotel_brand, hotel_code, checkin_date, checkout_date, room_qty = 1, adults = 2, kids = 0):
        base_url_dict = {
            'Hyatt': 'https://www.hyatt.com/shop/service/rooms/roomrates/'
        }
        search_base_url_dict = {
            'Hyatt': 'https://www.hyatt.com/shop/rooms/'
        }
        base_url = base_url_dict[hotel_brand] + hotel_code
        search_base_url = search_base_url_dict[hotel_brand] + hotel_code
        response_url = base_url + f'?spiritCode={hotel_code}&rooms={room_qty}&adults={adults}&checkinDate={checkin_date}&checkoutDate={checkout_date}&kids={kids}'
        search_url = search_base_url + f'?checkinDate={checkin_date}&checkoutDate={checkout_date}&rateFilter=woh'
        print("Response URL" + response_url)
        print("Verification URL: " + search_url)
        return response_url, search_url

    def get_award_stays(self, hotel_brand, hotel_code, checkin_date, checkout_date, room_qty = 1, adults = 2, kids = 0):
        try:
            url, search_url = self.build_url(hotel_brand, hotel_code, checkin_date, checkout_date, room_qty, adults, kids)

            # Get award stays
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 5)
            pre_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))
            json_data = json.loads(pre_element.text)

            room_rates = json_data.get('roomRates', {})  # Using get to avoid KeyError
            awards_list = []

            for room, room_data in room_rates.items():
                if room_data.get('lowestPointValue') is not None:  # Using get to avoid KeyError
                    room_details = {
                        "Room Name": room,
                        "Room Type Code": room_data.get('roomTypeCode'),
                        "Room Category": room_data.get('roomCategory'),
                        "Room Quantity": room_data.get('roomQuantity'),
                        "Lowest Point Value": room_data.get('lowestPointValue'),
                        "Lowest Public Rate": room_data.get('lowestPublicRate'),
                        "Currency Code": room_data.get('currencyCode'),
                        "Search URL": search_url
                    }
                    awards_list.append(room_details)
            
            return awards_list
        except Exception as e:
            print(f"An error occurred while getting award stays: {e}")
            return []

    def quit(self):
        self.driver.quit()


# options = ChromeOptions()
# mydriver = Chrome(profile, options=options, uc_driver=False)
# mydriver.options.add_argument("--headless=new")
# driver = mydriver.start() 

# awardsearch = AwardSearch(driver)

# award_stays = awardsearch.get_award_stays('Hyatt', 'madel', '2023-08-23', '2023-08-24')

# for room_details in award_stays:
#     print(room_details)
            
# awardsearch.quit()