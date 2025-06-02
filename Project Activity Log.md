# Project Activity Log

## 2025-05-31

### Added Baidu Tieba Spiders

- Added `tieba_forum_posts_spider.py` to crawl thread titles and links from Baidu Tieba forums using keywords and start URLs from `configuration_files/Tieba/`.
- Added `tieba_content_spider.py` to crawl post content from Baidu Tieba threads listed in a `thread_urls.csv` file in the `spiders/` folder.
- Both spiders use Selenium for dynamic content and robust pagination, following the structure and conventions of the clubautohome spiders.
- Updated documentation in `README.md` to include instructions and details for Baidu Tieba spiders and configuration.

### Documentation

- Updated `README.md` to reflect the addition of Baidu Tieba spiders, their configuration, and usage instructions.

## 2025-06-01

### Added Test Automation for Baidu Tieba Spiders

- Created `test_tieba_forum_posts_spider.py` to automate running the `tieba_forum_posts_spider`.
  - Output CSV files are named as `tieba_forum_threads_YYYYMMDD_HHMMSS.csv` and saved in the `forum_threads/` folder.
  - Log files are named as `tieba_forum_posts_spider_YYYYMMDD_HHMMSS.log` and saved in the top-level `logs/` directory.
- Created `test_tieba_content_spider.py` to automate running the `tieba_content_spider`.
  - Output CSV files are named as `tieba_post_content_YYYYMMDD_HHMMSS.csv` and saved in the `automation_exp_output/` folder.
  - Log files are named as `tieba_content_spider_YYYYMMDD_HHMMSS.log` and saved in the `automation_exp_log/` directory.
- Both scripts follow the same conventions as the clubautohome test automation scripts, including automatic creation of output and log directories and timestamped file naming.
- Updated the `README.md` to document the usage and conventions for the new Tieba test automation scripts.

## 2025-06-02

### Filtering Logic Update

- Updated `filter_link` in `utils.py` so that if a forum thread does not provide a creation date (`date` is None), the filter will only apply keyword matching and will not exclude the thread based on date. This allows threads without a date to be included if they match the keywords.

### Output and Log Directory Convention Update

- All spider output files are now saved in `C:\Users\maste\PythonProjects\automation_exp_output`.
- All log files are now saved in `C:\Users\maste\PythonProjects\automation_exp_log`.
- All test automation scripts have been updated to use these directories for output and logs.
- Documentation in `README.md` updated to reflect this change.