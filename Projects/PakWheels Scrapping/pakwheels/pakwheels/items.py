# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PakwheelsItem(scrapy.Item):
    # define the fields for your item here like:
    description_text = scrapy.Field()
    price = scrapy.Field()
    model = scrapy.Field()
    kms_ran = scrapy.Field()
    engine_power = scrapy.Field()
    transmission = scrapy.Field()
    image_link = scrapy.Field()


    pass
