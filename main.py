#!/usr/bin/python3

# BlackBBoard -- virtual boards

###############
### IMPORTS ###
###############

import sys, os, argparse, datetime, math, functools, tarfile, io, time
from PIL import Image



#############
#### V&A ####
#############

__version__ = "1.0"
__author__ = "BlackBeans"



###########################
## COMMANDLINE ARGUMENTS ##
###########################

parser = argparse.ArgumentParser(
    prog='BlackBBoard',
    description='''\
BlackBBoard: WYSIWYG interactive board
----------------------------------

Lets you save into session pages the result.\
''',
    epilog='Program made by BlackBeans',
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument('-p', '--penwidth', help='width of the pen', default=4, type=int)
parser.add_argument('-s', '--session', help='session name', default='%Y-%m-%d-%H-%M-%S')
parser.add_argument('--width', help='set the width of the window', type=int, default=1280)
parser.add_argument('--height', help='set the height of the window', type=int, default=1024)
parser.add_argument('-f', '--format', help='format of output files', default='png', choices={'string', 'png', 'jpeg', 'bmp', 'tga'})
parser.add_argument('-d', '--dir', help='target directory to save session pages', default='blackbboard')
parser.add_argument('--chunk-size', type=int, help='size of each chunk', default=300)
parser.add_argument('-v', '--version', action='version', version='%(prog)s '+__version__)
parser.add_argument('-P', '--ppp', help='inverse speed of scale of pen width', default=20, type=int)
parser.add_argument('-F', '--fps', help='set maximum fps (higher values improve drawing at cost of more ressources)', default=60, type=int)
parser.add_argument('--scale-x', help='set the scale factor corresponding to the number of pixel the screen horizontally moves per pixel the pen moves', type=int, default=1)
parser.add_argument('--scale-y', help='set the scale factor corresponding to the number of pixel the screen vertically moves per pixel the pen moves', type=int, default=1)
args = parser.parse_args()



###############
### IMPORTS ###
###############

import pygame
import pygame.gfxdraw
from pygame.locals import *



###############
## CONSTANTS ##
###############

FPS = args.fps
SCREENSIZE = (args.width,args.height)
PPP = args.ppp
BASEDIR = os.path.dirname(os.path.abspath(__file__))
MAXUNDO = 5
MOVESCALE = (args.scale_x, args.scale_y)

# Cursession
# **********
CSFILE = 'cursession'
CSIMGFORMAT = 'RGBA'
CSARCHWMODE = 'w:gz'
CSARCHRMODE = 'r:gz'
CSCHUNKMASK = '{x}.{y}.chunk'
CSPERSISTANCE = False

# Key aliases
# ***********
KEY_SAVE   = 's'
KEY_QUIT   = 'q'
KEY_RESIZE = 'w'
KEY_CUT    = 'x'
KEY_COPY   = 'c'
KEY_PASTE  = 'v'
KEY_DELETE = 'd'
KEY_FILL   = 'f'
KEY_UNDO   = 'z'
KEY_SAVECS = 'a'

# Tool names
# *********
tool_map = {
    KEY_RESIZE: 'resize',
    KEY_CUT:    'cut',
    KEY_COPY:   'copy',
    KEY_DELETE: 'delete',
    KEY_FILL:   'fill',
    'm3':       'delete',
    'm2':       'move',
    'm1':       'pen',
    None:       'pen'
}

# Save info
# ********
SESSION = datetime.datetime.now().strftime(args.session)
FORMAT = args.format
DIR = args.dir

# Colors
# *****
white = 255,255,255
grey = 127,127,127
black = 0,0,0
blue = 0,0,255
cyan = 127,127,255
red = 255,0,0
green = 0,255,0
maroon = 128,0,0
pink = 255,105,180
yellow = 255,255,0
orange = 235,120,0
transparent = 0,0,0,0

colors = [black,red,green,blue,cyan,maroon,pink,yellow,orange]

penwidth = args.penwidth
pencolor = black



#################
#### CLASSES ####
#################

class Surface:
    def __init__(self, chunksize, chunks=None):
        self.chunksize = chunksize
        if chunks == None:
            self.chunks = {}
        else:
            self.chunks = chunks
        self.lasts = []
    def get_chunk(self, pos, write):
        if pos not in self.chunks:
            if write: self.create_chunk(pos)
            else: return False
        return self.chunks[pos]
    def undo(self):
        if len(self.lasts) == 0:
            return
        current = self.lasts.pop()
        self.chunks.update(current)
    def create_chunk(self, pos):
        self.chunks[pos] = pygame.Surface((self.chunksize,self.chunksize), SRCALPHA)
        self.chunks[pos].set_colorkey(white)
        self.chunks[pos].fill(transparent)
    def retrieve_chunks(self, screensize, pos,write=False):
        # Yields chunks that you can possibly see in `surface'
        #  if surface.topleft == pos
        #     and chunksize >= surface.height
        #     and chunksize >= surface.width
        # yields (pos,chunk) where pos == chunk.topleft
        # yields at most four chunks
        x,y=pos
        ox, oy = -x, -y
        sx, sy = screensize
        tx = ox//self.chunksize
        ty = oy//self.chunksize
        bx = (ox+sx)//self.chunksize
        by = (oy+sy)//self.chunksize
        for x in range(tx, bx+1):
            for y in range(ty, by+1):
                chunk = self.get_chunk((-x,-y), write)
                if chunk:
                    yield (-x*self.chunksize,-y*self.chunksize), chunk
    def blit(self, surface, pos):
        last = {}
        for (x,y), chunk in self.retrieve_chunks(surface.get_size(), pos,write=True):
            lchunk = chunk.copy()
            rpos = sub_tuples((x,y),pos)
            chunk.blit(surface,rpos)
            last[x//self.chunksize,y//self.chunksize] = lchunk
        self.lasts.append(last)
        if len(self.lasts) > MAXUNDO:
            self.lasts.pop(0)
    def save(self):
        return (self.chunksize, self.chunks)

class Lock:
    def __init__(self):
        self._lock = None
        self.lock = None
    @property
    def lock(self):
        return self._lock
    @lock.setter
    def lock(self, value):
        self._lock = value
        chtool(tool_map[value])

class Hitbox:
    def __init__(self, pos1,pos2):
        x1,y1 = pos1
        x2,y2 = pos2
        self.x1,self.x2 = min(x1,x2), max(x1,x2)
        self.y1,self.y2 = min(y1,y2), max(y1,y2)
    def __contains__(self, pos):
        x,y=pos
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
        
        

#################
### FUNCTIONS ###
#################

def undo():
    flush()
    surface.undo()
    popup('undo')

# Session handling
# ****************
def add_file_archive(archive, name, string):
    s = io.BytesIO(string)
    tar_info = tarfile.TarInfo(name=name)
    tar_info.size = len(string)
    archive.addfile(tarinfo=tar_info, fileobj=s)

def save_chunk(surface, format, size):
    data = pygame.image.tostring(surface, CSIMGFORMAT)
    if format == 'string':
        return data
    img = Image.frombytes(CSIMGFORMAT, (size,size), data)
    zdata = io.BytesIO()
    img.save(zdata, format)
    return zdata.getvalue()
    
def save_cursession():
    flush()
    cs, chunks = surface.save()
    format = FORMAT
    with tarfile.open(os.path.join(BASEDIR, SESSION, CSFILE), CSARCHWMODE) as archive:
        add_file_archive(archive, 'chunksize', bytes(str(cs), 'utf-8'))
        add_file_archive(archive, 'offset', bytes(str(offset), 'utf-8'))
        add_file_archive(archive, 'format', bytes(format, 'utf-8'))
        for (x,y), chunk in chunks.items():
            add_file_archive(archive, CSCHUNKMASK.format(x=x,y=y), save_chunk(chunk, format, cs))
    popup('saved current session')

def read_var(var, files, archive, default=None,type=eval):
    if var not in files and default!=None:
        return default
    elif var not in files:
        raise FileNotFoundError("Couldn't find the variable file %s" % var)
    files.remove(var)
    return type(archive.extractfile(var).read())

def load_chunk(string, size, format):
    if format == 'string':
        r = pygame.image.fromstring(string, (size,size), CSIMGFORMAT)
    else:
        zdata = io.BytesIO(string)
        img = Image.open(zdata)
        r = pygame.image.fromstring(img.tobytes(), (size,size), CSIMGFORMAT)
    r.set_colorkey(white)
    return r
    
    
def load_cursession():
    try:
        if os.path.isfile(os.path.join(BASEDIR, SESSION, CSFILE)) and tarfile.is_tarfile(os.path.join(BASEDIR, SESSION, CSFILE)):
            #print(os.path.join(BASEDIR,SESSION,CSFILE))
            with tarfile.open(os.path.join(BASEDIR,SESSION,CSFILE), CSARCHRMODE) as archive:
                files = archive.getnames()
                cs = read_var('chunksize', files, archive)
                offset = read_var('offset', files, archive, default=(0,0))
                format = read_var('format', files, archive, default='string',type=lambda x: x.decode('utf-8'))
                chunks = {}
                for file in files:
                    coords = tuple(int(e) for e in file.split('.')[:2])
                    string = archive.extractfile(file).read()
                    chunk = load_chunk(string, cs, format)
                    chunks[coords] = chunk
            return offset, (cs, chunks)
        else:
            return (0,0), (args.chunk_size, {})
    except BaseException as e:
        print('Error while trying to restore session: %s' % e)
        return (0,0), (args.chunk_size, {})
    
# Quit
# ****
def quit(exitcode=0):
    if CSPERSISTANCE: save_cursession()
    pygame.quit()
    sys.exit(exitcode)

# Tuples
# ******
def mul_tuples(t1,t2):
    return tuple(a*b for a,b in zip(t1,t2))

def mul_tuple(r, t):
    return tuple(r*v for v in t)
    
def add_tuples(*tuples):
    return tuple(sum(values) for values in zip(*tuples))

def sub_tuples(t1,t2):
    return tuple(a-b for a,b in zip(t1,t2))

def realpos(pos):
    return sub_tuples(pos, offset)

def relpos(pos):
    return add_tuples(pos, offset)

# Save to page
# ************
def pre_render():
    global rendered_pos
    rendered_pos = []
    screen.fill(white)
    result = []
    for pos, chunk in surface.retrieve_chunks(screen.get_size(), offset):
        result.append(str(pos))
        screen.blit(chunk, sub_tuples(offset,pos))
    rendered_pos.extend(result)
    screen.blit(temp_surf,(0,0))
    
def full_render():
    pre_render()
    flush()

def render():
    pre_render()
    screen.blit(popup_surface, popup_pos)
    screen.blit(tool_surface, tool_pos)
    screen.blit(color_surface, color_pos)
    if lock.lock in {'m3', KEY_CUT, KEY_COPY, KEY_DELETE, KEY_FILL} and isdown:
        x1, y1 = anchor
        x2, y2 = pygame.mouse.get_pos()
        points = ((x1,y1),(x2,y1),(x2,y2),(x1,y2))
        pygame.draw.aalines(screen, grey, True, points, 4)
    if lock.lock in {KEY_RESIZE} and isdown:
        pygame.draw.circle(screen, grey, anchor, (penwidth)>>1)
    pygame.display.flip()
    
def save():
    global page
    full_render()
    pygame.image.save(screen, os.path.join(DIR, SESSION, ("%s-%s.%s" % (SESSION, page, FORMAT))))
    popup('saved page %s' % page)
    page += 1

# Better drawing functions
# ************************
def drawing(commit=True):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(surface, *args, **kwargs):
            global need_flush
            n = function(temp_surf, *args, **kwargs)
            if commit and n:
                need_flush = True
                flush()
            else:
                need_flush |= n
        return wrapper
    return decorator

def make_rect(pos1,pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    left = min(x1,x2)
    w = max(x1,x2) - left
    top = min(y1,y2)
    h = max(y1,y2) - top
    return pygame.Rect(left, top, w, h)
@drawing(False)
def draw_line(surface, pos1, pos2, color, width):
    pos1=pos1
    pos2=pos2
    pygame.gfxdraw.filled_circle(surface,*pos1,width//2,color)
    pygame.gfxdraw.filled_circle(surface,*pos2,width//2,color)
    pygame.draw.line(surface,color,pos1,pos2,width+1)
    return True
def delete(surface, pos1, pos2):
    erase(surface, pos1, pos2)
    popup('deleted')
    return True
@drawing()
def erase(surface, pos1, pos2):
    pygame.draw.rect(surface, white, make_rect(pos1,pos2))
    return True
def copy(surface, pos1, pos2):
    global buffer
    full_render()
    buffer = screen.subsurface(make_rect(pos1,pos2)).copy()
    buffer.set_colorkey(white)
    popup('copied')
@drawing()
def cut(surface, pos1, pos2):
    copy(surface, pos1, pos2)
    erase(surface, pos1, pos2)
    popup('cuted')
    return True
@drawing()
def paste(surface, pos1):
    global buffer
    if buffer == None:
        return False
    surface.blit(buffer, pos1)
    popup('pasted')
    return True
@drawing()
def fill(surface, pos1, pos2, color):
    pygame.draw.rect(surface, color, make_rect(pos1,pos2))
    popup('filled')
    return True
def popup(*args, sep=' '):
    string = sep.join(str(e) for e in args)
    text = font.render(string, True, black)
    popup_surface.fill(white)
    pygame.draw.rect(popup_surface, grey, pygame.Rect(0,0,popup_surface.get_width(),popup_surface.get_height()),3)
    popup_surface.blit(text, (2,2))
def chtool(tool):
    text = font.render('Tool: %s' % tool, True, black)
    tool_surface.fill(white)
    pygame.draw.rect(tool_surface, grey, pygame.Rect(0,0,tool_surface.get_width(),tool_surface.get_height()),3)
    tool_surface.blit(text, (2,2))
def flush():
    global need_flush
    if need_flush == False:
        return
    surface.blit(temp_surf, mul_tuple(1,offset))
    temp_surf.fill(transparent)
    need_flush = False

#############
### SETUP ###
#############

# Session dir
# ***********
if not os.path.isdir(os.path.join(DIR,SESSION)):
    os.makedirs(os.path.join(DIR,SESSION))

# Cursession dir
# **************
if not os.path.isdir(os.path.join(BASEDIR,SESSION)):
    os.makedirs(os.path.join(BASEDIR,SESSION))
    
# Pygame
# ******
pygame.init()
pygame.mixer.quit()

fontsize = 24
font = pygame.font.Font(None, fontsize)

screen = pygame.display.set_mode(SCREENSIZE)

pygame.display.set_caption('BlackBBoard - %s' % SESSION)
icon = pygame.image.load(os.path.join(BASEDIR, 'blackbboard.png'))
pygame.display.set_icon(icon)
print('Icon made by Good Ware from flaticon.com')

offset, surface = load_cursession()
surface = Surface(*surface)

popup_surface = pygame.Surface((screen.get_width(), fontsize))
popup_surface.fill(white)
popup_pos = 0,0

tool_surface = pygame.Surface((screen.get_width()//2, fontsize))
tool_surface.fill(white)
tool_pos = 0,fontsize

color_surface = pygame.Surface((screen.get_width()//2,fontsize))
color_surface.fill(white)
color_pos = screen.get_width()//2+2,fontsize
color_hitbox = Hitbox(color_pos, add_tuples(color_pos, (color_surface.get_width(), color_surface.get_height())))

for i, color in enumerate(colors):
    pos = color_surface.get_height()*(i+1)+color_surface.get_height()//2,color_surface.get_height()//2
    radius = color_surface.get_height()//2
    pygame.gfxdraw.filled_circle(color_surface, *pos, radius, color)

pygame.mouse.set_cursor(*pygame.cursors.tri_left)



################
## INPUT VARS ##
################

# also known as buffer for computing input

islock = False
isdown = False
anchor = (None,None)
lock = Lock()
# lock may be either:
#  - 'm1':  draw
#  - 'm3':  erase
#  - 'm2':  move
#  - 'w' :  change pen width
#  - 'x' :  cut
#  - 'c' :  copy
#  - 'f' :  fill
#  - None:  nothing
# lock represents the actual state of the pen

coff = 0
maxcoff = 0
anchw = penwidth

buffer = None
# the clipboard for cut/copy/paste tools

temp_surf = pygame.Surface(SCREENSIZE, SRCALPHA)
temp_surf.fill(transparent)
temp_surf.set_colorkey(white)
need_flush = False

page = 1
while os.path.isfile(os.path.join(DIR, SESSION, ("%s-%s.%s" % (SESSION, page, FORMAT)))):
    page += 1


###############
## MAIN LOOP ##
###############

popup('Current session: %s' % SESSION)

clock = pygame.time.Clock()

rendered_pos = []

while True:
    for event in pygame.event.get():
        pos = pygame.mouse.get_pos()
        if event.type == pygame.QUIT: quit()
        #elif event.type == VIDEORESIZE:
        #    screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            isdown = False
            flush()
            if lock.lock == 'm1':
                islock = False
                lock.lock = None
            elif lock.lock == 'm3':
                delete(surface, anchor, pos)
            elif lock.lock == 'm2':
                pass
            elif lock.lock == KEY_RESIZE:
                anchw = penwidth
                pygame.mouse.set_pos(anchor)
                pygame.mouse.set_visible(True)
            elif lock.lock == KEY_CUT:
                cut(surface, anchor, pos)
            elif lock.lock == KEY_COPY:
                copy(surface, anchor, pos)
            elif lock.lock == KEY_DELETE:
                delete(surface, anchor, pos)
            elif lock.lock == KEY_FILL:
                fill(surface, anchor, pos, pencolor)
            anchor = (None,None)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if not islock:
                if pos in color_hitbox:
                    ncolor = screen.get_at(pos)
                    if ncolor != white:
                        pencolor = ncolor
                        continue
                islock = True
                lock.lock = 'm1'
            elif lock.lock == KEY_RESIZE:
                pygame.mouse.set_visible(False)
                anchw = penwidth
                coff = 0
                maxcoff = -(anchw-1)*PPP
            isdown = True
            anchor = pos
        elif event.type == MOUSEBUTTONDOWN and event.button == 3:
            if not islock:
                islock = True
                lock.lock = 'm3'
        elif event.type == MOUSEBUTTONDOWN and event.button == 2:
            if not islock:
                islock = True
                lock.lock = 'm2'
        elif event.type == MOUSEBUTTONUP and event.button == 3:
            if lock.lock == 'm3':
                islock = False
                lock.lock = None
        elif event.type == MOUSEBUTTONUP and event.button == 2:
            if lock.lock == 'm2':
                islock = False
                lock.lock = None
        elif event.type == MOUSEMOTION:
            if not islock:
                pass
            if not isdown:
                pass
            if lock.lock == 'm1' and isdown:
                if anchor == (None,None):
                    last = pos
                else:
                    last = anchor
                anchor = pos
                draw_line(surface, last, anchor, pencolor, penwidth)
            elif lock.lock == 'm2' and isdown:
                flush()
                d = mul_tuples(MOVESCALE, sub_tuples(pos, anchor))
                offset = add_tuples(offset, d)
                anchor = pos
            elif lock.lock == KEY_RESIZE and isdown:
                coff = pos[0] - anchor[0]
                coff = max(coff,maxcoff)
                penwidth = max(anchw+coff//PPP,1)
                chtool(tool_map[lock.lock] + (' %s' % penwidth))
        elif event.type == KEYDOWN:
            if event.key == ord(KEY_SAVE):
                save()
            elif event.key == ord(KEY_QUIT):
                quit()
            elif event.key == ord(KEY_RESIZE):
                if not islock:
                    islock = True
                    lock.lock = KEY_RESIZE
                    chtool(tool_map[lock.lock] + (' %s' % penwidth))
            elif event.key == ord(KEY_CUT):
                if not islock:
                    islock = True
                    lock.lock = KEY_CUT
            elif event.key == ord(KEY_COPY):
                if not islock:
                    islock = True
                    lock.lock = KEY_COPY
            elif event.key == ord(KEY_PASTE):
                paste(surface, pos)
            elif event.key == ord(KEY_DELETE):
                if not islock:
                    islock = True
                    lock.lock = KEY_DELETE
            elif event.key == ord(KEY_FILL):
                if not islock:
                    islock = True
                    lock.lock =KEY_FILL
            elif event.key == ord(KEY_UNDO):
                undo()
            elif event.key == ord(KEY_SAVECS):
                popup('saving current session...')
                render()
                save_cursession()
                popup('saved current session!')
        elif event.type == KEYUP:
            if event.key == ord(KEY_RESIZE):
                if lock.lock == KEY_RESIZE:
                    islock = False
                    lock.lock = None
                    if anchor != (None,None):
                        anchw = penwidth
                        pygame.mouse.set_pos(anchor)
                        pygame.mouse.set_visible(True)
                        anchor = (None,None)
            elif event.key == ord(KEY_CUT):
                if lock.lock == KEY_CUT:
                    islock = False
                    lock.lock = None
                    if anchor != (None,None):
                        cut(surface, anchor, pos)
                        anchor = (None, None)
            elif event.key == ord(KEY_COPY):
                if lock.lock == KEY_COPY:
                    islock = False
                    lock.lock = None
                    if anchor != (None,None):
                        copy(surface, anchor, pos)
                        anchor = (None,None)
            elif event.key == ord(KEY_DELETE):
                if lock.lock == KEY_DELETE:
                    islock = False
                    lock.lock = None
                    if anchor != (None,None):
                        delete(surface, anchor, pos)
                        anchor = (None,None)
            elif event.key == ord(KEY_FILL):
                if lock.lock == KEY_FILL:
                    islock = False
                    lock.lock = None
                    if anchor != (None,None):
                        fill(surface, anchor, pos, pencolor)
                        anchor = (None,None)
    render()
    clock.tick(FPS)
