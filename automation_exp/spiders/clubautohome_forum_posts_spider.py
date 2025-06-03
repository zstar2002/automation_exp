import scrapy
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from ..utils import set_filter, filter_link
from ..utils import load_keywords, load_start_urls
from datetime import datetime, timedelta, timezone
import re
import time
import random
from webdriver_manager.chrome import ChromeDriverManager  # Add this import

class ClubAutohomeForumPostsSpider(scrapy.Spider):
    name = "clubautohome_forum_posts_spider"
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
            'automation_exp.pipelines.clubautohome_forum_posts_pipeline.ClubautohomeForumPostsPipeline': 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # load the keywords, start urls and start date; set the filter
        keywords_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'configuration_files', 'clubautohome', 'keywords.txt')
        self.keywords = load_keywords(keywords_file_path)

        start_urls_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'configuration_files', 'clubautohome', 'start_urls.json')
        self.start_urls = load_start_urls(start_urls_file_path)
        
        start_date = '2020-07-01'
        self.keyword_pattern, self.start_date = set_filter(self.keywords, start_date)

        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument('--log-level=3')  # Suppress DevTools listening logs
        # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode

        try:
            driver_path = r"C:\Users\maste\.wdm\drivers\chromedriver\win64\chromedriver-win64\chromedriver.exe"
            self.driver = webdriver.Chrome(
                service=Service(driver_path),
                options=chrome_options
            )    
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise

        self.forum_stats = {}  # {forum_name: {'pages': 0, 'posts_crawled': 0, 'posts_yielded': 0}}

    def start_requests(self):
        for forum in self.start_urls:
            yield scrapy.Request(url=forum['url'], callback=self.parse, meta={'forum': forum})

    def parse_post_date(self, date_str):
        """
        Parse post date string which can be either absolute (YYYY/MM/DD HH:MM:SS)
        or relative (e.g., '4天前', '2小时前', '5分钟前'). Returns ISO format string with timezone.
        """
        if not date_str:
            return None
        date_str = date_str.strip()
        tz = timezone(timedelta(hours=8))  # China Standard Time
        # Absolute date: 2025/03/16 12:36:26
        abs_match = re.match(r"(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})", date_str)
        if abs_match:
            dt = datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S")
            dt = dt.replace(tzinfo=tz)
            return dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        # Relative: X天前, X小时前, X分钟前
        now = datetime.now(tz)
        day_match = re.match(r"(\d+)天前", date_str)
        hour_match = re.match(r"(\d+)小时前", date_str)
        min_match = re.match(r"(\d+)分钟前", date_str)
        if day_match:
            days = int(day_match.group(1))
            dt = now - timedelta(days=days)
            return dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        elif hour_match:
            hours = int(hour_match.group(1))
            dt = now - timedelta(hours=hours)
            return dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        elif min_match:
            mins = int(min_match.group(1))
            dt = now - timedelta(minutes=mins)
            return dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        # If format is unknown, return as is
        return date_str

    def parse(self, response):
        # Log the URL being processed
        self.logger.debug(f"Processing URL: {response.url}")

        # Use Selenium to load the page and wait for the target element
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div > ul.post-list"))
            )
            self.logger.debug("Successfully found the element")
        except WebDriverException as e:
            self.logger.error(f"Error loading page with Selenium: {e}")
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join('..', 'logs', f'debug_screenshot_{current_time}.png')
            self.driver.save_screenshot(screenshot_path)
            return

        forum_name = response.meta['forum']['name']
        forum_description = response.meta['forum'].get('description', 'No description provided')
        forum_url = response.meta['forum']['url']

        if forum_name not in self.forum_stats:
            self.forum_stats[forum_name] = {'pages': 0, 'posts_crawled': 0, 'posts_yielded': 0}

        # --- Robust Pagination Control ---
        max_pages = 200  # Prevent infinite loop
        max_next_retries = 3  # Retry finding/clicking next button
        pagination_start_time = time.time()
        max_pagination_seconds = 60  #1 minutes per forum

        page_count = 0
        while True:
            # Timeout check
            if time.time() - pagination_start_time > max_pagination_seconds:
                self.logger.warning(f"Pagination timeout after {max_pagination_seconds} seconds on forum: {forum_name}")
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join('..', 'logs', f'timeout_screenshot_{current_time}.png')
                self.driver.save_screenshot(screenshot_path)
                break

            if page_count >= max_pages:
                self.logger.warning(f"Reached max page limit ({max_pages}) for forum: {forum_name}")
                break

            selenium_response = scrapy.http.HtmlResponse(
                url=response.url,
                body=self.driver.page_source,
                encoding='utf-8'
            )

            self.forum_stats[forum_name]['pages'] += 1
            page_count += 1

            posts = selenium_response.css('ul.post-list > li')
            if not posts:
                self.logger.debug("No posts found with the selector 'ul.post-list > li'")

            self.forum_stats[forum_name]['posts_crawled'] += len(posts)

            for post in posts:
                post_title = post.css('p.post-title > a::text').get()
                post_link = post.css('p.post-title > a::attr(href)').get()
                if post_link and post_link.startswith('/'):
                    post_link = post_link[1:]
                post_date_raw = post.css('div.post-basic-info > i.time::text').get()
                post_date = self.parse_post_date(post_date_raw)

                if post_title and filter_link({'link': post_title, 'date': post_date},
                                              self.keyword_pattern, self.start_date):
                    self.forum_stats[forum_name]['posts_yielded'] += 1
                    self.logger.debug(f'The link of the post is: {post_link}')
                    self.logger.debug(f'The title of the post is: {post_title}')
                    yield {
                        'post_title': post_title,
                        'post_link': 'https://club.autohome.com.cn/' + post_link.lstrip('/'),
                        'post_date': post_date,
                        'forum_name': forum_name,
                        'forum_url': forum_url
                    }

            # --- Robust Next Page Handling ---
            next_found = False
            for retry in range(max_next_retries):
                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.athm-page__next"))
                    )
                    if not next_button.is_enabled():
                        self.logger.info("Next button found but disabled. Exiting pagination loop.")
                        next_found = False
                        break
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    self.logger.debug("Clicking the next page button.")
                    next_button.click()
                    delay = random.uniform(2, 3)
                    time.sleep(delay)
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: driver.find_element(By.CSS_SELECTOR, "div > ul.post-list")
                    )
                    next_found = True
                    break
                except Exception as e:
                    self.logger.warning(f"Retry {retry+1}/{max_next_retries} failed to find/click next button: {e}")
                    time.sleep(2)
            if not next_found:
                self.logger.info("No more pages to crawl for this forum or failed to paginate. Exiting pagination loop.")
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join('..', 'logs', f'pagination_end_{current_time}.png')
                self.driver.save_screenshot(screenshot_path)
                break

        return  # Explicitly return to signal Scrapy this request is done

    def closed(self, reason):
        # Print forum statistics
        self.logger.info("==== Forum Crawl Statistics ====")
        for forum, stats in self.forum_stats.items():
            self.logger.info(
                f"Forum: {forum} | Pages: {stats['pages']} | Posts Crawled: {stats['posts_crawled']} | Posts Yielded: {stats['posts_yielded']}"
            )
        # Close the Selenium WebDriver when the spider is closed
        if hasattr(self, 'driver'):
            self.driver.quit()

    def write_to_csv(self, data, file_path):
        """Write data to a CSV file with proper encoding."""
        import csv
        with open(file_path, mode='w', encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


