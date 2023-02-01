# taken from https://github.com/jsoma/selenium-github-actions

import sys,os,time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import hclient

#######################################################
port = sys.argv[1]
import importlib
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
    x=tests(hclient.HClient(driver))
    print(x and ">OK<" or ">KO<")