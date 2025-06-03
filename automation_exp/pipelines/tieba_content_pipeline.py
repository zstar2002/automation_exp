# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from automation_exp.items import AutomationExpItem
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

class TiebaContentPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Clean and validate thread_title
        if adapter.get('thread_title'):
            adapter['thread_title'] = self.clean_text(adapter['thread_title'])
            if not self.validate_text(adapter['thread_title']):
                raise DropItem(f"Invalid thread_title in {item}")
        else:
            raise DropItem(f"Missing thread_title in {item}")

        # Clean and validate thread_link
        if adapter.get('thread_link'):
            adapter['thread_link'] = adapter['thread_link'].strip()
        else:
            raise DropItem(f"Missing thread_link in {item}")

        # Clean and validate date
        if adapter.get('date'):
            adapter['date'] = self.process_time_data(adapter['date'])
            if not self.validate_date(adapter['date']):
                raise DropItem(f"Invalid date in {item}")
        else:
            raise DropItem(f"Missing date in {item}")

        # Clean and validate text
        if adapter.get('text'):
            adapter['text'] = self.clean_text(adapter['text'])
            if not self.validate_text(adapter['text']):
                raise DropItem(f"Invalid text in {item}")
        else:
            raise DropItem(f"Missing text in {item}")

        # Clean and validate position
        if adapter.get('position'):
            adapter['position'] = self.clean_position(adapter['position'])
            if not self.validate_position(adapter['position']):
                raise DropItem(f"Invalid position in {item}")
        else:
            raise DropItem(f"Missing position in {item}")

        return item

    def process_time_data(self, time_str):
        # Accept ISO 8601 or return as is if not parseable
        try:
            dt = datetime.fromisoformat(time_str)
            dt_utc = dt.astimezone(pytz.utc)
            return dt_utc.strftime('%Y-%m-%d %H:%M:%S %Z')
        except Exception:
            return time_str

    def clean_text(self, text):
        # Remove HTML tags and extra whitespace
        soup = BeautifulSoup(text, 'html.parser')
        text_modified = soup.get_text(separator=' ').strip()
        text_modified = re.sub(r'\s+', ' ', text_modified)
        return text_modified

    def clean_position(self, position_str):
        cleaned_position = re.sub(r'\s+', '', str(position_str))
        return cleaned_position

    def validate_text(self, text):
        return bool(text.strip()) and len(text) >= 3

    def validate_position(self, position):
        return bool(str(position).strip())

    def validate_date(self, date):
        try:
            datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
            return True
        except Exception:
            try:
                datetime.fromisoformat(date)
                return True
            except Exception:
                return False
