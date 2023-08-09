import scrapy
from ..items import PakwheelsItem

class CarSpider(scrapy.Spider):
    name = "cars"
    allowed_pages_to_scrap = int(input("Enter the number of pages to scrape: "))  # User input
    page_number = 1
    start_urls = [
        f'https://www.pakwheels.com/used-cars/rawalpindi/24831?page={page_number}'
    ]
    def parse(self, response):
        items = PakwheelsItem()

        car = response.css("div.search-title-row")
        car_description = car.css(".ad-detail-path h3::text").extract()
        car_price = response.css(".generic-dark-grey::text").extract()
        cleaned_prices = [price.strip() for price in car_price if price.strip().startswith("PKR")]
        model = response.css(".search-vehicle-info-2 li:nth-child(1)::text").extract()
        kms_ran = response.css(".fs13 li:nth-child(2)::text").extract()
        engine_power = response.css(".fs13 li:nth-child(4)::text").extract()
        transmission = response.css(".fs13 li:nth-child(5)::text").extract()
        image_link = response.css(".pic::attr(src)").extract()

        for i in range (len(car_description)):
            items['description_text'] = car_description[i]
            items['price'] = cleaned_prices[i]
            items['model'] = model[i]
            items['kms_ran'] = kms_ran[i]
            items['engine_power'] = engine_power[i]
            items['transmission'] = transmission[i]
            items['image_link'] = image_link[i]

            yield items

        CarSpider.page_number += 1 
        next_page = f'https://www.pakwheels.com/used-cars/rawalpindi/24831?page={CarSpider.page_number}'

        if next_page is not None and CarSpider.page_number <= CarSpider.allowed_pages_to_scrap:
            yield response.follow(next_page, callback = self.parse)

