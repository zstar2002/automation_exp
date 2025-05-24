from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
CHROMEDRIVER_PATH = ChromeDriverManager().install() 
driver = webdriver.Chrome(
    service=Service(CHROMEDRIVER_PATH),
    options=chrome_options
)
driver.get('http://pythonscraping.com/pages/javascript/redirectDemo1.html')
try:
    # Wait for the element with ID 'content' to be present
    txt = 'This is the page you are looking for!'
    bodyElement = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, f'//body[contains(text(), "{txt}")]'))
    )
    print(bodyElement.text)
except TimeoutException:
    print('Did not find the element')