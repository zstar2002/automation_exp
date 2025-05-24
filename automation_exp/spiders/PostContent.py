import scrapy
import csv
import os
import chardet
from automation_exp.items import AutomationExpItem


class PostcontentSpider(scrapy.Spider):
    name = "PostContent"
    allowed_domains = ["www.teslaownersonline.com"]
    start_urls = ["https://www.teslaownersonline.com"]

    def start_requests(self):
        try:
            urls = []
            # Construct the absolute path to the CSV file
            csv_file_path = os.path.join(os.path.dirname(__file__), 'thread_urls.csv')
            
            # Detect the encoding of the CSV file
            with open(csv_file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
            
            # Read the CSV file with the detected encoding
            with open(csv_file_path, 'r', encoding=encoding) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    thread = {}
                    thread['thread_title'] = row['thread_title']
                    thread['thread_link'] = row['thread_link']
                    urls.append(thread)
                    self.logger.debug(f"Obtained URL: {thread['thread_link']} from CSV")
            for url in urls:
                yield scrapy.Request(url=url['thread_link'], callback=self.parse, meta=url)
        
        except Exception as e:
                    self.logger.error(f"Error while obtaining start requests: {e}")
     
            
    def parse(self, response):
        # Log the URL being processed
        self.logger.debug(f"Processing URL: {response.url}")
        posts = response.css('div.MessageCard')  # Adjust the selector based on the actual HTML structure
        for post in posts:
            post_item = AutomationExpItem()
            
            post_item['author_id'] = post.css(' a.MessageCard__user-info__name::attr(data-user-id)').get()
            post_item['date'] = post.css('a.MessageCard__date-created > time.u-dt::attr(datetime)').get()
            post_item['position'] = post.css(' a.MessageCard__post-position::text').get()
            post_item['text'] = post.css(' div.bbWrapper').get()  # Extract the inner content of the div.bbWrapper element
            post_item['thread_title'] = response.meta['thread_title']
            post_item['thread_link'] = response.meta['thread_link']               
            
            yield post_item
        
        # Follow pagination link
        next_page = response.css('div.block-outer-opposite').css(' a.pageNav-jump.pageNav-jump--next.button.button--icon-only::attr(href)').get()
        if next_page:
            next_page_url ='https://www.teslaownersonline.com' + next_page
            self.logger.debug("Go into the next page: %s" % next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse, meta=response.meta)
        else:
            self.logger.debug("No next page found")
