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

