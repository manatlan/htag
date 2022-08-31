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
 * `/` -> will result in http/400 (because `name` is mandatory)

**Remarks:**

 * TODO: complete here (http/400 when mandatory ..)
 * all query params are string. It's up to you to cast to your needs.
