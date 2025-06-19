import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
import types
from automation_exp.spiders import teslaownersonline_forum_posts_spider

# Patch sys.modules to mock selenium and scrapy dependencies
mock_scrapy = types.ModuleType("scrapy")
mock_scrapy.Spider = object
mock_scrapy.http = types.SimpleNamespace(HtmlResponse=MagicMock())
sys.modules["scrapy"] = mock_scrapy
sys.modules["scrapy.http"] = mock_scrapy.http

mock_selenium = types.ModuleType("selenium")
sys.modules["selenium"] = mock_selenium
sys.modules["selenium.webdriver"] = types.SimpleNamespace(
    Chrome=MagicMock(),
    ChromeOptions=MagicMock(),
    ChromeService=MagicMock(),
    common=types.SimpleNamespace(
        by=types.SimpleNamespace(By=MagicMock()),
        exceptions=types.SimpleNamespace(WebDriverException=Exception)
    ),
    support=types.SimpleNamespace(
        ui=types.SimpleNamespace(WebDriverWait=MagicMock()),
        expected_conditions=types.SimpleNamespace(EC=MagicMock())
    )
)

# Patch the utils import
mock_utils = types.ModuleType("utils")
mock_utils.set_filter = MagicMock(return_value=("pattern", "2023-07-01"))
mock_utils.filter_link = MagicMock(return_value=True)
mock_utils.load_keywords = MagicMock(return_value=["tesla"])
mock_utils.load_start_urls = MagicMock(return_value=[{"name": "Forum1", "url": "http://example.com"}])
sys.modules["automation_exp.spiders.utils"] = mock_utils
sys.modules["..utils"] = mock_utils

# Now import the spider
with patch.dict('sys.modules', {
    'scrapy': mock_scrapy,
    'scrapy.http': mock_scrapy.http,
    'selenium': mock_selenium,
    'selenium.webdriver': sys.modules["selenium.webdriver"],
    'selenium.webdriver.common.by': types.SimpleNamespace(By=MagicMock()),
    'selenium.webdriver.chrome.options': types.SimpleNamespace(Options=MagicMock()),
    'selenium.webdriver.chrome.service': types.SimpleNamespace(Service=MagicMock()),
    'selenium.webdriver.support.ui': types.SimpleNamespace(WebDriverWait=MagicMock()),
    'selenium.webdriver.support.expected_conditions': types.SimpleNamespace(EC=MagicMock()),
    'selenium.common.exceptions': types.SimpleNamespace(WebDriverException=Exception),
    'automation_exp.spiders.utils': mock_utils,
    '..utils': mock_utils,
}):

class TestTeslaownersonlineForumPostsSpider(unittest.TestCase):
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.webdriver.Chrome")
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.load_keywords", return_value=["tesla"])
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.load_start_urls", return_value=[{"name": "Forum1", "url": "http://example.com"}])
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.set_filter", return_value=("pattern", "2023-07-01"))
    def test_spider_initialization(self, mock_set_filter, mock_load_start_urls, mock_load_keywords, mock_chrome):
        spider = teslaownersonline_forum_posts_spider.TeslaownersonlineForumPostsSpider()
        self.assertEqual(spider.keywords, ["tesla"])
        self.assertEqual(spider.start_urls_data, [{"name": "Forum1", "url": "http://example.com"}])
        self.assertEqual(spider.keyword_pattern, "pattern")
        self.assertEqual(spider.start_date, "2023-07-01")
        self.assertTrue(hasattr(spider, "driver"))

    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.webdriver.Chrome")
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.load_keywords", return_value=["tesla"])
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.load_start_urls", return_value=[{"name": "Forum1", "url": "http://example.com"}])
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.set_filter", return_value=("pattern", "2023-07-01"))
    def test_start_requests_yields(self, mock_set_filter, mock_load_start_urls, mock_load_keywords, mock_chrome):
        spider = teslaownersonline_forum_posts_spider.TeslaownersonlineForumPostsSpider()
        # Patch parse_forum_with_selenium to yield a known value
        spider.parse_forum_with_selenium = MagicMock(return_value=iter([{"thread_title": "Test", "thread_link": "http://example.com/thread", "thread_date": "2023-07-02", "forum_name": "Forum1", "forum_url": "http://example.com"}]))
        results = list(spider.start_requests())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["thread_title"], "Test")

    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.webdriver.Chrome")
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.load_keywords", return_value=["tesla"])
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.load_start_urls", return_value=[{"name": "Forum1", "url": "http://example.com"}])
    @patch("automation_exp.spiders.teslaownersonline_forum_posts_spider.set_filter", return_value=("pattern", "2023-07-01"))
    def test_closed_logs_and_quits_driver(self, mock_set_filter, mock_load_start_urls, mock_load_keywords, mock_chrome):
        spider = teslaownersonline_forum_posts_spider.TeslaownersonlineForumPostsSpider()
        spider.logger = MagicMock()
        spider.driver = MagicMock()
        spider.forum_stats = {"Forum1": {"pages": 1, "threads_crawled": 2, "threads_yielded": 1}}
        spider.closed("finished")
        spider.logger.info.assert_any_call("==== Forum Crawl Statistics ====")
        spider.driver.quit.assert_called_once()

if __name__ == "__main__":
    unittest.main()