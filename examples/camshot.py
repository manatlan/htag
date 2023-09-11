import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from htag import Tag

class Cam(Tag.video):
    """ Htag component to start the cam, and to take screnshot (by clicking on it)"""

    # some javascripts needed for the component
    statics = Tag.script("""
function startCam(video) {
    navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
    })
    .then(function(stream) {
        video.srcObject = stream;
        video.play();
    })
    .catch(function(err) {
        const o = document.createElement("div");
        o.innerHTML = "NO CAMERA: " + err;
        video.replaceWith(o);
    });
}

function takeCamShot(video) {
    let {width, height} = video.srcObject.getTracks()[0].getSettings();

    let canvas = document.createElement("canvas");
    let context = canvas.getContext('2d');
    canvas.width = width;
    canvas.height = height;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}
""")

    # js which will be executed, each time the component is appended
    js = """startCam(tag);"""

    def init(self,callback=None,width=300,height=300):
        self.width=width
        self.height=height
        self["style"]=f"width:{width}px;height:{height}px;border:1px solid black"
        if callback:
            self["onclick"]=self.bind( callback, b"takeCamShot(this)" )

class App(Tag.body):
    """ An Htag App to handle the camera, screenshots are displayed in the flow"""

    statics = b"function error(m) {alert(m)}"

    def init(self):
        self <= Cam(self.takeShot)

    def takeShot(self,o,dataurl):
        self <= Tag.img(_src=dataurl,_style="max-width:%spx;max-height:%spx;" % (o.width,o.height))



if __name__=="__main__":
    from htag.runners import *
    # r=PyWebWiew( App )
    # r=BrowserStarletteHTTP( App )
    # r=BrowserStarletteWS( App )
    # r=BrowserHTTP( App )
    r=BrowserTornadoHTTP( App )
    r.run()

