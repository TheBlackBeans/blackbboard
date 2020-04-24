#!/usr/bin/python3

# BlackBBoard -- virtual boards

###############
### IMPORTS ###
###############

import sys, os, argparse, datetime, math



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
parser.add_argument('-f', '--format', help='format of output files', default='png', choices={'png', 'jpeg', 'bmp', 'tga'})
parser.add_argument('-d', '--dir', help='target directory to save session pages', default='session')
parser.add_argument('--canvas-mul', type=int, help='real canvas size respect to window size', default=10)
parser.add_argument('-v', '--version', action='version', version='%(prog)s '+__version__)
parser.add_argument('-P', '--ppp', help='inverse speed of scale of pen width', default=20, type=int)
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

SCREENSIZE = (args.width,args.height)
PPP = args.ppp

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
transparent = 0,0,0,0

colors = {black,blue,cyan,red,green}

penwidth = args.penwidth
pencolor = black



#################
#### CLASSES ####
#################

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

# Quit
# ****
def quit(exitcode=0):
    pygame.quit()
    sys.exit(exitcode)

# Tuples
# ******
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
def save():
    global page
    page += 1
    pygame.image.save(screen, os.path.join(DIR, ("%s-%s.%s" % (SESSION, page, FORMAT))))
    popup('saved page %s' % page)

# Better drawing functions
# ************************
def make_rect(pos1,pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    left = min(x1,x2)
    w = max(x1,x2) - left
    top = min(y1,y2)
    h = max(y1,y2) - top
    return pygame.Rect(left, top, w, h)
def draw_line(surface, pos1, pos2, color, width):
    pygame.gfxdraw.filled_circle(surface,*pos1,math.ceil(width/2),color)
    pygame.gfxdraw.filled_circle(surface,*pos2,math.ceil(width/2),color)
    pygame.draw.line(surface,color,pos1,pos2,width)
def delete(surface, pos1, pos2):
    erase(surface, pos1, pos2)
    popup('deleted')
def erase(surface, pos1, pos2):
    pygame.draw.rect(surface, transparent, make_rect(pos1,pos2))
def copy(surface, pos1, pos2):
    global buffer
    buffer = surface.subsurface(make_rect(pos1,pos2)).copy()
    popup('copied')
def cut(surface, pos1, pos2):
    copy(surface, pos1, pos2)
    erase(surface, pos1, pos2)
    popup('cuted')
def paste(surface, pos1):
    global buffer
    if buffer == None:
        return
    surface.blit(buffer, pos1)
    popup('pasted')
def fill(surface, pos1, pos2, color):
    pygame.draw.rect(surface, color, make_rect(pos1,pos2))
    popup('filled')
def popup(message):
    text = font.render(message, True, black)
    popup_surface.fill(white)
    pygame.draw.rect(popup_surface, grey, pygame.Rect(0,0,popup_surface.get_width(),popup_surface.get_height()),3)
    popup_surface.blit(text, (2,2))
def chtool(tool):
    text = font.render('Tool: %s' % tool, True, black)
    tool_surface.fill(white)
    pygame.draw.rect(tool_surface, grey, pygame.Rect(0,fontsize,tool_surface.get_width(),tool_surface.get_height()),3)
    tool_surface.blit(text, (2,2))

#############
### SETUP ###
#############

# Session dir
# ***********
if not os.path.isdir(DIR):
    os.makedirs(DIR)

# Pygame
# ******
pygame.init()
pygame.mixer.quit()

fontsize = 24
font = pygame.font.Font(None, fontsize)

screen = pygame.display.set_mode(SCREENSIZE)

pygame.display.set_caption('BlackBBoard - %s' % SESSION)
icon = pygame.image.load('blackbboard.png')
pygame.display.set_icon(icon)
print('Icon made by Good Ware from flaticon.com')

surface = pygame.Surface(mul_tuple(args.canvas_mul, SCREENSIZE), SRCALPHA)
surface.fill(transparent)

popup_surface = pygame.Surface((screen.get_width(), fontsize))
popup_surface.fill(white)
popup_pos = 0,0

tool_surface = pygame.Surface((screen.get_width()//2, fontsize))
tool_surface.fill(white)
tool_pos = 0,fontsize

color_surface = pygame.Surface((screen.get_width()//2,fontsize))
color_surface.fill(white)
color_pos = screen.get_width()//2,fontsize
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
offset = (0,0)

coff = 0
maxcoff = 0
anchw = penwidth

buffer = None

page = 0



###############
## MAIN LOOP ##
###############

popup('Current session: %s' % SESSION)

while True:
    for event in pygame.event.get():
        pos = realpos(pygame.mouse.get_pos())
        if event.type == pygame.QUIT: quit()
        #elif event.type == VIDEORESIZE:
        #    screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            isdown = False
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
            isdown = True
            anchor = pos
            if not islock:
                if relpos(pos) in color_hitbox:
                      pencolor = screen.get_at(relpos(pos))
                islock = True
                lock.lock = 'm1'
            elif lock.lock == KEY_RESIZE:
                pygame.mouse.set_visible(False)
                anchw = penwidth
                coff = 0
                maxcoff = -(anchw-1)*PPP
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
                d = sub_tuples(pos, anchor)
                offset = add_tuples(offset, d)
                mo = add_tuples(anchor, d)
            elif lock.lock == KEY_RESIZE and isdown:
                coff = pos[0] - anchor[0]
                coff = max(coff,maxcoff)
                penwidth = max(anchw+coff//PPP,1)
        elif event.type == KEYDOWN:
            if event.key == ord(KEY_SAVE):
                save()
            elif event.key == ord(KEY_QUIT):
                quit()
            elif event.key == ord(KEY_RESIZE):
                if not islock:
                    islock = True
                    lock.lock = KEY_RESIZE
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
    screen.fill(white)
    screen.blit(surface, offset)
    screen.blit(popup_surface, popup_pos)
    screen.blit(tool_surface, tool_pos)
    screen.blit(color_surface, color_pos)
    if lock.lock in {'m3', KEY_CUT, KEY_COPY, KEY_DELETE, KEY_FILL} and isdown:
        x1, y1 = relpos(anchor)
        x2, y2 = pygame.mouse.get_pos()
        points = ((x1,y1),(x2,y1),(x2,y2),(x1,y2))
        pygame.draw.aalines(screen, grey, True, points, 4)
    if lock.lock in {KEY_RESIZE} and isdown:
        pygame.draw.circle(screen, grey, relpos(anchor), (penwidth+1)>>1)
    pygame.display.flip()
