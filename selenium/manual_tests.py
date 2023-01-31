from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import threading,sys,os
from multiprocessing import Process

"""
Tests on my local dev machine ...
Just for me ;-)

"""



def run(runner,klass):
    print("="*79)
    print("RUN",runner.__name__)
    print("="*79)

    app=runner( klass )
    app.run(openBrowser=False)


import app2 as app
from common import HClient
from htag.runners import *

# a=DevApp( app.App )
# if __name__ == "__main__":
#     a.run(); quit()

if __name__ == "__main__":
    # browsers = [webdriver.Chrome,webdriver.Firefox]
    # runners = [BrowserStarletteHTTP,BrowserStarletteWS,BrowserHTTP,BrowserTornadoHTTP]
    browsers = [webdriver.Chrome]
    runners = [BrowserStarletteHTTP]

    for dbrowser in browsers:
        for runner in runners:
            Process(target=run, args=(runner,app.App,)).start()

            with dbrowser() as driver:
                driver.get("http://127.0.0.1:8000/")
                x=app.tests( HClient(driver) )
                print("-->",x and "OK" or "KO")

