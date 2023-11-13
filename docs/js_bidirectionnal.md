# JS bidirectionnal

Sometimes, when using a JS lib, with heavy/bidirectionnal interactions : you 'll need to call js and receive events from JS.
The best practice (currently) is :

Here is a "audio player" tag, which expose a python "play' method, and a "event" method to receive event from the js side. Here is the best way to do it :

```python
from htag import Tag

class APlayer(Tag.div):
    statics=Tag.script(_src="https://cdnjs.cloudflare.com/ajax/libs/howler/2.2.4/howler.min.js")
    
    def init(self):
        self.js="""

self.event=function(...args) {%s};

self.play= function(url) {
    if(this._hp) {
        this._hp.stop();
        this._hp.unload();
    }
    
    this._hp = new Howl({
      src: [url],
      autoplay: true,
      loop: false,
      volume: 1,
      onend: function() {
        self.event("end",url);
      }
    });
    
}
    """ % self.bind.event(b"args")

    def play(self,url):
        self.call( f"self.play(`{url}`)" )
    def event(self,*args):
        self+="EVENT: %s" % args
```
