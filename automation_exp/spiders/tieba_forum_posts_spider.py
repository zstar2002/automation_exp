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

class TiebaForumPostsSpider(scrapy.Spider):
    name = "tieba_forum_posts_spider"
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
            # Add your pipeline if needed
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        keywords_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'configuration_files', 'Tieba', 'keywords.txt')
        self.keywords = load_keywords(keywords_file_path)

        start_urls_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'configuration_files', 'Tieba', 'start_urls.json')
        self.start_urls = load_start_urls(start_urls_file_path)
        
        start_date = '2020-07-01'
        self.keyword_pattern, self.start_date = set_filter(self.keywords, start_date)

        chrome_options = Options()
        chrome_options.add_argument('--log-level=3')
        # chrome_options.add_argument("--headless")
        try:
            driver_path = r"C:\\Users\\maste\\.wdm\\drivers\\chromedriver\\win64\\135.0.7049.114\\chromedriver-win32\\chromedriver.exe"
            self.driver = webdriver.Chrome(
                service=Service(driver_path),
                options=chrome_options
            )
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise
        self.forum_stats = {}

    def start_requests(self):
        for forum in self.start_urls:
            yield scrapy.Request(url=forum['url'], callback=self.parse, meta={'forum': forum})

    def parse(self, response):
        self.logger.debug(f"Processing URL: {response.url}")
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div > ul#thread_list.threadlist_bright"))
            )
            self.logger.debug("Successfully found the thread list element")
        except WebDriverException as e:
            self.logger.error(f"Error loading page with Selenium: {e}")
            return

        forum_name = response.meta['forum']['name']
        forum_url = response.meta['forum']['url']
        if forum_name not in self.forum_stats:
            self.forum_stats[forum_name] = {'pages': 0, 'posts_crawled': 0, 'posts_yielded': 0}

        max_pages = 100
        max_next_retries = 3
        pagination_start_time = time.time()
        max_pagination_seconds = 60
        page_count = 0
        while True:
            if time.time() - pagination_start_time > max_pagination_seconds:
                self.logger.warning(f"Pagination timeout after {max_pagination_seconds} seconds on forum: {forum_name}")
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
            posts = selenium_response.css('ul#thread_list.threadlist_bright > li.j_thread_list')
            if not posts:
                self.logger.debug("No posts found with the selector 'ul#thread_list > li.j_thread_list'")
            self.forum_stats[forum_name]['posts_crawled'] += len(posts)
            for post in posts:
                post_title = post.css('a.j_th_tit::text').get()
                post_link = post.css('a.j_th_tit::attr(href)').get()
                if post_link and post_link.startswith('/'):
                    post_link = post_link[1:]
                # Tieba does not always show post date on the list page, so skip date filtering if not available
                if post_title and filter_link({'link': post_title, 'date': None}, self.keyword_pattern, self.start_date):
                    self.forum_stats[forum_name]['posts_yielded'] += 1
                    self.logger.debug(f'The link of the post is: {post_link}')
                    self.logger.debug(f'The title of the post is: {post_title}')
                    yield {
                        'post_title': post_title,
                        'post_link': 'https://tieba.baidu.com/' + post_link.lstrip('/'),
                        'post_date': None,         # Tieba does not offer thread creation date; only the date of last reply
                        'forum_name': forum_name, 
                        'forum_url': forum_url
                    }
            # --- Next Page Handling ---
            next_found = False
            for retry in range(max_next_retries):
                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next.pagination-item"))
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
                        lambda driver: driver.find_element(By.CSS_SELECTOR, "div > ul#thread_list.threadlist_bright")
                    )
                    next_found = True
                    break
                except Exception as e:
                    self.logger.warning(f"Retry {retry+1}/{max_next_retries} failed to find/click next button: {e}")
                    time.sleep(2)
            if not next_found:
                self.logger.info("No more pages to crawl for this forum or failed to paginate. Exiting pagination loop.")
                break
        return

    def closed(self, reason):
        self.logger.info("==== Tieba Forum Crawl Statistics ====")
        for forum, stats in self.forum_stats.items():
            self.logger.info(
                f"Forum: {forum} | Pages: {stats['pages']} | Posts Crawled: {stats['posts_crawled']} | Posts Yielded: {stats['posts_yielded']}"
            )
        if hasattr(self, 'driver'):
            self.driver.quit()
