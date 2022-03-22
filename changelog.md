### 0.1.0 "Api Changed" 2022/03/22

 * Now, "Tag" is for dynamic Html Tag (with @id/interactions)
 * And, "H" is for static Html tag (without @id/interactions)

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

