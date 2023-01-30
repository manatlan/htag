# taken from https://github.com/jsoma/selenium-github-actions

import sys
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

port = sys.argv[1]

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.get('http://localhost:'+port)

#######################################################
from app2 import tests
#######################################################
x=tests(driver)

driver.quit()
print(x and "ok" or "ko")