# HTag for Brython

[Brython](https://brython.info/) is a marvelous implementation of py3 in javascript, and here is an **htag.Tag** implem for brython.
The goal of this side htag project, is to provide a brython's htag way to create components which are compatibles with **htag** and **brython**.

In this repo, you will find :

 - [htag.txt](https://github.com/manatlan/htag/blob/main/brython/htag.txt) : A minimal implementation (to use with brython)
 - `htagfull.txt` : a more complete implem ... **when it will be ready** ;-)
 - somes examples


## Instructions
Put this line in your html file :
```html
<script type="text/python" src="https://raw.githubusercontent.com/manatlan/htag/main/brython/htag.txt" id="htag"></script>
```
In a `<script type="text/python">`, you can now add:

```python
from htag import Tag
```
And you can create your components, as you could do, with real [htag](https://github.com/manatlan/htag/) (NOT 100% compatible for now)

```html
<script type="text/python">
from browser import document,window
from htag import Tag

document <= Tag.button("Say Hi", _style="color:red", _onclick=lambda ev: window.alert('hello world'))
</script>
```


## Examples
See [Example 1](https://raw.githack.com/manatlan/htag/main/brython/example1.html) (using [shoelace](https://shoelace.style/) too)

