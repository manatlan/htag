# taken from https://github.com/jsoma/selenium-github-actions

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)


driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.get('http://localhost:8000')

assert "App" in driver.title

driver.find_element(By.XPATH, '//button[text()="click"]').click()
driver.find_element(By.XPATH, '//button[text()="click"]').click()
driver.find_element(By.XPATH, '//button[text()="click"]').click()

assert len(driver.find_elements(By.XPATH, '//li'))==3

driver.find_element(By.XPATH, '//button[text()="exit"]').click()

driver.quit()
print("ok")