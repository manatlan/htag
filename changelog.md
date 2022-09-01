## 0.8.1 2202/09/01

 - Runner `AndroidApp` could `self.exit()` (to test !)
 
## 0.8.0 "Runners tour" 2022/08/31

 - All runners only accept only one Htag class by default : simpler !
 - Runner `AndroidApp` could `self.exit()` (to test !)
 - Runner `ChromeApp` accept port (`app.run(port=9999)`)
 - Runner `WebHTTP` don't accept multiple htag classes anymore ! Just one (like others !), but got a `serve(...)` method  to allow to hook new http endpoints on others Htag Class (using starlette.add_route(...)): giving a lot more of possibilities ;-)
 - Runner `DevApp` (like WebHTTP) provide a `serve(...)` method, (so you can dev WebHTTP app with DevApp)
 - Runner `BrowserHTTP` manage only the main class/route ("/")
 - all runners (except `PyWebView`) accept query params from url !!! (ex: "/?John%20Doey&p=1" -> (("John Doe",{p:1}) -> can call TagClass(name,p=None) )
   (in the past, only WebHTTP could, but it was complicate). IT WAS MY MOST WANTED/NEEDED FEATURE ;-)
   (All runners manage only one user (except WebHTTP, which can serve multiple clients))
 - the `__main__` on module, create an empty app, with DevApp (if it can pip) or BrowserHTTP (if not)

## 0.7.8 2022/08/28

 - runner `DevApp` can work again on chromebook/penguin (no more weakref/loop/asyncio pickable trouble)


## 0.7.7 "pyscript for one htag class only" 2022/08/27

 - Runner `PyScript` don't accept multiple htag classes anymore ! Just one (like others !)
   (the feature can be done with a simple htag.Tag component (see `examples/navigate_with_hashchange.py`, see Example2 (at top level))
 - So `WebHTTP` runner is the last to accept multiple htag'classes ...

## 0.7.6 2022/08/22

 - BIG CHANGES on how "inherited Tag" allows auto-init property & html_attribut : more consistent (need to have a "**kargs" in init/constructor)
   (could break things on old htag app !!!)
 - remove the old "def _majVersion()", and put it in task/build !
 - add a `__main__` on module, which just create a main.py with "hello world" app, with DevApp runner (and install uvicorn+starlette if needed)

## 0.7.5 "Bye bye guy !" 2022/08/20

  - bye bye GuyApp ... htag is free from guy !
  - more intelligent htag.runners importing (the runner broke with the real exception, and does'nt
    show a warning when external lib is not present)
  - the "Elements" class (the list of tags, created using "+" operator) has now a __str__ method, and should render well ;-)
  - the Caller.prior() method disappear (useless, and htbulma doesn't use it anymore)
  - attrs "on[event]" are now, not None (like "style" & "class"), and can now be used/chained easier


## 0.7.4 2022/07/16

 - can add str to Caller/BaseCaller (new `self.bind(action)` and old `self.bind.<action>()` ) with `+` operator

## 0.7.3 2022/07/11

 - add `tag["style"].__contains__ & __len__`
 - add `tag["class"].__contains__ & __len__`

## 0.7.2 2022/07/10

 - add `tag["style"].dict.update( dict )`

## 0.7.1 "fix style & class" 2022/07/10

 - it works better now ;-)

