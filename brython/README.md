# HTag for Brython

[Brython](https://brython.info/) is a marvelous implementation of py3 in javascript, and here is an **htag.Tag** implem for brython.
The goal of this side htag project, is to provide a brython's htag way to creat component which are compatible with **htag** and **brython**.

Put this line in your html file :
```html
   <script type="text/python" src="https://raw.githubusercontent.com/manatlan/htag/main/brython/htag.txt" id="htag"></script>
```
In a `<script type="text/python">`, you can now add:

```python
   from htag import Tag
```
And you can create your componant, as you could do, with real [htag](https://github.com/manatlan/htag/) (NOT FOR THE MOMENT)

See [Example1](https://raw.githack.com/manatlan/htag/main/brython/example1.html) (using [shoelace](https://shoelace.style/) too)

