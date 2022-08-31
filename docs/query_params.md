# Can instanciate with url/query params

In most runners, you can use "query parameters" (from the url) to instanciate your htag main class.

Admit that your main class looks like that :

```python

class MyTag(Tag.div):
    def init(self,name,age=12):
        ...

```

If can point your running App to urls like:

 * `/?name=john&age=12` -> will create the instance `MyTag("john",'12')`
 * `/?Jim&42` -> will create the instance `MyTag("Jim",'42')`
 * `/?Jo` -> will create the instance `MyTag("Jo",12)`

As long as parameters, fulfill the signature of the constructor : it will construct the instance with them.
If it doesn't fit : it try to construct the instance with no parameters !

So things like that :

 * `/` -> will result in http/400, **because `name` is mandatory** in all cases !!

BTW, if your class looks like that (with `**a` trick, to accept html attributes or property instance)

```python
class MyTag(Tag.div):
    def init(self,name,age=12,**a):
        ...
```
things like that, will work :

* `/?Jim&_style=background:red` -> will create the instance `MyTag("Jim",'42')`, and change the default bg color of the instance.

So, it's a **best practice**, to not have the `**a` trick in the constructor of main htag class (the one which is runned by the runner)

**Remarks:**

 * all query params are string. It's up to you to cast to your needs.
 * this feature comes with htag >= 0.8.0
