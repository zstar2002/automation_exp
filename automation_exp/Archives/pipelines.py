# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from automation_exp.items import AutomationExpItem
from bs4 import BeautifulSoup
from datetime import datetime
import pytz


class AutomationExpPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # check is text present, and then clean and validate it
        if adapter.get('text'):
            adapter['text'] = self.clean_text(adapter['text'])
            # Validate text field
            if not self.validate_text(adapter['text']):
                raise DropItem(f"Invalid text content in {item}")
        
        else:
            # drop item if no text
            raise DropItem(f"Missing text content in {item}")

        # Check if position is present, and then clean and validate it
        if adapter.get('position'):
            adapter['position'] = self.clean_position(adapter['position'])
            # Validate position field
            if not self.validate_position(adapter['position']):
                raise DropItem(f"Invalid position content in {item}")
        
        # Check if time data is present and process it
        if adapter.get('date'):
            adapter['date'] = self.process_time_data(adapter['date'])
            # Validate date field
            if not self.validate_date(adapter['date']):
                raise DropItem(f"Invalid date content in {item}")
        
        return item
    
    def process_time_data(self, time_str):
        # Parse the time string with timezone information
        dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S%z')
        # Convert to UTC
        dt_utc = dt.astimezone(pytz.utc)
        # Format the datetime object as a string
        return dt_utc.strftime('%Y-%m-%d %H:%M:%S %Z')
    
    def clean_text(self, html_content):
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the div with class bbWrapper
        bb_wrapper_div = soup.find('div', class_='bbWrapper')

        # Replace <br> tags with newline characters
        for br in bb_wrapper_div.find_all('br'):
            br.replace_with('\n')

        # Extract the text content
        text_modified = bb_wrapper_div.get_text(separator='\n').strip()
        # Remove extra empty lines
        text_modified = re.sub(r'\n\s*\n', '\n', text_modified)
        return text_modified
    
    def clean_position(self, position_str):
        # Remove all spaces and empty lines
        cleaned_position = re.sub(r'\s+', '', position_str)
        return cleaned_position
    
    def validate_text(self, text):
        # Example validation: Check if text is not empty and contains at least 10 characters
        return bool(text.strip()) and len(text) >= 10

    def validate_position(self, position):
        # Example validation: Check if position is not empty and matches a specific pattern
        # Assuming position should be a non-empty string
        return bool(position.strip())

    def validate_date(self, date):
        # Example validation: Check if date matches the expected format
        try:
            datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
            return True
        except ValueError:
            return False