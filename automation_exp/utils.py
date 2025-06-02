import re
from datetime import datetime
import pytz
import json
import os

def set_filter(keywords, start_date):
    """
    Sets the filter criteria based on specified keywords and date range.

    Parameters:
    keywords (list): List of keywords to match in the link.
    start_date (str): Start date in 'YYYY-MM-DD' format.

    Returns:
    tuple: Compiled keyword pattern and start date as datetime object.
    """
    # Compile the regular expression for keywords
    keyword_pattern = re.compile(r'(?:' + '|'.join(keywords) + ')', re.IGNORECASE)
    
    # Convert start_date to datetime object
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    return keyword_pattern, start_date   

def filter_link(link_info, keyword_pattern, start_date):
    """
    Filters a single link based on the specified keyword pattern and date range.

    Parameters:
    link_info (dict): Dictionary containing 'link' and 'date' keys. 'date' key value should be a datetime string or None.
    keyword_pattern (re.Pattern): Compiled regular expression pattern for keywords.
    start_date (datetime): Start date as datetime object.

    Returns:
    str or None: The link if it matches the criteria, None otherwise.
    """
    link = link_info['link']
    date_str = link_info['date']

    # If no date is provided, only filter by keyword
    if date_str is None:
        if keyword_pattern.search(link):
            return link
        else:
            return None

    # Convert link date to datetime object
    link_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')

    # Convert start_date to timezone-aware datetime object
    start_date = start_date.replace(tzinfo=pytz.UTC)

    # Get the current date and convert it to timezone-aware datetime object
    end_date = datetime.now(pytz.UTC)

    # Check if link matches the keyword pattern and is within the date range
    if keyword_pattern.search(link) and start_date <= link_date <= end_date:
        return link
    else:
        return None

# Add utility functions for dynamic keyword and URL updates
def load_keywords(file_path):
    """Load keywords from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:  # Specify UTF-8 encoding
        return [line.strip() for line in f if line.strip()]

def load_start_urls(file_path):
    """Load start URLs from a file."""
    # Resolve the absolute path for start_urls.json in the upper folder
    file_path = os.path.join(os.path.dirname(__file__), 'spiders', file_path)  # Adjusted to reflect the correct path
    try:
        with open(file_path, 'r', encoding='utf-8') as f:  # Specify UTF-8 encoding
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"The start_urls file was not found at the expected location: {file_path}")