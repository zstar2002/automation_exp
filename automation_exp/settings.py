import logging
import os
from datetime import datetime

# Scrapy settings for automation_exp project
BOT_NAME = 'automation_exp'

SPIDER_MODULES = ['automation_exp.spiders']
NEWSPIDER_MODULE = 'automation_exp.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

DOWNLOAD_DELAY = 2  # Default, can be overridden in spider custom_settings

# Configure logging
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'
os.makedirs('logs', exist_ok=True)
LOG_FILE = f"logs/{BOT_NAME}_{current_time}.log"

ROBOTSTXT_OBEY = True

SPIDER_MIDDLEWARES = {
    "automation_exp.middlewares.LoggingMiddleware": 543,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
