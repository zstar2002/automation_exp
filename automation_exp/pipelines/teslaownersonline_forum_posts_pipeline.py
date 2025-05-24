import re
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from automation_exp.items import AutomationExpItem
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

class TeslaownersonlineForumPostsPipeline:
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

        # Clean and validate thread_date
        if adapter.get('thread_date'):
            adapter['thread_date'] = self.process_time_data(adapter['thread_date'])
            if not self.validate_date(adapter['thread_date']):
                raise DropItem(f"Invalid thread_date in {item}")
        else:
            raise DropItem(f"Missing thread_date in {item}")

        # Clean and validate forum_name
        if adapter.get('forum_name'):
            adapter['forum_name'] = adapter['forum_name'].strip()
        else:
            raise DropItem(f"Missing forum_name in {item}")

        # Clean and validate forum_url
        if adapter.get('forum_url'):
            adapter['forum_url'] = adapter['forum_url'].strip()
        else:
            raise DropItem(f"Missing forum_url in {item}")

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

    def validate_text(self, text):
        return bool(text.strip()) and len(text) >= 3

    def validate_date(self, date):
        # Accepts 'YYYY-MM-DD HH:MM:SS UTC' or ISO 8601
        try:
            datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
            return True
        except Exception:
            try:
                datetime.fromisoformat(date)
                return True
            except Exception:
                return False
