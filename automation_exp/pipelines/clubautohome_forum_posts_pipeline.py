# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from automation_exp.items import AutomationExpItem
from bs4 import BeautifulSoup
from datetime import datetime

class ClubautohomeForumPostsPipeline:
    def process_item(self, item, spider):
        # ...implement your item processing logic here...
        return item
