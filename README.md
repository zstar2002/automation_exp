# Automation Exp

`automation_exp` is a web scraping project using the Scrapy framework to crawl posts from automotive forums such as [club.autohome.com.cn](https://club.autohome.com.cn). The project is designed to accumulate text data for subsequent text analysis. The structure supports per-website configuration and can be adapted for other web scraping tasks with some modifications.

## Features

- Crawl forum thread links and posts based on pre-defined rules.
- Extract posts from threads and handle pagination to ensure all posts are collected.
- Log the start and end times of each spider run, with log files named by start time and spider name.
- Save extracted data in a structured format for further analysis.
- **Automated crawling and output saving:** Running the automation script will automatically run the forum spider and save results to a timestamped CSV file in a dedicated folder.
- **Forum-level statistics:** The spider tracks and logs, for each forum, the number of pages crawled, posts crawled (before filtering), and posts yielded (after filtering).
- **Per-site configuration:** All configuration, keywords, and start URLs are loaded from `configuration_files/<website>/` (e.g., `configuration_files/clubautohome/`).

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/automation_exp.git
    cd automation_exp
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    # or
    source venv/bin/activate  # On Linux/Mac
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Prepare the start links and configuration

- Place your per-site configuration files in `configuration_files/<website>/` (e.g., `configuration_files/clubautohome/`).
  - `keywords.txt`: List of keywords for filtering posts.
  - `start_urls.json`: List of forum URLs to crawl.
- For content spiders that require thread URLs, create a CSV file named `thread_urls.csv` in the `automation_exp/spiders` directory with the following structure:

```csv
thread_title,thread_link
Example Thread 1,https://club.autohome.com.cn/threads/example-thread-1
Example Thread 2,https://club.autohome.com.cn/threads/example-thread-2
```

### 2. Run the forum spider automation

To automatically crawl forum posts and save the output to a timestamped CSV file, run:

```powershell
python automation_exp/test_clubautohome_automation.py
```

This will:
- Run the `clubautohome_forum_posts_spider` automatically.
- Save the output as a CSV file named like `clubautohome_forum_threads_YYYYMMDD_HHMMSS.csv`.
- Place the output file in the `automation_exp/forum_threads/` folder (created if it does not exist).
- After crawling, the spider logs per-forum statistics (pages crawled, posts crawled, posts yielded) in the log file for each run.

### 3. Log Files

Each spider run will create a new log file with the spider name and start time in its name. The log file will contain information about when the spider started and how long it took to complete the task. Log files are saved in the `automation_exp/logs/` directory. Only one top-level `logs` directory is used for all log files.

## Project Configuration and Structure (Updated 2025-05-20)

### Per-Site Configuration

- All configuration files (`start_urls.json`, `keywords.txt`) are now stored in `configuration_files/<website>/` (e.g., `configuration_files/clubautohome/`, `configuration_files/Tieba/`).
- The `spiders` folder should NOT contain any config, keywords, or start_urls files.
- Spiders load only data files (such as `keywords.txt` and `start_urls.json`) from the appropriate `configuration_files/<website>/` directory. **All spider-specific settings are now defined directly in each spider's Python file using the `custom_settings` attribute. No spider loads configuration or settings from any external config file.**

### Spider and Script Naming

- Spiders and test scripts are named to reflect the website they target, e.g.:
  - `clubautohome_forum_posts_spider.py`
  - `clubautohome_content_spider.py`
  - `tieba_forum_posts_spider.py`
  - `tieba_content_spider.py`
  - `test_clubautohome_automation.py`

### Output and Logging

- Output CSV files always include the website name and a timestamp, e.g. `clubautohome_forum_threads_YYYYMMDD_HHMMSS.csv`.
- Log files are named with the spider name and timestamp, e.g. `clubautohome_forum_posts_spider_YYYYMMDD_HHMMSS.log`.
- All logs are written to a single top-level `logs/` directory to avoid confusion.

### Running the Spider

- Use the test script (e.g., `python test_clubautohome_automation.py`) to run the spider and automatically generate output and logs with the correct naming and location.

### Troubleshooting

- If you see a `FileNotFoundError` for `spiders/config.json`, ensure you have removed all config files from the `spiders` folder and that your spider and settings are loading config from `configuration_files/<website>/`.
- The project no longer expects or uses any config, keywords, or start_urls files in the `spiders` directory.

## Troubleshooting Pagination and Yielded Results

### Why does the spider not crawl all pages or yield few/no results for some forums?

- **Max Page Limit:** The spider has a built-in `max_pages` limit (default 100) to prevent infinite loops. If a forum has more than 100 pages, crawling will stop at this limit.
- **Next Button Issues:** If the "Next" button is not found, not clickable, or disabled (e.g., on the last page), the spider will stop paginating. This can happen if the selector changes or the button is not loaded in time.
- **Timeouts:** If a forum takes too long to load pages, the spider will stop paginating after a set timeout (default 5 minutes per forum).
- **Anti-bot or Rate Limiting:** Some forums may have anti-bot measures that prevent further navigation after a certain number of requests or pages.
- **Filter Logic:** The spider uses keyword and date filters. If no posts match the filter, the spider will yield few or no results, even if many posts are crawled.

### How to Diagnose and Adjust

- Check the log files for warnings about the next button, timeouts, or max page limits.
- Manually inspect the forum in a browser to see if the "Next" button is present and enabled on all pages.
- Print/log the current page number and URL at each iteration for debugging.
- Review and adjust your filter logic and keyword/date settings in the configuration files.
- If you encounter anti-bot blocks, consider increasing delays, randomizing user agents, or using proxies.

## Project Structure

- `automation_exp/`: Root directory of the project.
- `spiders/`: Contains only the spider definitions and (optionally) thread URL input files. **No config, keywords, or start_urls files should be here.**
- `items.py`: Defines the data structure for the scraped items.
- `middlewares.py`: Contains custom middlewares, including logging middleware.
- `pipelines.py`: Defines the item processing pipeline.
- `settings.py`: Scrapy settings for the project.
- `forum_threads/`: Output folder for all forum spider CSV files.
- `logs/`: Log files for each spider run. All logs are stored here, not in subfolders.
- `configuration_files/<website>/`: Per-site configuration, keywords, and start URLs. **All config, keywords, and start_urls files must be here.**
- `test_clubautohome_automation.py`: Script to run the clubautohome forum spider and save output automatically.

## Customization

To adapt this project for other web scraping tasks or websites, you may need to:

- Add a new folder under `configuration_files/` for the new website and provide the necessary config, keywords, and start URLs.
- Modify the CSS selectors in the spider to match the structure of the target website.
- Update the item definitions in `items.py` to include the fields you want to extract.
- Adjust the pipelines and middlewares as needed for your specific use case.
- Rename the spider and test script to reflect the new website.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [Scrapy](https://scrapy.org/) - An open-source and collaborative web crawling framework for Python.

- `tieba_forum_posts_spider.py`: Scrapes thread titles and links from Baidu Tieba forums using keywords and start URLs from `configuration_files/Tieba/`.
- `tieba_content_spider.py`: Scrapes post content from Baidu Tieba threads listed in a `thread_urls.csv` file in the `spiders/` folder.

## Usage for Baidu Tieba

- For Baidu Tieba, use `tieba_forum_posts_spider.py` to crawl thread links and `tieba_content_spider.py` to crawl post content from those threads. Place your `keywords.txt` and `start_urls.json` in `configuration_files/Tieba/` and your `thread_urls.csv` in the `spiders/` folder.

## Test Automation for Baidu Tieba Spiders

### Running Tieba Forum Posts Spider

To automatically crawl Baidu Tieba forum thread links and save the output to a timestamped CSV file, run:

```powershell
python automation_exp/test_file/test_tieba_forum_posts_spider.py
```

- This will run the `tieba_forum_posts_spider`.
- Output is saved as `tieba_forum_threads_YYYYMMDD_HHMMSS.csv` in the `forum_threads/` folder.
- Log files are named as `tieba_forum_posts_spider_YYYYMMDD_HHMMSS.log` and saved in the top-level `logs/` directory.

### Running Tieba Content Spider

To crawl post content from Baidu Tieba threads listed in `thread_urls.csv`, run:

```powershell
python automation_exp/test_file/test_tieba_content_spider.py
```

- This will run the `tieba_content_spider`.
- Output is saved as `tieba_post_content_YYYYMMDD_HHMMSS.csv` in the `automation_exp_output/` folder.
- Log files are named as `tieba_content_spider_YYYYMMDD_HHMMSS.log` and saved in the `automation_exp_log/` directory.

### Notes

- Both test scripts follow the same automation and output/logging conventions as the clubautohome scripts.
- Output and log directories are created automatically if they do not exist.
- See the `test_file/` directory for all available test automation scripts for each site and spider.
