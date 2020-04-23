#!/usr/bin/python3

# BlackBBoard -- virtual boards

###############
### IMPORTS ###
###############

import sys, os, argparse, datetime



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
parser.add_argument('-P', '--ppp', help='inverse speed of scale of pen width', default=50, type=int)
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

screen = pygame.display.set_mode(SCREENSIZE)

pygame.display.set_caption('Tableau')

surface = pygame.Surface(mul_tuple(args.canvas_mul, SCREENSIZE))
surface.fill(white)

pygame.mouse.set_cursor(*pygame.cursors.tri_left)



################
## INPUT VARS ##
################

islock = False
isdown = False
anchor = (None,None)
lock = None
# lock may be either:
#  - 'm1':  draw
#  - 'm3':  erase
#  - 'm2':  move
#  - 'c' :  change pen width
#  - None:  nothing
offset = (0,0)

coff = 0
maxcoff = 0
anchw = penwidth

page = 0



###############
## MAIN LOOP ##
###############

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
                x1, y1 = anchor
                x2, y2 = realpos(event.pos)
                left = min(x1,x2)
                w = max(x1,x2) - left
                top = min(y1,y2)
                h = max(y1,y2) - top
                pygame.draw.rect(surface, white, pygame.Rect(left, top, w, h))
            elif lock == 'm2':
                pass
            elif lock == 'c':
                anchw = penwidth
                pygame.mouse.set_pos(anchor)
                pygame.mouse.set_visible(True)
            anchor = (None,None)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            isdown = True
            anchor = realpos(event.pos)
            if not islock:
                islock = True
                lock = 'm1'
            elif lock == 'c':
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
                pygame.draw.line(surface,black,last,realpos(event.pos),penwidth)
                anchor = realpos(event.pos)
            elif lock == 'm2' and isdown:
                d = sub_tuples(realpos(pygame.mouse.get_pos()), anchor)
                offset = add_tuples(offset, d)
                mo = add_tuples(anchor, d)
            elif lock == 'c' and isdown:
                coff = realpos(pygame.mouse.get_pos())[0] - anchor[0]
                coff = max(coff,maxcoff)
                penwidth = max(anchw+coff//PPP,1)
        elif event.type == KEYDOWN:
            if event.key == ord('s'):
                save()
            elif event.key == ord('q'):
                quit()
            elif event.key == ord('c'):
                if not islock:
                    islock = True
                    lock = 'c'
        elif event.type == KEYUP:
            if event.key == ord('c'):
                if lock == 'c':
                    islock = False
                    lock = None
                    if anchor != (None,None):
                        anchw = penwidth
                        pygame.mouse.set_pos(anchor)
                        pygame.mouse.set_visible(True)
                        anchor = (None,None)
                
    screen.fill(white)
    screen.blit(surface, offset)
    if lock == 'm3' and isdown:
        x1, y1 = relpos(anchor)
        x2, y2 = pygame.mouse.get_pos()
        points = ((x1,y1),(x2,y1),(x2,y2),(x1,y2))
        pygame.draw.aalines(screen, grey, True, points, 4)
    if lock == 'c' and isdown:
        pygame.draw.circle(screen, grey, relpos(anchor), (penwidth+1)>>1)
    pygame.display.flip()
