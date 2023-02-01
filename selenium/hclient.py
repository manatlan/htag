##################################################################################################
## the common framework between the github action : .github/workflows/selenium.yaml and IRL
##################################################################################################

import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from multiprocessing import Process
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class HClient:
    def __init__(self,driver):
        self.driver=driver

    @property
    def title(self):
        return self.driver.title

    def click(self,xp:str):
        print("CLICK:",xp)
        try:
            self.driver.find_element(By.XPATH, xp).click()
            time.sleep(0.5)
        except Exception as e:
            print("***HClient ERROR***",e)

    def find(self,xp:str) -> list:
        print("FIND:",xp)
        return self.driver.find_elements(By.XPATH, xp)

    def wait(self,nbs):
        time.sleep(nbs)

def run(App,runner:str,openBrowser=True):
    import htag.runners
    getattr(htag.runners,runner)(App).run(openBrowser=openBrowser)

def test(App,runner:str, tests):
    """ for test on a local machine only """
    Process(target=run, args=(App, runner, False)).start()
    with webdriver.Chrome() as driver:
        driver.get("http://127.0.0.1:8000/")
        x=tests( HClient(driver) )
        print("-->",x and "OK" or "KO")




