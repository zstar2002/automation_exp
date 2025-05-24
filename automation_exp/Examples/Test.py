from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium import webdriver

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
CHROMEDRIVER_PATH = ChromeDriverManager().install() 
driver = webdriver.Chrome(
    service=Service(CHROMEDRIVER_PATH),
    options=chrome_options
)   
driver.get('http://pythonscraping.com/pages/javascript/ajaxDemo.html')
time.sleep(10)  # Wait for the page to load
print(driver.find_element(By.ID, 'content').text)
driver.close()