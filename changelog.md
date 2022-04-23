### 0.2.0 "killing the braces" 2022/04/22

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

