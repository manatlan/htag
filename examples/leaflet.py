import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from htag import Tag

class LeafLet(Tag.div):
    statics =[
        Tag.link(_href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css",_rel="stylesheet"),
        Tag.script(_src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js"),
    ]

    def init(self,lat:float,long:float,zoom:int=13):
        self["style"]="height:300px;width:300px;border:2px solid black;display:inline-block;margin:2px;"
        self.js = f"""
var map = L.map('{id(self)}').setView([{lat}, {long}], {zoom});

L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
{{
    attribution: 'LeafLet',
    maxZoom: 17,
    minZoom: 9
}}).addTo(map);
"""

class App(Tag.body):

    def init(self):
        self <= LeafLet(51.505, -0.09)          #london, uk
        self <= LeafLet(42.35,-71.08)           #Boston, usa

        self.call(   """navigator.geolocation.getCurrentPosition((position)=>{%s});"""
                % self.bind.add_me(b"position.coords.latitude",b"position.coords.longitude")
        )

    def add_me(self,lat,long):
        self <= Tag.div(f"And you could be near here: ({lat},{long}):")
        self <= LeafLet(lat,long)


from htag.runners import DevApp

app=DevApp(App)

if __name__=="__main__":
    app.run()