## 0.7.0 "style & class" 2022/07/10

 - The "DevApp runner" is able to print in stdout (no more python buffering !!!!!) <- really needed for me ;-)
   (it's now the perfect runner for dev process !!!)
 - "style" and "class" are now specials attributs (htag.attrs.StrStyle & htag.attrs.StrClass) on a Tag.
   which provides methods to manage contents (respectivly "dict" & list) !
   But works in the old/classic way, with str !

## 0.6.2 "DevApp runner++" 2022/06/09

 - "DevApp runner" upgraded ! (popup with skip/refresh & full error traceback (py only))
 - meanwhile HRenderer can set special statics list with param statics.

## 0.6.1 "DevApp runner" 2022/06/08

 - "DevApp runner" specialized for dev (autoreload/autorefresh/log)

## 0.6.0 "asgi with starlette" 2022/06/07

 - MINOR BREAKING CHANGES : runners based on starlette (WebHTTP, BrowserStarletteHTTP & BrowserStarletteWS) create an "ASGI HTag Instance"
 - camshot example is better

## 0.5.8 "minor changes" 2022/06/04

 - fix typo in AndroidApp
 - Add an example : examples/camShot.py

## 0.5.7 "htag works on android/apk !!!" 2022/06/02

 - 2 new runners !!!
 - AndroidApp : and it works with buildozer with `android:usesCleartextTraffic="true"` in application of `AndroidManifest.tmpl.xml` !!!
 - BrowserTornadoHTTP : use tornado !

### 0.5.6 2022/06/01

 - Tag.innerHTML is here ;-) readonly (and without @id/Tag, but keeps @ig/TagBase(H)!

### 0.5.5 2022/06/01

 - FIX: the runner BrowserStarletteWS can now change its listening port ;-)

### 0.5.4 "ChromeApp is here" 2022/05/31

 - Add a new runner "ChromeApp", to run in a chrome app mode (without *guy* !)

### 0.5.3 "better js errors" 2022/05/31

 - the "window.error(msg)" can handle all js interactions !

### 0.5.2 "better errors" 2022/05/30

 - the "window.error(msg)" handle js post/next interactions too !
 - !!! PRE js error are not handle yet !!! (things with ex: b"this.value" when calling bindings)

### 0.5.1 "the real 5" 2022/05/30

 - create a js "window.error(msg)" method to manage your own (python) errors

### 0.5.0 "simplest" 2022/05/28

 * add shortcut to create simple basics (as js or css)
 * if a static is str -> add a style / CSS
 * if a static is bytes -> add a script / JS

### 0.4.9 "remove is here" 2022/05/27

 * Tag.remove() to remove itself, (if attached (has parent))

### 0.4.8 "remove is here" 2022/05/10

 * now you can remove a child from a tag with .remove(item) ;-)

### 0.4.7 "pyscript++" 2022/05/10

 * The runner "pyscript" declare statics in the right way in head (fix trouble with script/js)
 * The runner "pyscript" can handle multiple Tag class, and serve the right with #hash (hash == class name, if no, serve the 1st one)

### 0.4.6 "pyscript" 2022/05/07

 * FIX: declare PyScript as runner ;-)

### 0.4.5 "pyscript" 2022/05/07

 * new runner "PyScript" (alpha), so htag can be runned in client side ;-)

### 0.4.4 "nice" 2022/05/05

 * the runner 'BrowserStarletteWS' can be autoreloaded too, with uvicorn/reload'er ... it's now asgi compliant (factory)

### 0.4.3 "going nice" 2022/05/05

 * Tag: better declaration/init of _hr/parent on the instance !
 * better tu test_interactions
 * fix examples
 * add an example, on how to use uvicorn/autoreload

### 0.4.2 "fix fix big breaking changes" 2022/05/04

 * FIX the way add interaction script (post js) with `__call__` : now it works in the init of the main tag too !
 * + tu (new) simu

### 0.4.1 "fix big breaking changes" 2022/05/03

 * FIX the way add interaction script (post js) with `__call__` : now it works like expected

### 0.4.0 "big breaking changes" 2022/05/03

 * BIG/BREAKING CHANGES : The Tag.__init__(...) shouldn't be used anymore : use init() only !!!!!!!
 * BIG/BREAKING CHANGES : all runners/Hrenderer takes tag subclass (no more an instance!), and create the tag instance at construction
 * tag.parent refer to the parent Tag (except the root one, where its parent is None)
 * fix webhttp when post with no htuid
 * nearly 100% tested (tag+render statements)

### 0.3.2  2022/05/02

 * if app set a statics Tag.title is prefered over default one (based on tag name)
 * don't throw a log warning when dynamic tag are included in statics (they are converted to static silently)

