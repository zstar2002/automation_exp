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
import time
from scrapy import signals

class ClubAutohomeContentSpider(scrapy.Spider):
    """
    ClubAutohomeContentSpider is a Scrapy spider designed to crawl and extract content from threads and replies on the club.autohome.com.cn forum.
    Features:
    - Reads a list of thread URLs from the latest CSV file in the 'automation_exp_output' directory, supporting automatic encoding detection for Chinese characters.
    - Uses Selenium WebDriver (Chrome) to render JavaScript-heavy pages and ensure all dynamic content is loaded before parsing.
    - Extracts main post and all replies from each thread, yielding a structured item for each post/reply, including author, date, position, text, thread title, and thread link.
    - Handles errors gracefully, including Selenium initialization and page loading issues, with logging and screenshot capture for debugging.
    - Custom Scrapy settings for user agent, request headers, download delay, and pipeline integration.
    - Includes utility methods for writing to CSV and locating the latest input CSV file.
    Args:
        *args: Variable length argument list passed to the Scrapy Spider.
        **kwargs: Arbitrary keyword arguments passed to the Scrapy Spider.
    Raises:
        WebDriverException: If Selenium WebDriver fails to initialize.
        FileNotFoundError: If no suitable CSV file is found for input URLs.
    Usage:
        Run as a Scrapy spider. Ensure ChromeDriver is installed and the path is correctly set.
        The spider will automatically find the latest CSV file with thread URLs and crawl each thread, extracting posts and replies.
    """
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
            driver_path = os.environ.get(
                "CHROMEDRIVER_PATH",
                r"C:\Users\maste\.wdm\drivers\chromedriver\win64\chromedriver-win64\chromedriver.exe"
            )
            self.driver = webdriver.Chrome(
                service=Service(driver_path),
                options=chrome_options
            )
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise

        self.crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_closed(self, spider):
        """Ensure the Selenium WebDriver is properly closed when the spider finishes."""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                self.logger.info("Selenium WebDriver closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing Selenium WebDriver: {e}")

    def write_to_csv(self, data, file_path):
        """Write data to a CSV file with proper encoding."""
        import csv

        with open(file_path, mode='w', encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    def find_latest_csv(self):
        """
        Finds the most recently modified CSV file in the 'automation_exp_output' directory whose name starts with 'clubautohome_forum_threads_'.
        Returns:
            str: The full path to the latest CSV file.
        Raises:
            FileNotFoundError: If no matching CSV files are found in the output directory.
        """
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
        """
        Reads a CSV file containing thread information, detects and ensures proper encoding for Chinese characters,
        and generates Scrapy requests for each thread link found in the file.
        The method performs the following steps:
        1. Detects the encoding of the specified CSV file using the `chardet` library.
        2. Ensures the encoding supports Chinese characters, defaulting to UTF-8 if necessary.
        3. Reads the CSV file using the detected encoding and extracts thread information such as title, date, and link.
        4. Logs relevant information and errors during the process.
        5. Yields Scrapy requests for each thread link, passing thread metadata via the `meta` parameter.
        Yields:
            scrapy.Request: A Scrapy request object for each thread link found in the CSV file, with thread metadata attached.
        """
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
            if not encoding or (encoding and encoding.lower() not in ['utf-8', 'utf-16', 'gbk']):
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

            # self.write_to_csv(urls, csv_file_path)

            for url in urls:
                yield scrapy.Request(url=url['thread_link'], callback=self.parse, meta=url)
    
        except Exception as e:
            self.logger.error(f"Error while obtaining start requests: {e}")

    def parse(self, response):
        """
        Parse the main post and all replies in a clubautohome thread, yielding an item for each.
        This method uses Selenium to load the thread page and waits for the main post container to be present and visible.
        If the container is not visible or an error occurs during loading, a screenshot is saved and the URL is skipped.
        Once the page is loaded, it creates a Scrapy HtmlResponse from the Selenium page source for further parsing.
        Yields:
            AutomationExpItem: An item for the main post and each reply, containing author ID, date, position, text, thread title, and thread link.
        Args:
            response (scrapy.http.Response): The response object for the thread page.
        Side Effects:
            - Uses Selenium WebDriver to load and interact with the page.
            - Saves screenshots on errors or when elements are not visible.
            - Logs debug and error messages.
        """
        
        self.logger.debug(f"Processing URL: {response.url}")

        # Use Selenium to load the page and wait for the post container
        self.driver.get(response.url)
        try:
            # Wait for the post container to be present in the DOM
            elem = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section.fn-container"))
            )
            # Check if the element is visible
            if not elem.is_displayed():
                screenshot_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    f"selenium_not_visible_{int(time.time())}.png"
                )
                self.driver.save_screenshot(screenshot_path)
                self.logger.error(f"'section.fn-container' found but not visible. Screenshot saved to {screenshot_path}. Skipping URL.")
                return
            self.logger.debug("Successfully found the post container section with Selenium and it is visible.")
        except WebDriverException as e:
            screenshot_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                f"selenium_error_{int(time.time())}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            self.logger.error(f"Error loading page with Selenium: {e}. Screenshot saved to {screenshot_path}")
            return

        #while True: # Loop to handle pagination if needed
        selenium_response = scrapy.http.HtmlResponse(
                url=response.url, # no pagination, otherwise use self.driver.current_url to get the current URL after selenium loading the current page
                body=self.driver.page_source,
                encoding='utf-8'
            )

        # --- Main post ---
        post = selenium_response.css('section.fn-container > div.post-wrap')
        if post:
            post_item = AutomationExpItem()
            post_item['author_id'] = post.css('div.user-name > a.name::text').get()
            post_item['date'] = response.meta.get('thread_date')
            post_item['position'] = 1
            paragraphs = post.css('div.tz-paragraph::text').getall()
            concatenated_text = ''.join([p.strip() for p in paragraphs if p.strip()])
            post_item['text'] = concatenated_text
            post_item['thread_title'] = response.meta.get('thread_title')
            post_item['thread_link'] = response.meta.get('thread_link') or response.url
            yield post_item
        else:
            self.logger.debug("No post found with the selector 'div.post-wrap'")

        # --- Replies ---
        replies = selenium_response.css('section.fn-container > ul.reply-wrap > li.js-reply-floor-container')
        for idx, reply in enumerate(replies, start=2):
            reply_item = AutomationExpItem()
            reply_item['author_id'] = reply.css('div.user-name > a.name::text').get()
            reply_item['date'] = reply.css('span.reply-static-text > strong::text').get()
            reply_item['position'] = idx
            paragraphs = reply.css('div.reply-detail > div::text').getall()
            concatenated_text = ''.join([p.strip() for p in paragraphs if p.strip()])
            reply_item['text'] = concatenated_text
            reply_item['thread_title'] = response.meta.get('thread_title')
            reply_item['thread_link'] = response.meta.get('thread_link') or response.url
            yield reply_item

        # --- Pagination for replies --- temporarily disabled
        
        #next_page = selenium_response.css('div.reply-page > a.page-item-next::attr(href)').get()
        #if next_page:
            #   next_page_url = response.urljoin(next_page)
            #  self.logger.debug(f"Following next reply page: {next_page_url}")
            # self.driver.get(next_page_url)
            # Loop will continue with new page loaded
        #else:
            #   self.logger.debug("No more reply pages found.")
            #  break
