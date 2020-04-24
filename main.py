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
transparent = 0,0,0,0

penwidth = args.penwidth



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
def fill(surface, pos1, pos2):
    pygame.draw.rect(surface, black, make_rect(pos1,pos2))
    popup('filled')
def popup(message):
    text = font.render(message, True, black)
    popup_surface.fill(white)
    pygame.draw.rect(popup_surface, grey, pygame.Rect(0,0,popup_surface.get_width(),popup_surface.get_height()),3)
    popup_surface.blit(text, (2,2))


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

surface = pygame.Surface(mul_tuple(args.canvas_mul, SCREENSIZE), SRCALPHA)
surface.fill(transparent)

popup_surface = pygame.Surface((screen.get_width(), fontsize))
popup_surface.fill(white)
popup_pos = 0,0

pygame.mouse.set_cursor(*pygame.cursors.tri_left)



################
## INPUT VARS ##
################

# also known as buffer for computing input

islock = False
isdown = False
anchor = (None,None)
lock = None
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
        if event.type == pygame.QUIT: quit()
        #elif event.type == VIDEORESIZE:
        #    screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            isdown = False
            if lock == 'm1':
                islock = False
                lock = None
            elif lock == 'm3':
                delete(surface, anchor, realpos(event.pos))
            elif lock == 'm2':
                pass
            elif lock == KEY_RESIZE:
                anchw = penwidth
                pygame.mouse.set_pos(anchor)
                pygame.mouse.set_visible(True)
            elif lock == KEY_CUT:
                cut(surface, anchor, realpos(event.pos))
            elif lock == KEY_COPY:
                copy(surface, anchor, realpos(event.pos))
            elif lock == KEY_DELETE:
                delete(surface, anchor, realpos(event.pos))
            elif lock == KEY_FILL:
                fill(surface, anchor, realpos(event.pos))
            anchor = (None,None)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            isdown = True
            anchor = realpos(event.pos)
            if not islock:
                islock = True
                lock = 'm1'
            elif lock == KEY_RESIZE:
                pygame.mouse.set_visible(False)
                anchw = penwidth
                coff = 0
                maxcoff = -(anchw-1)*PPP
        elif event.type == MOUSEBUTTONDOWN and event.button == 3:
            if not islock:
                islock = True
                lock = 'm3'
        elif event.type == MOUSEBUTTONDOWN and event.button == 2:
            if not islock:
                islock = True
                lock = 'm2'
        elif event.type == MOUSEBUTTONUP and event.button == 3:
            if lock == 'm3':
                islock = False
                lock = None
        elif event.type == MOUSEBUTTONUP and event.button == 2:
            if lock == 'm2':
                islock = False
                lock = None
        elif event.type == MOUSEMOTION:
            if not islock:
                pass
            if not isdown:
                pass
            if lock == 'm1' and isdown:
                if anchor == (None,None):
                    last = realpos(event.pos)
                else:
                    last = anchor
                anchor = realpos(event.pos)
                draw_line(surface, last, anchor, black, penwidth)
            elif lock == 'm2' and isdown:
                d = sub_tuples(realpos(pygame.mouse.get_pos()), anchor)
                offset = add_tuples(offset, d)
                mo = add_tuples(anchor, d)
            elif lock == KEY_RESIZE and isdown:
                coff = realpos(pygame.mouse.get_pos())[0] - anchor[0]
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
                    lock = KEY_RESIZE
            elif event.key == ord(KEY_CUT):
                if not islock:
                    islock = True
                    lock = KEY_CUT
            elif event.key == ord(KEY_COPY):
                if not islock:
                    islock = True
                    lock = KEY_COPY
            elif event.key == ord(KEY_PASTE):
                paste(surface, realpos(pygame.mouse.get_pos()))
            elif event.key == ord(KEY_DELETE):
                if not islock:
                    islock = True
                    lock = KEY_DELETE
            elif event.key == ord(KEY_FILL):
                if not islock:
                    islock = True
                    lock =KEY_FILL
        elif event.type == KEYUP:
            if event.key == ord(KEY_RESIZE):
                if lock == KEY_RESIZE:
                    islock = False
                    lock = None
                    if anchor != (None,None):
                        anchw = penwidth
                        pygame.mouse.set_pos(anchor)
                        pygame.mouse.set_visible(True)
                        anchor = (None,None)
            elif event.key == ord(KEY_CUT):
                if lock == KEY_CUT:
                    islock = False
                    lock = None
                    if anchor != (None,None):
                        cut(surface, anchor, realpos(pygame.mouse.get_pos()))
                        anchor = (None, None)
            elif event.key == ord(KEY_COPY):
                if lock == KEY_COPY:
                    islock = False
                    lock = None
                    if anchor != (None,None):
                        copy(surface, anchor, realpos(pygame.mouse.get_pos()))
                        anchor = (None,None)
            elif event.key == ord(KEY_DELETE):
                if lock == KEY_DELETE:
                    islock = False
                    lock = None
                    if anchor != (None,None):
                        delete(surface, anchor, realpos(pygame.mouse.get_pos()))
                        anchor = (None,None)
            elif event.key == ord(KEY_FILL):
                if lock == KEY_FILL:
                    islock = False
                    lock = None
                    if anchor != (None,None):
                        fill(surface, anchor, realpos(pygame.mouse.get_pos()))
                        anchor = (None,None)
    screen.fill(white)
    screen.blit(surface, offset)
    screen.blit(popup_surface, popup_pos)
    if lock in {'m3', KEY_CUT, KEY_COPY, KEY_DELETE, KEY_FILL} and isdown:
        x1, y1 = relpos(anchor)
        x2, y2 = pygame.mouse.get_pos()
        points = ((x1,y1),(x2,y1),(x2,y2),(x1,y2))
        pygame.draw.aalines(screen, grey, True, points, 4)
    if lock in {KEY_RESIZE} and isdown:
        pygame.draw.circle(screen, grey, relpos(anchor), (penwidth+1)>>1)
    pygame.display.flip()
