import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
import os
from automation_exp.spiders.tieba_forum_posts_spider import TiebaForumPostsSpider

# Patch sys.path to import the spider module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTiebaForumPostsSpider(unittest.TestCase):
    @patch('automation_exp.spiders.tieba_forum_posts_spider.webdriver.Chrome')
    @patch('automation_exp.spiders.tieba_forum_posts_spider.load_keywords', return_value=['test'])
    @patch('automation_exp.spiders.tieba_forum_posts_spider.load_start_urls', return_value=[{'name': 'test_forum', 'url': 'http://test.com'}])
    @patch('automation_exp.spiders.tieba_forum_posts_spider.set_filter', return_value=(MagicMock(), '2020-07-01'))
    def setUp(self, mock_set_filter, mock_load_start_urls, mock_load_keywords, mock_chrome):
        self.spider = TiebaForumPostsSpider()
        self.spider.logger = MagicMock()

    def test_start_requests_yields_requests(self):
        requests = list(self.spider.start_requests())
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].url, 'http://test.com')
        self.assertEqual(requests[0].meta['forum']['name'], 'test_forum')

    @patch('automation_exp.spiders.tieba_forum_posts_spider.scrapy.http.HtmlResponse')
    @patch('automation_exp.spiders.tieba_forum_posts_spider.filter_link', return_value=True)
    def test_parse_yields_posts(self, mock_filter_link, mock_html_response):
        # Setup mock response and selenium driver
        mock_response = MagicMock()
        mock_response.url = 'http://test.com'
        mock_response.meta = {'forum': {'name': 'test_forum', 'url': 'http://test.com'}}
        # Mock selenium driver and page_source
        self.spider.driver.page_source = '<html></html>'
        # Mock posts in selenium_response
        mock_post = MagicMock()
        mock_post.css.side_effect = [
            MagicMock(get=MagicMock(return_value='Test Title')),  # post_title
            MagicMock(get=MagicMock(return_value='/p/123')),      # post_link
            MagicMock(get=MagicMock(return_value='2024-01-01')),  # post_reply_date
        ]
        mock_html_response.return_value.css.return_value = [mock_post]
        # Patch WebDriverWait and EC
        with patch('automation_exp.spiders.tieba_forum_posts_spider.WebDriverWait'), \
             patch('automation_exp.spiders.tieba_forum_posts_spider.EC'):
            results = list(self.spider.parse(mock_response))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['post_title'], 'Test Title')
        self.assertTrue(results[0]['post_link'].startswith('https://tieba.baidu.com/'))

    @patch('automation_exp.spiders.tieba_forum_posts_spider.webdriver.Chrome')
    @patch('automation_exp.spiders.tieba_forum_posts_spider.load_keywords', return_value=['test'])
    @patch('automation_exp.spiders.tieba_forum_posts_spider.load_start_urls', return_value=[{'name': 'test_forum', 'url': 'http://test.com'}])
    @patch('automation_exp.spiders.tieba_forum_posts_spider.set_filter', return_value=(MagicMock(), '2020-07-01'))
    def test_closed_logs_and_quits_driver(self, mock_set_filter, mock_load_start_urls, mock_load_keywords, mock_chrome):
        spider = TiebaForumPostsSpider()
        spider.logger = MagicMock()
        spider.driver = MagicMock()
        spider.forum_stats = {'test_forum': {'pages': 1, 'posts_crawled': 2, 'posts_yielded': 1}}
        spider.closed('finished')
        spider.logger.info.assert_any_call("==== Tieba Forum Crawl Statistics ====")
        spider.driver.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main()