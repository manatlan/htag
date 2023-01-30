from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import threading,sys,os
from multiprocessing import Process

"""
Tests on my local dev machine ...
Just for me ;-)

"""

from htag.runners import *


def run(runner,klass):
    print("="*79)
    print("RUN",runner.__name__)
    print("="*79)

    app=runner( klass )
    app.run(openBrowser=False)

def test(driver,app):
    print("Test",driver)
    driver= driver()
    driver.get("http://127.0.0.1:8000/")
    x=app.tests(driver)
    driver.quit()
    return x

import app2 as app

if __name__ == "__main__":
    # browsers = [webdriver.Chrome,webdriver.Firefox]
    # runners = [BrowserStarletteHTTP,BrowserStarletteWS,BrowserHTTP,BrowserTornadoHTTP]
    browsers = [webdriver.Chrome]
    runners = [BrowserStarletteHTTP]


    # for driver in browsers:
    #     for runner in runners:
    #         Process(target=run, args=(runner,app.App,)).start()
    #         x=test(driver,app)
    #         print("-->",x and "OK" or "KO")

    BrowserStarletteWS( app.App ).run()