# Creating a Tag : the complete guide

If you come from [domonic](https://github.com/byteface/domonic) or [brython](https://brython.info/static_doc/fr/create.html) : htag borrows the best ideas from them.

## the basics

### at construction time
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

You can construct whatever tag you want ...

```python
print( Tag.my_tag("hello world", _class="mine") )
```
Will generate `<my-tag class="mine">hello world</my-tag>` (notice that the `_` is replaced by `-` ;-)

```python
print( Tag.span("hello world", _val=12, _checked=True) )
```
Will generate `<span val="12" checked>hello world</span>` !

It's simple ;-)

But you can init some instance properties at construction time ...
```python
tag = Tag.span("hello world", value=12, _value=42 )
print( tag )
```
Will generate `<span value="42">hello world</span>`, but the instance var (here `tag`) will contain 12 ( tag.value==12 ) !
So `_value` is an html attribut ... whereas `value` is an instance property (on python side only). It's important to understand the difference.

Take a break, and medit on that ;-)

You can compose tags ...
```python
Tag.div( Tag.span("hello")+" "+Tag.b("world") )
# or
Tag.div( [Tag.span("hello")," ",Tag.b("world")] )
```
it's basically the same thing ^^

### post construction time

all this variables are usable/settable post construction time.
```python
tag = Tag.span("hello world", value=12, _value=42 )
assert tag["value"]=="42"
assert tag.value==12
```
html attributs are in the dictitem of the tag ! Whereas the instance properties are in the instance ;-)

So you can do that:
```python
tag = Tag.a("hello world")
tag["onclick"]="alert(42)"
```
And you can compose them like that :

```python
div=Tag.div()
div.add( Tag.span("hello") )
div.add( " " )
div.add( Tag.b("world") )
```

but there are operators (`+=` (prefer) or `<=` (brython style)), to simplify that :
```python
div = Tag.div()
div += Tag.span("hello") )
div += " "
div += Tag.b("world")
```

easy, no ?

### IRL

An important thing to understand, is that a Tag renders differently when used in a runner (TODO LINK).
AS you see before, the tags are rendered without attributs 'id'. But, IRL, when using in a htag runner context, all tags are rendered with an html id attribut (it's the main reason why you can't set an `_id` at runtime !). Htag's runner manage all the tags, with theirs ids: it's the core feature, to be able to keep states/rendering between the gui/client_side and the back/python ;-)


... TODO ...

## Inherit a Tag

It's the main purpose of Htag : create feature rich components on python side ...

... TODO ...
