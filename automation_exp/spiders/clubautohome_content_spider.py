import scrapy
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import glob
import chardet
from automation_exp.items import AutomationExpItem

class ClubAutohomeContentSpider(scrapy.Spider):
    name = "clubautohome_content_spider"
    allowed_domains = ["club.autohome.com.cn"]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://club.autohome.com.cn/'
        },
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'FEED_EXPORT_ENCODING': 'utf-8',
        'ITEM_PIPELINES': {
            'automation_exp.pipelines.clubautohome_content_pipeline.ClubautohomeContentPipeline': 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        chrome_options = Options()
        chrome_options.add_argument('--log-level=3')
        # chrome_options.add_argument("--headless")  # Uncomment for headless mode
        try:
            driver_path = r"C:\Users\maste\.wdm\drivers\chromedriver\win64\chromedriver-win64\chromedriver.exe"
            self.driver = webdriver.Chrome(
                service=Service(driver_path),
                options=chrome_options
            )
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise

    def write_to_csv(self, data, file_path):
        """Write data to a CSV file with proper encoding."""
        import csv

        with open(file_path, mode='w', encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    def find_latest_csv(self):
        """Find the newest CSV file in automation_exp_output starting with 'clubautohome_forum_threads_'."""
        # Get the current script directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
    
        # Navigate to project root (3 levels up from spiders folder)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
        # Path to output directory
        output_dir = os.path.join(project_root, 'automation_exp_output')
    
        # Pattern to match CSV files
        pattern = os.path.join(output_dir, 'clubautohome_forum_threads_*.csv')
    
        # Find matching files
        files = glob.glob(pattern)
        if not files:
            raise FileNotFoundError(f"No CSV files starting with 'clubautohome_forum_threads_' found in {output_dir}")
    
        # Return the most recently modified file
        latest_file = max(files, key=os.path.getmtime)
        self.logger.info(f"Found latest CSV file: {latest_file}")
        return latest_file

    def start_requests(self):
        try:
            urls = []
            # Find the latest CSV file
            # The CSV file should be in the 'forum_threads' directory, which is at the same level as the 'spiders' directory.
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
                    thread['thread_title'] = row.get('post_title')
                    thread['thread_link'] = row.get('post_link')
                    thread['thread_date'] = row.get('post_date')
                    if thread['thread_title'] and thread['thread_link']:
                        urls.append(thread)
                        self.logger.debug(f"Obtained URL: {thread['thread_link']} from CSV")

            # Write back to CSV with proper encoding
            # self.write_to_csv(urls, csv_file_path)

            for url in urls:
                yield scrapy.Request(url=url['thread_link'], callback=self.parse, meta=url)
        
        except Exception as e:
            self.logger.debug(f"Error while obtaining start requests: {e}")

    def parse(self, response):
        """Parse individual posts. Currently only got the 1st place of the thread."""
        # Log the URL being processed
        self.logger.debug(f"Processing URL: {response.url}")

        # Use Selenium to load the page and wait for the post container
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.post-container"))
            )
            self.logger.debug("Successfully found the post container element with Selenium")
        except WebDriverException as e:
            self.logger.error(f"Error loading page with Selenium: {e}")
            return

        selenium_response = scrapy.http.HtmlResponse(
            url=response.url,
            body=self.driver.page_source,
            encoding='utf-8'
        )

        post = selenium_response.css('div.post-container')
        if not post:
            self.logger.debug("No posts found with the selector 'div.post-container'")
            return
        
        post_item = AutomationExpItem()
        post_item['author_id'] = selenium_response.css('div.user-name > a.name::text').get()
        post_item['date'] = response.meta['thread_date']
        post_item['position'] = 1
        
        # Extract and concatenate all texts from div.tz-paragraph
        paragraphs = post.css('div.tz-paragraph::text').getall()
        concatenated_text = ''.join([p.strip() for p in paragraphs if p.strip()])
        post_item['text'] = concatenated_text
        
        post_item['thread_title'] = response.meta['thread_title']
        post_item['thread_link'] = response.meta['thread_link']

        # Ensure text content is properly decoded for Chinese characters
        if post_item['text']:
            post_item['text'] = post_item['text'].encode('utf-8').decode('utf-8', errors='ignore')

        # Ensure thread title is properly decoded for Chinese characters
        if post_item['thread_title']:
            post_item['thread_title'] = post_item['thread_title'].encode('utf-8').decode('utf-8', errors='ignore')

        yield post_item
