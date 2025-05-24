from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
CHROMEDRIVER_PATH = ChromeDriverManager().install() 
driver = webdriver.Chrome(
    service=Service(CHROMEDRIVER_PATH),
    options=chrome_options
)
driver.get('http://pythonscraping.com/pages/javascript/ajaxDemo.html')
try:
    # Wait for the element with ID 'content' to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'loadedButton'))
    )
finally:
    print(driver.find_element(By.ID, 'content').text)
    driver.close()