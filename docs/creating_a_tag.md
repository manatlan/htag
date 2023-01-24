# Creating a Tag : the complete guide

if you come from [domonic](https://github.com/byteface/domonic) or brython

## the basics

A Tag (htag's Tag) is a helper to let you build easily html representation of an object.

```python
from htag import Tag

print( Tag.div("hello world") )
```
Will generate `<div>hello world</div>` ... easy ;-)

If you want to set html attributs, prefix them with '_'

```python
print( Tag.div("hello world", _style="background:yellow") )
```
Will generate `<div style="background:yellow">hello world</div>` ;-)

It will work for every kind of html attributs, and events too

```python
print( Tag.div("hello world", _onclick="alert(42)") )
```
Will generate `<div onclick="alert(42)">hello world</div>` ;-)

... TODO ...

## Inherit a Tag

It's the main purpose of Htag : create feature rich components on python side ...

... TODO ...
