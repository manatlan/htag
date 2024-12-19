##################################################################################################
## the common framework between the github action : .github/workflows/selenium.yaml and IRL
##################################################################################################

import time,sys,os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from multiprocessing import Process

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
            time.sleep(1)
        except Exception as e:
            print("***HClient ERROR***",e)

    def find(self,xp:str) -> list:
        print("FIND:",xp)
        return self.driver.find_elements(By.XPATH, xp)

    def wait(self,nbs):
        time.sleep(nbs)

def run(App,runner:str,openBrowser=True,port=8000):
    assert runner in ("PyScript","WS","HTTP")
    print("App runned in",runner)

    if runner=="PyScript":
        """
        This thing is complex to test/develop (need to py-env the wheel), you'll need to do :
        - poetry build                                              # to produce dist/htag-0.0.0-py3-none-any.whl
        - python3 -m http.server 8001
        - chrome http://localhost:8001/manual_pyscript.html

        """
        content = """<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.10.2/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.10.2/core.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body> Starting pyscript ;-)

<script type="py" config='{"packages":["./dist/htag-0.0.0-py3-none-any.whl"]}'>
###############################################################################

%s

###############################################################################
from htag.runners import PyScript

PyScript( App  ).run()

</script>
</body>
</html>"""

        import inspect,re
        import http.server
        import socketserver
        import webbrowser

        src = re.search(r"#<code>(.+)#</code>", open(inspect.getsourcefile(App)).read(),re.DOTALL)
        if src:
            src=src.group(1).strip()
        else:
            print("This app is not pyscript'able (miss '#<code>(.+)#</code>')")
            sys.exit(-1)
        try:
            with open("index.html","w+") as fid:
                fid.write(content % src)

            Handler = http.server.SimpleHTTPRequestHandler
            try:
                with socketserver.TCPServer(("", port), Handler) as httpd:
                    print("serving at port", port)
                    if openBrowser:
                        webbrowser.open_new_tab(f"http://localhost:{port}")
                    httpd.serve_forever()
            except Exception as e:
                print("can't start httpd server",e)
                sys.exit(-1)
        finally:
            os.unlink("index.html")
    elif runner == "WS":
        from htag.runners import Runner
        Runner(App,port=port,interface = 1 if openBrowser else 0).run()
    elif runner == "HTTP":
        from htag.runners import Runner
        Runner(App,port=port,interface = 1 if openBrowser else 0,http_only=True).run()

def test(App,runner:str, tests):
    """ for test on a local machine only """
    Process(target=run, args=(App, runner, False)).start()
    with webdriver.Chrome() as driver:
        driver.get("http://127.0.0.1:8000/")
        x=testDriver(driver,tests)
        print("-->",x and "OK" or "KO")

def testDriver(driver,tests):
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- # pyscript specific
    time.sleep(1)
    hc=HClient(driver)
    while 1:
        bodys=hc.find("//body")
        if bodys and ("Starting" not in bodys[0].text):
            break
        time.sleep(1)
    print("Start")
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    return tests( hc )

def normalRun(App):
    """ just for test/dev in a normal context """
    from htag.runners import Runner
    Runner(App,interface = 1,use_first_free_port=True).run()    # run in all cases (find a free port automatically)