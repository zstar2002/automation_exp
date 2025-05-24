# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AutomationExpItem(scrapy.Item):
    # define the fields for your item here like:
    author_id = scrapy.Field()
    date = scrapy.Field()
    position = scrapy.Field()
    text = scrapy.Field()
    thread_title = scrapy.Field()
    thread_link = scrapy.Field()
    
    pass
