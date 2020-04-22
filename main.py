#!/usr/bin/python3

import sys, os, argparse, datetime

__version__ = "1.0"

parser = argparse.ArgumentParser(
    prog='Board',
    description='''\
Board: WYSIWYG interactive board
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
parser.add_argument('--canvas-mul', type=int, help='Real canvas size respect to window size', default=10)
parser.add_argument('-v', '--version', action='version', version='%(prog)s '+__version__)
args = parser.parse_args()

import pygame
from pygame.locals import *

SCREENSIZE = (args.width,args.height)
PENWIDTH = args.penwidth
SESSION = datetime.datetime.now().strftime(args.session)
FORMAT = args.format
DIR = args.dir

def quit(exitcode=0):
    pygame.quit()
    sys.exit(exitcode)

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

def save():
    global page
    page += 1
    pygame.image.save(screen, os.path.join(DIR, ("%s-%s.%s" % (SESSION, page, FORMAT))))

if not os.path.isdir(DIR):
    os.makedirs(DIR)

pygame.init()
pygame.mixer.quit()
screen = pygame.display.set_mode(SCREENSIZE)

pygame.display.set_caption('Tableau')

white = 255,255,255
grey = 127,127,127
black = 0,0,0

surface = pygame.Surface(mul_tuple(args.canvas_mul, SCREENSIZE))
surface.fill(white)
isdown = False
last = None, None

isrdown = False
rtopleft = (0,0)

ismdown = False
mo = (0,0)
offset = (0,0)

page = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: quit()
        #elif event.type == VIDEORESIZE:
        #    screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            isdown = True
            last = realpos(event.pos)
        elif event.type == MOUSEBUTTONDOWN and event.button == 3:
            isrdown = True
            rtopleft = realpos(event.pos)
        elif event.type == MOUSEBUTTONUP and event.button == 3:
            isrdown = False
            x1, y1 = rtopleft
            x2, y2 = realpos(event.pos)
            left = min(x1,x2)
            w = max(x1,x2) - left
            top = min(y1,y2)
            h = max(y1,y2) - top
            pygame.draw.rect(surface, white, pygame.Rect(left, top, w, h))
        elif event.type == MOUSEBUTTONDOWN and event.button == 2:
            ismdown = True
            mo = event.pos
        elif event.type == MOUSEBUTTONUP and event.button == 2:
            ismdown = False
        elif event.type == MOUSEMOTION:
            if isdown:
                if last == (None,None):
                    last = realpos(event.pos)
                pygame.draw.line(surface,black,last,realpos(event.pos),PENWIDTH)
                last = realpos(event.pos)
            elif last != (None, None):
                last = (None, None)
            if ismdown:
                d = sub_tuples(pygame.mouse.get_pos(), mo)
                offset = add_tuples(offset, d)
                mo = add_tuples(mo, d)
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            isdown = False
            last = (None, None)
        elif event.type == KEYDOWN:
            if event.key == ord('s'):
                save()
    screen.fill(white)
    screen.blit(surface, offset)
    if isrdown:
        x1, y1 = relpos(rtopleft)
        x2, y2 = pygame.mouse.get_pos()
        points = ((x1,y1),(x2,y1),(x2,y2),(x1,y2))
        pygame.draw.lines(screen, grey, True, points, PENWIDTH)
    pygame.display.flip()
