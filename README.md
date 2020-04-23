# board(1) - virtual boards

Version 1.0, April 2020

```
./main.py [-h] [-p PENWIDTH] [-s SESSION] [--width WIDTH] [--height HEIGHT] .IP [-f {jpeg,bmp,tga,png}] [-d DIR] [--canvas-mul CANVAS_MUL] [-v]
```


<a name="description"></a>

# Description

**Board** allows you to create virtual boards and to save them as pages within your current session.

Use left click to draw, right click to erase, middle click to scroll.

Use [s] to save a page (what you currently see).

Your pages will be at _dir_/_session_-_page_._format_, where _page_ is an integer representing the n-th page saved in the current session.


<a name="options"></a>

# Options


<a name="optional-arguments"></a>

### optional arguments:


* **-h**, **--help**  
  show this help message and exit
* **-p** _PENWIDTH_, **--penwidth** _PENWIDTH_  
  width of the pen
* **-s** _SESSION_, **--session** _SESSION_  
  session name
* **--width** _WIDTH_  
  set the width of the window
* **--height** _HEIGHT_  
  set the height of the window
* **-f** {jpeg,bmp,tga,png}, **--format** {jpeg,bmp,tga,png}  
  format of output files
* **-d** _DIR_, **--dir** _DIR_  
  target directory to save session pages
* **--canvas-mul** _CANVAS\_MUL_  
  Real canvas size respect to window size
* **-v**, **--version**  
  show program's version number and exit
  

<a name="examples"></a>

# Examples

Most simple usage of this out-of-the-box utilitary

     ./main.py

Specify the name of the session you want to work on (let's say, \`session1',
and the directory to which print the pages (let's say, \`mydir')

     ./main.py -s session1 -d mydir


<a name="bugs"></a>

# Bugs

Report bugs at https://github.com/TheBlackBeans/board/issues


<a name="author"></a>

# Author

Written by BlackBeans (https://github.com/TheBlackBeans).
