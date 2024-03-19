##################################################################################################
## Run the selenium test on port 'sys.argv[1]' with the App 'sys.argv[2]'
## used by github action : .github/workflows/selenium.yaml
##################################################################################################

import sys,os,time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
try:
    from webdriver_manager.core.utils import ChromeType
except ImportError:
    from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import hclient


import importlib
#######################################################
port = sys.argv[1]
tests=importlib.import_module(sys.argv[2]).tests
#######################################################

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

with webdriver.Chrome(service=chrome_service, options=chrome_options) as driver:
    driver.get('http://localhost:'+port)
    x=hclient.testDriver(driver,tests)

if x:
    print("----> OK")
    sys.exit(0)
else:
    print("----> KO")
    sys.exit(-1)
