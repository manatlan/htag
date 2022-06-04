import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from htag import Tag

class Cam(Tag.video):
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
        alert("An error occurred: " + err);
    });
}

function takeCamShot(video,width,height) {
    let canvas = document.createElement("canvas");
    let context = canvas.getContext('2d');
    canvas.width = width;
    canvas.height = height;
    context.drawImage(video, 0, 0, width, height);
    return canvas.toDataURL('image/jpeg');
}
""")

    js = """startCam(tag);"""

    def init(self,callback=None,width=320,height=240):
        self["style"]=f"width:{width}px;height:{height}px;border:1px solid black"
        if callback:
            self["onclick"]=self.bind( callback, bytes("takeCamShot(this,%s,%s)" % (width,height),"utf8") )

class App(Tag.body):
    statics = b"function error(m) {alert(m)}"

    def init(self):
        self <= Tag.p("Click on the video, to take a screenshot ;-)")
        self <= Cam(self.takeShot)

    def takeShot(self,o,dataurl):
        self <= Tag.img(_src=dataurl)



if __name__=="__main__":
    from htag.runners import *
    # r=GuyApp( App )
    # r=PyWebWiew( App )
    # r=BrowserStarletteHTTP( App )
    # r=BrowserStarletteWS( App )
    # r=BrowserHTTP( App )
    r=BrowserTornadoHTTP( App )
    # r=WebHTTP( Page )
    r.run()

