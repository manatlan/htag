# HTag for Brython

[Brython](https://brython.info/) is a marvelous implementation of py3 in javascript, and here is an **htag.Tag** implem for brython.
The goal of this side htag project, is to provide a brython's htag way to create components whose could be compatibles with **htag** and **brython**.

In fact, it's just It's a class helper, to facilitate the creation of html element.

In this repo, you will find :

 - [htag.txt](https://github.com/manatlan/htag/blob/main/brython/htag.txt) : the minimal implementation (to use with brython)
 - `htagfull.txt` : a more complete implem ... **when it will be ready** ;-)
 - somes examples
 - [bryted](https://raw.githack.com/manatlan/htag/main/brython/bryted.html) : an online editor to test brython'htag components (made with brython'htag) **PREVERSION**


## Instructions
Put this line in your html file :
```html
<script type="text/python" src="https://raw.githubusercontent.com/manatlan/htag/main/brython/htag.txt" id="htag"></script>
```
In a `<script type="text/python">`, you can now add:

```python
from htag import Tag
```
And you can create components, nearly as you could do, with the real [htag](https://github.com/manatlan/htag/).

ex:
In pure brython, you'll have to create your element like that:
```python
from browser import html

def test(ev):
    window.alert(ev.target.kiki)

b=html.BUTTON("tag",style="color:red")
b.kiki = 42
b.bind("click",test)

document <= b
```

With **Tag**, you can do it, in one line, like that :

```python
from htag import Tag

def test(ev):
    window.alert(ev.target.kiki)

document <= Tag.button("tag", kiki=42, _style="color:red", _onclick=test)
```
It's exactly the same but:
 - parameters starting with '_' are attributs for the html element (those starting with "_on" are event binded)
 - others are property on the node instance.
 - Here it will produce a `<button>`, but you can produce whatever you want.

Ex:
```python
document <= Tag.sl_color_picker( _onsl_change = onchanged )
```
will produce something like `<sl-color-picker></sl-color-picker>`, with an auto-binded event on "sl-change".

And best of all, you can easily craft components

```python
class MyComponent(Tag.sl_card):
    " a component in the htag's style "
    def init(self,txt):
        self.txt=txt
        self+=Tag.sl_button(f"add {txt}",_onclick=self.addline)
		
    def addline(self,ev):
        self += Tag.li(self.txt)

document <= MyComponent("C1")
document <= MyComponent("C2")
```
And like with real **htag** : this component is "closed", because it won't accept redefinition at construction time. If you want to "open" it, to be able to redefine some attributs : change its `init` method to :

```python
    def init(self,txt, **a):
```
and now, you can surcharge it (or not) at construction phase, like that :
```python
document <= MyComponent("C3", _class="myclass", _onmouseover= .... )
```
It's a special, and useful, trick


## Examples
- See [Example 1](https://raw.githack.com/manatlan/htag/main/brython/example1.html) (using [shoelace](https://shoelace.style/) web components)
- See [Example 2](https://raw.githack.com/manatlan/htag/main/brython/example2.html) (using the "ace editor" as a Tag Component (using statics and wait load))

