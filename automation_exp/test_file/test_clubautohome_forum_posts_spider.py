import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from automation_exp.spiders.clubautohome_forum_posts_spider import ClubAutohomeForumPostsSpider

class TestClubAutohomeForumPostsSpider(unittest.TestCase):
    def setUp(self):
        # Patch Selenium WebDriver to avoid launching a real browser
        patcher = patch('automation_exp.spiders.clubautohome_forum_posts_spider.webdriver.Chrome')
        self.mock_webdriver = patcher.start()
        self.addCleanup(patcher.stop)
        # Patch logger to avoid actual logging
        self.logger_patcher = patch.object(ClubAutohomeForumPostsSpider, 'logger', new=MagicMock())
        self.logger_patcher.start()
        self.addCleanup(self.logger_patcher.stop)
        # Patch utility functions
        self.load_keywords_patch = patch('automation_exp.spiders.clubautohome_forum_posts_spider.load_keywords', return_value=['test'])
        self.load_start_urls_patch = patch('automation_exp.spiders.clubautohome_forum_posts_spider.load_start_urls', return_value=[{'url': 'http://test.com', 'name': 'TestForum'}])
        self.set_filter_patch = patch('automation_exp.spiders.clubautohome_forum_posts_spider.set_filter', return_value=(MagicMock(), '2020-07-01'))
        self.load_keywords_patch.start()
        self.load_start_urls_patch.start()
        self.set_filter_patch.start()
        self.addCleanup(self.load_keywords_patch.stop)
        self.addCleanup(self.load_start_urls_patch.stop)
        self.addCleanup(self.set_filter_patch.stop)
        self.spider = ClubAutohomeForumPostsSpider()

    def test_parse_post_date_absolute(self):
        date_str = "2025/03/16 12:36:26"
        result = self.spider.parse_post_date(date_str)
        self.assertTrue(result.startswith("2025-03-16T12:36:26"))

    def test_parse_post_date_relative_days(self):
        now = datetime.now(timezone(timedelta(hours=8)))
        date_str = "2天前"
        result = self.spider.parse_post_date(date_str)
        dt = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S%z")
        self.assertAlmostEqual((now - dt).days, 2, delta=1)

    def test_parse_post_date_relative_hours(self):
        now = datetime.now(timezone(timedelta(hours=8)))
        date_str = "3小时前"
        result = self.spider.parse_post_date(date_str)
        dt = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S%z")
        self.assertAlmostEqual((now - dt).seconds // 3600, 3, delta=1)

    def test_parse_post_date_relative_minutes(self):
        now = datetime.now(timezone(timedelta(hours=8)))
        date_str = "15分钟前"
        result = self.spider.parse_post_date(date_str)
        dt = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S%z")
        self.assertAlmostEqual((now - dt).seconds // 60, 15, delta=2)

    def test_parse_post_date_invalid(self):
        date_str = "invalid date"
        result = self.spider.parse_post_date(date_str)
        self.assertEqual(result, "invalid date")

    def test_start_requests_yields_requests(self):
        requests = list(self.spider.start_requests())
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].url, 'http://test.com')
        self.assertEqual(requests[0].meta['forum']['name'], 'TestForum')

    def test_closed_calls_driver_quit(self):
        self.spider.driver = MagicMock()
        self.spider.forum_stats = {'TestForum': {'pages': 1, 'posts_crawled': 2, 'posts_yielded': 1}}
        self.spider.closed('finished')
        self.spider.driver.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main()