### 0.3.1 "runners version" 2022/04/29

 * all runners are upgraded (taking host,port,openBrowser,debug options, and assert) : compatibiliy keeped
 * WebHTTP can takes multiples class now
 * WebHTTP can handle multiple client, multiple Tags ... and give "query_params" to tag constructor (if needed)
 * WebHTTP can take a param "timeout" (by default 5min)
 * runners http with starlette are now compatible with unicorn/reloader !!! exemple:

      app = WebHTTP( MyTag )
      if __name__=="__main__":
          uvicorn.run("main:app",reload=True)


### 0.3.0 "back to future" 2022/04/22

 * Remove "Tag.NoRender" trick (too brain fucked) ... kiss ! (can be simulated easily)
 * if Tag.init() is defined : it will use as a simplified init method (don't mix __init__() & init() ;-) )
   (it's the old ".init(...)" behaviour of gtag)
 * if Tag.render() is defined : Rendering (str) will call it before rendering -> useful for lately rendering (simple dynamic ones)
   (it's the old ".build()" behaviour of gtag)

### 0.2.2 "the 1st good one" 2022/04/22

 * MAJOR VERSION : the lib for runners are not mandatory !!!
   (til now, it didn't worked when no starlette, uvicorn, guy)

### 0.2.1 "killing the braces 2" 2022/04/22

 * new operator on tag/tagbase : "+=" -> same as "<=" ... but "a += b,c"  ===  "a <= (b,c)"
   (but avoid to mix "+=" and "<=" in a same line)


### 0.2.0 "killing the braces" 2022 /04/22

 * new operator on tag/tagbase : "+" -> create a list of tags
   (now, it's easier to add multiple childs in one line :

    - "a <= b+c", instead of "a <= (b,c)"
    - "Tag.div( a+b )" instead of "Tag.div( (a,b) )"

### 0.1.13 2022/04/21

 * add unitests for ".imports"
 * better statics resolver

### 0.1.12 "fixed version" 2022/04/20

 * _renderStatic() -> _ensureTagBase(), returns a TagBase (preserving H/TagBase @id)
 * all unittests are back

### 0.1.11 "bugued version" 2022/04/20

 * IGNORE on test_statics_in_real_statics ;-( ... (so it's a bugued version from scratch, a 0.1.12 will fix soon)
 * Tag.statics : None|Tag(instance)|List|Tuple
 * Tag.imports : None|Tag(class)|List|Tuple
 * _renderStatic() on Tag (no more on Tagbase), preserving H/TagBase @id !

### 0.1.10 2022/04/18

 - tagbase/tag "self._contents" -> "self.childs" : can now access to children, officially !
 - tagbase/tag "self._attrs" -> "self.attrs" : can now access to attributes, officially !
 - effort on typings

### 0.1.9 2022/04/09

 * add more unit tests (tag/render is at 99% cov)
 * add an htagexception when trying to render a caller on something other than a Tag.
 * the "self.bind.<method>()" doesn't return a string anymore, but a BaseCaller object, str'able

### 0.1.8 2022/04/08

 * add a "caller.prior()" which is same concept as bind, but "insert" (instead of append)
   (should be only useful for complex objects which want to make multiple bind, with keeping the same instance
   to be able to pass its own js needs, see "htbulma.inputs" )

### 0.1.7 2022/04/06

 * permit to add a 2nd (and so on) binder 'None' (does nothing)
 * Caller doesn't use self.bind.<method>() anymore ;-)
 * More tu

### 0.1.6 "multi bind" 2022/04/06

 * Multi bind : ability to chain (ex: self.bind(..).bind(..) ). Only the first bind may contains b"js_code" !
 * first TU on new callback system (oufffff)

### 0.1.5 "stream/yield fix" 2022/04/05

 * FIX: yielding list was buggued (in visual stream, not in real content !)

### 0.1.4 "big chamboulement" 2022/04/05

 * The renderer is now "rock solid". Use a custom mechanism to hold weakref to 'id' of tags/generators
   (can't crash silently when "ctypes.cast(oid, ctypes.py_object).value " fail)
 * the newer __on__ (for callbacks) yield correctly now !
 * FIX: multiple self.bind(...) were overriding previous one ;-(
 * ability to stream content (with yield statement in interaction)
 * IMPORTANT : don't call bounded method with double "self" !

### 0.1.3 "bind changer" 2022/04/04

 * add a new sig : self.bind( callback, *a,**k) to bind in context

### 0.1.2 "game changer" 2022/04/03

 * self.bind.<method>(*a,**k) could disappear in next version, replaced
   by the new, more natural, way to bind callbacks

### 0.1.1 "improve it" 2022/03/24

 * runner's BrowserHTTP is more solid (better handle short chunks on http socket) !
 * better logging/info for interaction (describe the method and its args)

### 0.1.0 "Api Changed !" 2022/03/23

 * btw, it should be compatible (at this time !)
 * Now, "Tag" is for dynamic Html Tag (with @id/interactions)
 * And, "H" is for static Html tag (without @id/interactions)
 * BTW, Tag.H is a shortcut to H class
 * runner.BrowserHTTP is more solid, and can handle message <= 8Mo
 * the renderer force statics as real static !!!

### 0.0.17 "better logging" 2022/03/22

 * better logging.info to see `**NoRender**`

### 0.0.16 "@Tag.NoRender" 2022/03/22

 * the decoraton "@Tag.NoRender" for an interaction, avoid rendering itself !
 * the return thing is gone (yield or return should return none only)

### 0.0.15 "return of return, act final" 2022/03/21

 * BUT I DON'T LIKE THAT, and it will probably change (return is not the good way !)
 * the "don't redraw itself" is more clever (now, in stater.guess)
 * with unittests ^^

### 0.0.14 "return of return, act2" 2022/03/20

 * FIX : avoid redrawing itself is more clever

### 0.0.13 "return of return, act1" 2022/03/20

 * actions.update is now a dict
 * interaction can now "return 0" to avoid redrawing itself

### 0.0.12 "Back to the source" 2022/03/19

 * statics discovering is now based on static class declaration (no more dynamic)

### 0.0.11 "better js discovering" 2022/03/19

 * now, it's able to find (init)script/js from Tag embbeded in TagBase !!!
 * tagbase.__repr__ shortened (no more all attrs, juste the @id if present)
 * logger.debug for tag rendering, in general
 * logger.debug for state/guesser
 * more tests

### 0.0.10 "tagbase setter!" 2022/03/18

 * no more "space" between childs in tagbase.__str__ (rendering)
 * Add tagbase.set(), to clear+add objects
 * tagbase.set() & tagbase.add() & tagbase() can takes iterables now ;-)
 * FIX : when error in interact, log/info the return {err:"xxx"}
 * minor comments

### 0.0.9 "state log" 2022/03/17

 * log/debug for Stater.guess() (before+after state of changeds tags)

### 0.0.8 "catch interact error" 2022/03/16

 * log/debug for Tag.__str__()
 * log/error for exceptions in py interactions.
 * front display a console.log for server err
 * more tests

### 0.0.7 "use logging" 2022/03/16

 * use logging
 * IIFE can be generated for "//comment"

### 0.0.6 "new name" 2022/03/14

 * Rename all from "thag" to new name : "htag"

### 0.0.5 "the third patch" 2022/03/12

 * Statics discovering didn't work well for Tags "builded lately" (whose override __str__)

### 0.0.4 "the second patch" 2022/03/12

 * Statics discovering couldn't include those inside TagBase ;-(

### 0.0.3 "the first patch" 2022/03/12

 * "Intelligent rendering" didn't work for Tags "builded lately" (whose override __str__)

### 0.0.2 "initial public release" 2022/03/12

 * initial public release
 * there was a "0.0.1" before (never released)

