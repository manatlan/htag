# JS bidirectionnal (@expose)

Sometimes, when using a JS lib, with heavy/bidirectionnal interactions : you 'll need to call js and receive events from JS. You can do that by using a `@expose` decorator.

Here is a "audio player" tag, which expose a python "play' method, and a "event" method (whil will be decorated) to receive event from the js side. Here is the best way to do it :

```python
from htag import Tag, expose

class APlayer(Tag.div):
    statics=Tag.script(_src="https://cdnjs.cloudflare.com/ajax/libs/howler/2.2.4/howler.min.js")
    
    def init(self):
        self.js="""

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

    @expose
    def event(self,name,url):
        self+=f"EVENT: {name} {url}"
```
