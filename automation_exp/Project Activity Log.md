# Project Activity Log

This document records the daily activities and changes made to the files in the **automation_exp** project.

## 2024-10-19

### Updates to `items.py`

- Changed field `html_content` to [`text`].

### Updates to `PostContent.py`

- Replaced all occurrences of `html_content` with `text`.

### Updates to `pipelines.py`

- Replaced all occurrences of `html_content` with `text`.
- Changed all occurrences of `text_content` to `text_modified`.
- Added `process_time_data` function to process the `date` field of the crawled item. This function adds time zone information and converts the date-time format from `%Y-%m-%dT%H:%M:%S%z` to `%Y-%m-%d %H:%M:%S %Z`. It returns the string containing the time information.
- Separated functions `clean_text` and `clean_position` for cleaning HTML content and post position information.
- Added validation functions for validating the position, date, and text information crawled.

### Updates to `settings.py`

- Enabled the logging middleware.
- Changed the log file creation behavior:
  - A new log file is created whenever the spider is executed.
  - The log file name contains the start time of crawling.

### Updates to `middlewares.py`

- Added logging middleware class to log the start time, end time, and duration of crawling.

### Problem to be Solved

- The time of the first post inside a thread is incorrect. When extracting the time, it always incorrectly yields the last update time of the thread.

## 2024-10-20

### Updates to `PostContent.py`

- Updated the method of getting the `date` field to correctly extract the time of post creation. This resolved the problem mentioned on 2024-10-19. After checking the log file and output file, the problem has been resolved.

### Updates to `First_Insight.ipynb`

- Re-crawled the web data from Tesla Owners Online and accommodated the changes in the output file. The previous issue of the spider yielding empty text data (normally because the post author didn’t input any text and just cited another post or inserted a picture or video) in the Oct. 14 output data has disappeared since the new validation functions were added in the item pipelines.

### Updates to `Preparation.ipynb`

- Adjusted the file to make it workable.

## 2025-05-14

### Updates to `test_automation.py`

- Automated the execution of `forum_posts_spider` whenever the script is run.
- Ensured that the spider output is saved as a CSV file in the `forum_threads` folder under `automation_exp`.
- The output CSV filename now includes `forum_threads` and a timestamp (e.g., `forum_threads_YYYYMMDD_HHMMSS.csv`).
- The output directory is created automatically if it does not exist.

### Updates to `forum_posts_spider.py`

- Fixed the spider so it exits cleanly after crawling all forum URLs, allowing the process to terminate automatically.
- Added per-forum statistics: the spider now logs, for each forum, the number of pages crawled, posts crawled (before filtering), and posts yielded (after filtering) at the end of each crawl.

### Documentation

- Updated the `ReadMe.md` to reflect the new automation and output-saving behavior for forum crawling.

## 2025-05-15

### Project Structure and Configuration Refactor

- Removed redundant `config.json`, `start_urls.json`, and `keywords.txt` from the `spiders` folder. All configuration, keywords, and start URLs are now loaded exclusively from the appropriate `configuration_files/<website>/` directory (e.g., `configuration_files/clubautohome/`).
- Confirmed that all spiders read their configuration from the correct per-website configuration folder.

### File Renaming for Clarity

- Renamed `forum_posts_spider.py` to `clubautohome_forum_posts_spider.py` and `content_spider.py` to `clubautohome_content_spider.py` to reflect their site-specific purpose.
- Renamed `test_automation.py` to `test_clubautohome_automation.py` for clarity.

### Output and Logging Improvements

- Updated `test_clubautohome_automation.py`:
  - Output CSV files now always include `clubautohome` in their filenames (e.g., `clubautohome_forum_threads_YYYYMMDD_HHMMSS.csv`).
  - Log files are now named with the spider name and timestamp (e.g., `clubautohome_forum_posts_spider_YYYYMMDD_HHMMSS.log`).
  - Ensured log files are written to a single top-level `logs` directory to avoid confusion with multiple log folders.
- Verified that the spider and test script do not use or require any configuration files from the `spiders` directory.

### General

- Cleaned up project structure and improved maintainability by enforcing per-site configuration and naming conventions.

## 2025-05-16

### Updates to `test_clubautohome_automation.py`

- Confirmed that the script automatically creates the `forum_threads` output directory if it does not exist.
- Output CSV files are named as `clubautohome_forum_threads_YYYYMMDD_HHMMSS.csv` and saved in the `forum_threads` folder.
- Log files are named as `clubautohome_forum_posts_spider_YYYYMMDD_HHMMSS.log` and saved in the top-level `logs` directory.
- The script prints the log file path after each run for user convenience.

### Documentation

- Updated `ReadMe.md` to clarify the automated output and logging behavior, and to reflect the current script and project structure.

## 2025-05-18

### Project Structure and Folder Organization

- Moved all configuration files (`config.json`, `keywords.txt`, `start_urls.json`) for each website to the top-level `configuration_files/<website>/` directory. No configuration, keywords, or start_urls files remain in the `spiders/` folder.
- Verified that all spiders and scripts load their configuration exclusively from the appropriate `configuration_files/<website>/` directory.
- The `spiders/` folder now contains only spider definitions and (optionally) thread URL input files (such as `thread_urls.csv`).
- Output CSV files for forum threads are saved in the `forum_threads/` directory, always including the website name and a timestamp (e.g., `clubautohome_forum_threads_YYYYMMDD_HHMMSS.csv`).
- Output CSV files for post content are saved in the `post_content/` directory, with similar timestamped naming conventions (e.g., `clubautohome_post_content_YYYYMMDD_HHMMSS.csv`).
- Log files for each spider run are named with the spider name and timestamp (e.g., `clubautohome_forum_posts_spider_YYYYMMDD_HHMMSS.log` or `clubautohome_content_spider_YYYYMMDD_HHMMSS.log`) and are saved in the top-level `logs/` directory. No log files are stored in subfolders.
- The test scripts for running spiders and saving output/logs are now named to reflect the website and spider, e.g., `test_clubautohome_automation.py`, `test_clubautohome_content_spider.py`, and `test_clubautohome_forum_post_automation.py`.
- Confirmed that the output and log directories are created automatically by the test scripts if they do not exist.
- Updated the `ReadMe.md` to clarify the new folder structure, naming conventions, and automated output/logging behavior. The documentation now explicitly states that all configuration, keywords, and start_urls files must be in `configuration_files/<website>/`, and that the `spiders/` folder should not contain any such files.
- Ensured that all usage instructions, troubleshooting, and project structure documentation are consistent with the new organization and conventions.

## 2025-05-20

### Spider Configuration Refactor

- Removed all code in spiders that loaded configuration or settings from external config files (such as config.json or config.py). All spider-specific settings are now defined directly in each spider's Python file using the `custom_settings` attribute.
- Only data files (`keywords.txt`, `start_urls.json`) are loaded from `configuration_files/<website>/` as data sources, not as configuration.
- Updated documentation in `ReadMe.md` to clarify this change and to remove any mention of config.json for spider settings.

### Code Cleanup: Remove Unused Imports

- Reviewed all Python files in the project for unused import statements.
- Removed any import statements that were not used in the code, improving code clarity and reducing potential confusion.
- No functional changes were made to the spiders or scripts; this update is purely for code hygiene and maintainability.

### Investigation: Pagination and Yielded Results in clubautohome_forum_posts_spider

- Investigated why some forums do not paginate through all pages or yield few/no results.
- Documented causes: max page limit, next button not found/disabled, timeouts, anti-bot measures, and strict filter logic.
- Added troubleshooting and explanation to the ReadMe.md for future reference.


