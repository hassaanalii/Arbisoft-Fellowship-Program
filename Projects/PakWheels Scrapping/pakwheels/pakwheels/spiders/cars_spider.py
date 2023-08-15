import scrapy
from ..items import PakwheelsItem
import os
import time
import shutil
import math
import re

class CarSpider(scrapy.Spider):
    name = "cars"  
    allowed_pages_to_scrap = 0
    number_of_items = 0
    page_number = 1
    cities = [
        {"city_name": 'rawalpindi', "city_code": "24831"},
        {"city_name": 'lahore', "city_code": "24858"},
        {"city_name": 'karachi', "city_code": "24857"},
        {"city_name": 'islamabad', "city_code": "24856"},
        {"city_name": 'peshawar', "city_code": "24821"},
        {"city_name": 'faisalabad', "city_code": "24753"},
        {"city_name": 'multan', "city_code": "24810"},
        {"city_name": 'gujranwala', "city_code": "24763"}
    ]
    # Remove the existing 'filestore' directory and create a new one
    try:
        shutil.rmtree('./filestore')
        print("Removing existing 'filestore' directory.")
    except OSError:
        pass

    time.sleep(0.5)

    try:
        os.makedirs('./filestore')
        print("Creating a new 'filestore' directory.")
    except OSError:
        pass


    def selective_city(self):
        print("1. Rawalpindi\n2. Lahore\n3. Karachi\n4. Islamabad\n5. Peshawar\n6. Faisalabad\n7. Multan\n8. Gujranwala")
        input_city = int(input("\nWhich city's data do you want?"))

        city = self.cities[input_city - 1]
        self.number_of_items = int(input("\nHow many items do you want?"))
        self.allowed_pages_to_scrap = math.ceil(self.number_of_items / 40)
        start_url = f'https://www.pakwheels.com/used-cars/{city["city_name"]}/{city["city_code"]}?page={self.page_number}'
        yield scrapy.Request(start_url, self.parse, cb_kwargs={'city_name': city["city_name"], 'city_code': city["city_code"]})


    def start_requests(self):
        print("Select an option:")
        print("1. Extract data for all cities")
        print("2. Extract data for a specific city")

        choice = int(input("Enter your choice: "))

        if choice == 1:
            num_pages = int(input("Enter the number of pages to scrape: "))  # User input
            for city in self.cities:
                start_url = f'https://www.pakwheels.com/used-cars/{city["city_name"]}/{city["city_code"]}?page={self.page_number}'
                yield scrapy.Request(start_url, self.parse, cb_kwargs={'city_name': city["city_name"], 'city_code': city["city_code"], 'num_pages': num_pages})
        elif choice == 2:
            yield from self.selective_city()
        else:
            print("Invalid choice. Please select 1 or 2.")


   
    def parse(self, response, city_name, city_code, num_pages = None):
        self.page_number = 1
        items = PakwheelsItem()

        car = response.css("div.search-title-row")
        car_description = car.css(".ad-detail-path h3::text").extract()
        car_price = response.css(".price-details::text").extract()
        cleaned_prices = []

        price_pattern = re.compile(r'PKR\s*([\d.]+)')
        call_pattern = re.compile(r'call', re.IGNORECASE)  # Case-insensitive match for "call"

        for raw_price in car_price:
            match = price_pattern.search(raw_price)
            if match:
                cleaned_price = float(match.group(1))
                cleaned_prices.append(cleaned_price)
            else:
                call_match = call_pattern.search(raw_price)
                if call_match:
                    cleaned_prices.append("call")

        model = response.css(".search-vehicle-info-2 li:nth-child(1)::text").extract()
        kms_ran = response.css(".fs13 li:nth-child(2)::text").extract()
        engine_power = response.css(".fs13 li:nth-child(4)::text").extract()
        transmission = response.css(".fs13 li:nth-child(5)::text").extract()
        image_link = response.css(".pic::attr(src)").extract()
        location = response.css(".search-vehicle-info li::text").extract()

        for image_url in image_link:
            yield response.follow(
                url=image_url,
                callback=self.scrape_image
            )

        if num_pages is None:
            items_to_extract = min(self.number_of_items, len(car_description))
        else:
            items_to_extract = len(car_description)
        
        for i in range(items_to_extract):
            items['description_text'] = car_description[i]
            items['price'] = cleaned_prices[i]
            items['location'] = location[i]
            items['model'] = model[i]
            items['kms_ran'] = kms_ran[i]
            items['engine_power'] = engine_power[i]
            items['transmission'] = transmission[i]
            items['image_link'] = image_link[i]
            
            yield items

        if num_pages is None:
            if len(car_description) < self.number_of_items:
                self.number_of_items = self.number_of_items - len(car_description)
            
            self.page_number += 1
            next_page = f'https://www.pakwheels.com/used-cars/{city_name}/{city_code}?page={self.page_number}'

            if self.page_number <= self.allowed_pages_to_scrap:
                yield response.follow(next_page, callback=self.parse, cb_kwargs={'city_name': city_name, 'city_code' : city_code})
        else:
            self.page_number += 1
            next_page = f'https://www.pakwheels.com/used-cars/{city_name}/{city_code}?page={self.page_number}'

            if self.page_number <= num_pages:
                yield response.follow(next_page, callback=self.parse, cb_kwargs={'city_name': city_name, 'city_code' : city_code, 'num_pages' : num_pages})

    def scrape_image(self, response):
        file_name = response.url.split("?")[0].split("/")[-1]
        with open("filestore/" + file_name, 'wb') as f:
            f.write(response.body)




   