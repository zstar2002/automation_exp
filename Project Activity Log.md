# Project Activity Log

## 2025-05-31

### Added Baidu Tieba Spiders

- Added `tieba_forum_posts_spider.py` to crawl thread titles and links from Baidu Tieba forums using keywords and start URLs from `configuration_files/Tieba/`.
- Added `tieba_content_spider.py` to crawl post content from Baidu Tieba threads listed in a `thread_urls.csv` file in the `spiders/` folder.
- Both spiders use Selenium for dynamic content and robust pagination, following the structure and conventions of the clubautohome spiders.
- Updated documentation in `README.md` to include instructions and details for Baidu Tieba spiders and configuration.

### Documentation

- Updated `README.md` to reflect the addition of Baidu Tieba spiders, their configuration, and usage instructions.