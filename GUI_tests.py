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

########################################################################################################
from htag import Tag
from htag.runners import *

class APP1:
    """ the basic """

    class App(Tag.body):
        def init(self):
            def say_hello(o):
                self <= Tag.li("hello")
            self<= Tag.button("click",_onclick = say_hello)
            self<= Tag.button("exit",_onclick = lambda o: self.exit())

    @staticmethod
    def tests(driver):
        assert "App" in driver.title

        driver.find_element(By.XPATH, '//button[text()="click"]').click()
        driver.find_element(By.XPATH, '//button[text()="click"]').click()
        driver.find_element(By.XPATH, '//button[text()="click"]').click()

        assert len(driver.find_elements(By.XPATH, '//li'))==3

        driver.find_element(By.XPATH, '//button[text()="exit"]').click()
        return True

########################################################################################################
#from multiprocessing import Process
import threading

def run(runner,App):
    print("="*79)
    print("RUN",runner.__name__)
    print("="*79)
    runner( App ).run(openBrowser=False)


app=APP1
#Process(target=run, args=(BrowserHTTP,app.App,)).start()
threading.Thread(target=run, args=(BrowserHTTP,app.App,)).start()

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.get('http://localhost:8000')
assert app.tests(driver)
driver.quit()
