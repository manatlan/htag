from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import threading,sys,os
from multiprocessing import Process

from htag import Tag # the only thing you'll need ;-)
# from htag.runners import BrowserHTTP as Runner
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

def run(runner,app):
    print("="*79)
    print("RUN",runner.__name__)
    print("="*79)

    app=runner( app.App )
    app.run(openBrowser=False)

def test(driver,app):
    print("Test",driver)
    driver= driver()
    driver.get("http://127.0.0.1:8000/")
    x=app.tests(driver)
    driver.quit()
    return x



if __name__ == "__main__":
    # browsers = [webdriver.Chrome]
    # runners = [BrowserStarletteHTTP]
    browsers = [webdriver.Chrome,webdriver.Firefox]
    runners = [BrowserStarletteHTTP,BrowserStarletteWS,BrowserHTTP,BrowserTornadoHTTP]
    apps=[APP1]
    for app in apps:
        for driver in browsers:
            for runner in runners:
                Process(target=run, args=(runner,app,)).start()
                x=test(driver,app)
                print("-->",x and "OK" or "KO")
        # Process(target=run, args=(WebHTTP,)).start()
        # test(driver)

