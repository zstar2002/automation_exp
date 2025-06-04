import scrapy
import csv
import os
import chardet
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from automation_exp.items import AutomationExpItem
import time
import random
import re

def extract_position_and_date(tail_infos):
    raise NotImplementedError

class TiebaContentSpider(scrapy.Spider):
    name = "tieba_content_spider"
    allowed_domains = ["tieba.baidu.com"]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://tieba.baidu.com/'
        },
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'FEED_EXPORT_ENCODING': 'utf-8',
        'ITEM_PIPELINES': {
            'automation_exp.pipelines.tieba_content_pipeline.TiebaContentPipeline': 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument('--log-level=3')
        # chrome_options.add_argument("--headless")
        try:
            driver_path = r"C:\Users\maste\.wdm\drivers\chromedriver\win64\chromedriver-win64\chromedriver.exe"
            self.driver = webdriver.Chrome(
                service=Service(driver_path),
                options=chrome_options
            )
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise

    def find_latest_csv(self):
        """Find the newest CSV file in automation_exp_output starting with 'tieba_forum_threads_'."""
        # Get the current script directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Navigate to project root (3 levels up from spiders folder)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        
        # Path to output directory
        output_dir = os.path.join(project_root, 'automation_exp_output')
        
         # Pattern to match CSV files
        pattern = os.path.join(output_dir, 'tieba_forum_threads_*.csv')
        
        # Find matching files
        files = glob.glob(pattern)        
        if not files:
            raise FileNotFoundError(f"No CSV files starting with 'tieba_forum_threads_' found in {output_dir}")
        
        # Return the most recently modified file
        latest_file = max(files, key=os.path.getmtime)
        self.logger.info(f"Found latest CSV file: {latest_file}")
        return latest_file
    
    def extract_position_and_date(tail_infos):
        """Given a list of span.tail-info texts, return (position, date) based on their format."""
        position = None
        date = None
        date_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
        for info in tail_infos:
            if info.endswith("楼"):
                position = info
            elif date_pattern.match(info):
                date = info
        return position, date

    def start_requests(self):
        try:
            urls = []
            # Find the latest CSV file
            csv_file_path = self.find_latest_csv()
            self.logger.info(f"Using CSV file: {csv_file_path}")
            
            # Detect the encoding of the CSV file
            with open(csv_file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
            
            # Ensure encoding is compatible with Chinese characters  
            if encoding.lower() not in ['utf-8', 'utf-16', 'gbk']:
                self.logger.debug(f"Detected encoding {encoding} may not support Chinese characters. Defaulting to UTF-8.")
                encoding = 'utf-8'
                
            # Read the CSV file with the detected encoding   
            with open(csv_file_path, 'r', encoding=encoding) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    thread = {}
                    # Use the correct column names based on the CSV file structure
                    thread['thread_title'] = row.get('thread_title')
                    thread['thread_link'] = row.get('thread_link')
                    if thread['thread_title'] and thread['thread_link']:
                        urls.append(thread)
                        self.logger.debug(f"Obtained URL: {thread['thread_link']} from CSV")
                        
            for url in urls:
                yield scrapy.Request(url=url['thread_link'], callback=self.parse, meta=url)
                
                
        except Exception as e:
            self.logger.debug(f"Error while obtaining start requests: {e}")

    def parse(self, response):
        """Parse individual posts. Currently only got the 1st place of the thread."""
        # Log the URL being processed
        self.logger.debug(f"Processing URL: {response.url}")
        self.driver.get(response.url)
        
        try:
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.p_postlist"))
            )
            self.logger.debug("Successfully found the post list element")
        except WebDriverException as e:
            self.logger.error(f"Error loading page with Selenium: {e}")
            return
        while True:
            selenium_response = scrapy.http.HtmlResponse(
                url=self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8'
            )
            posts = selenium_response.css('div.p_postlist > div.l_post')
            for post in posts:
                item = AutomationExpItem()
                item['author_id'] = post.css('a.p_author_name::text').get()
                
                tail_infos = post.css('span.tail-info::text').getall()
                position, date = extract_position_and_date(tail_infos)
                item['date'] = date
                item['position'] = position
                
                item['text'] = post.css('div.d_post_content').xpath('string(.)').get()
                item['thread_title'] = response.meta['thread_title']
                item['thread_link'] = response.meta['thread_link']
                yield item
            # Pagination
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, 'a.pager_next')
                if 'disabled' in next_button.get_attribute('class'):
                    self.logger.info("Next button found but disabled. Exiting pagination loop.")
                    break
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                self.logger.debug("Clicking the next page button.")
                next_button.click()
                time.sleep(random.uniform(2, 3))
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.find_element(By.CSS_SELECTOR, "div#j_p_postlist")
                )
            except Exception:
                self.logger.info("No more pages to crawl for this thread or failed to paginate. Exiting pagination loop.")
                break

    def closed(self, reason):
        if hasattr(self, 'driver'):
            self.driver.quit()
