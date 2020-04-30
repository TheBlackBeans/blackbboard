# BlackBBoard(1) - virtual boards

Version 1.0, April 2020

```
blackbboard [-h] [-p PENWIDTH] [-s SESSION] [--width WIDTH] [--height HEIGHT] .IP [-f {jpeg,bmp,tga,png}] [-d DIR] [--chunk-size CHUNK_SIZE] [-v] [-P PPP] [-F FPS] [--scale-x SCALE_X] [--scale-y SCALE_Y]
```


<a name="description"></a>

# Description

**BlackBBoard** allows you to create virtual boards and to save them as pages within your current session.

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
* **--chunk-size** _CHUNK\_SIZE_  
  size of each chunk
* **-v**, **--version**  
  show program's version number and exit
* **-P** _PPP_, **--ppp** _PPP_
  inverse speed of scale of penwidth
* **-F** _FPS_, **--fps** _FPS_
  set maximum fps (higher values improve drawing at cost of more ressources)
* **--scale-x** _SCALE\_X_
  set the scale factor corresponding to the number of pixel the screen horizontally moves per pixel the pen moves
* **--scale-y** _SCALE\_Y_
  set the scale factor corresponding to the number of pixel the screen vertically moves per pixel the pen moves

<a name="examples"></a>

# Examples

Most simple usage of this out-of-the-box utilitary

     blackbboard

Specify the name of the session you want to work on (let's say, \`session1',
and the directory to which print the pages (let's say, \`mydir')

     blackbboard -s session1 -d mydir


<a name="bugs"></a>

# Bugs

Report bugs at https://github.com/TheBlackBeans/blackbboard/issues


<a name="author"></a>

# Author

Written by BlackBeans (https://github.com/TheBlackBeans).
