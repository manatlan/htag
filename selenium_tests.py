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

class APP2:
    """ construction and call events """

    class App(Tag.div):
        statics = b"var VALUE=42;var GLOBS={};"
        imports=[]

        def init(self):
            # * the .js can use 'self' at start
            # * it can get back a own html attribut
            # * it can get back a global var (from statics)
            assert self.tag=="div"  #sill a div, coz not rendered !
            self["data"]=1
            self.js = self.bind.step1( b"parseInt(self.getAttribute('data'))+VALUE" )

        def step1(self,v):
            # * the .js started the step1
            # * the .js is cleared (to avoid loop on rendering)
            # * the tag has no childs at start
            # * the tag has one attr
            # * the += operator works
            # * the <= operator works
            # * the add operator works
            # * the form self.call( self.bind ) works
            assert self.tag=="body"  #converted to body, as it's the main tag
            assert v==43
            assert len(self.childs)==0
            assert len(self.attrs)==1
            self.js=None
            self += Tag.li()
            self <= Tag.li()
            self.add( Tag.li() )
            self.call( self.bind.step2( len(self.childs), b"self.childNodes.length" ))

        def step2(self,nb1,nb2,add=12):
            # * the childs are ok (front & back)
            # * the default parameter is setted
            # * the clear method works
            # * yielding work as expected
            # * the new form self.call.method() works
            assert nb1==nb2==3
            assert len(self.childs)==3
            assert nb1+nb2+add==18
            self.clear()
            self <= Tag.div(1)
            yield Tag.div(2)
            yield Tag.div(3)
            yield Tag.div(4)
            self.call.step3(len(self.childs), b"self.childNodes.length")

        def step3(self,nb1,nb2):
            # * the childs are ok (front & back)
            # * the set method works
            # * we can create custom tag_name
            # * we can create a placeholder
            # * can set global vars from statics & reuse them, in self.call
            assert nb1==nb2==4
            self.set(Tag.my_tag("contentx"))
            self.call( "GLOBS.t1=self.innerHTML;" )
            yield
            self.set(Tag("content"))
            self.call( "GLOBS.t2=self.innerHTML;" )
            self.call.step4( b"GLOBS.t1",b"GLOBS.t2")

        def step4(self,v1,v2):
            # assert self.childs[0].tot==1
            self.clear()
            assert v1.startswith("<my-tag id=")
            assert v1.endswith("</my-tag>")
            assert v2=="content"
            self <= Tag.button("exit",_onclick = lambda o: self.exit())


    @staticmethod
    def tests(driver):
        assert "App" in driver.title

        driver.implicitly_wait(2) # seconds

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
    apps=[APP1,APP2]
    for app in apps:
        for driver in browsers:
            for runner in runners:
                Process(target=run, args=(runner,app,)).start()
                x=test(driver,app)
                print("-->",x and "OK" or "KO")

    # BrowserStarletteHTTP( APP2.App ).run()