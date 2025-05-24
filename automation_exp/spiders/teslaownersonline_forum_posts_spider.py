import scrapy
import os
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from ..utils import set_filter, filter_link, load_keywords, load_start_urls

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
]

class TeslaownersonlineForumPostsSpider(scrapy.Spider):
    name = "teslaownersonline_forum_posts_spider"
    allowed_domains = ["www.teslaownersonline.com"]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': random.choice(USER_AGENTS),
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.teslaownersonline.com/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1'
        },
        'DOWNLOAD_DELAY': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 10,
        'AUTOTHROTTLE_MAX_DELAY': 120,
        'COOKIES_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 1,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429, 409],
        'ITEM_PIPELINES': {
            'automation_exp.pipelines.teslaownersonline_forum_posts_pipeline.TeslaownersonlineForumPostsPipeline': 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_dir = os.path.join(base_dir, 'configuration_files', 'Teslaownersonline')
        keywords_file_path = os.path.join(config_dir, 'keywords.txt')
        start_urls_file_path = os.path.join(config_dir, 'start_urls.json')
        self.keywords = load_keywords(keywords_file_path)
        self.start_urls_data = load_start_urls(start_urls_file_path)
        start_date = '2023-07-01'
        self.keyword_pattern, self.start_date = set_filter(self.keywords, start_date)

        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument('--log-level=3')
        # chrome_options.add_argument("--headless")  # Uncomment to run headless
        try:
            driver_path = r"C:\Users\maste\.wdm\drivers\chromedriver\win64\135.0.7049.114\chromedriver-win32\chromedriver.exe"
            self.driver = webdriver.Chrome(
                service=Service(driver_path),
                options=chrome_options
            )
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise

        self.forum_stats = {}

    def start_requests(self):
        # Instead of yielding Scrapy requests, just iterate and call Selenium parse directly
        for forum in self.start_urls_data:
            yield from self.parse_forum_with_selenium(forum)

    def parse_forum_with_selenium(self, forum):
        forum_name = forum['name']
        forum_url = forum['url']
        keyword_pattern = self.keyword_pattern
        start_date = self.start_date

        if forum_name not in self.forum_stats:
            self.forum_stats[forum_name] = {'pages': 0, 'threads_crawled': 0, 'threads_yielded': 0}

        max_pages = 100
        max_next_retries = 3
        page_count = 0

        self.driver.get(forum_url)
        while True:
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.structItem-cell.structItem-cell--main"))
                )
            except WebDriverException as e:
                self.logger.error(f"Error loading page with Selenium: {e}")
                break

            selenium_response = scrapy.http.HtmlResponse(
                url=self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8'
            )

            threads = selenium_response.css('div.structItem-cell.structItem-cell--main')
            self.forum_stats[forum_name]['pages'] += 1
            self.forum_stats[forum_name]['threads_crawled'] += len(threads)
            page_count += 1

            if not threads:
                self.logger.debug("No threads found with the selector 'div.structItem-cell.structItem-cell--main'")
                break

            for thread in threads:
                thread_title = thread.css(' a.thread-title--gtm::text').get()
                thread_link = thread.css(' a.thread-title--gtm::attr(href)').get()
                thread_date = thread.css(' time.thread-time--gtm::attr(datetime)').get()
                if thread_title and thread_link and filter_link({'link': thread_link, 'date': thread_date}, keyword_pattern, start_date):
                    self.forum_stats[forum_name]['threads_yielded'] += 1
                    yield {
                        'thread_title': thread_title.strip(),
                        'thread_link': 'https://www.teslaownersonline.com' + thread_link if thread_link.startswith('/') else thread_link,
                        'thread_date': thread_date,
                        'forum_name': forum_name,
                        'forum_url': forum_url
                    }

            # Pagination: click next button if available
            next_found = False
            for retry in range(max_next_retries):
                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.pageNav-jump.pageNav-jump--next.button.button--icon-only"))
                    )
                    if not next_button.is_enabled():
                        self.logger.info("Next button found but disabled. Exiting pagination loop.")
                        next_found = False
                        break
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    self.logger.debug("Clicking the next page button.")
                    next_button.click()
                    time.sleep(random.uniform(2, 3))
                    next_found = True
                    break
                except Exception as e:
                    self.logger.warning(f"Retry {retry+1}/{max_next_retries} failed to find/click next button: {e}")
                    time.sleep(2)
            if not next_found or page_count >= max_pages:
                self.logger.info("No more pages to crawl for this forum or reached max page limit.")
                break

    def closed(self, reason):
        self.logger.info("==== Forum Crawl Statistics ====")
        for forum, stats in self.forum_stats.items():
            self.logger.info(
                f"Forum: {forum} | Pages: {stats['pages']} | Threads Crawled: {stats['threads_crawled']} | Threads Yielded: {stats['threads_yielded']}"
            )
        if hasattr(self, 'driver'):
            self.driver.quit()
