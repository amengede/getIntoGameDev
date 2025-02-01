import pygame as pg
import random
from openal import *

pg.init()
SCREENSIZE = (300,600)
SCREEN = pg.display.set_mode(SCREENSIZE)

PIECE_SIZE = 40

PALETTE = {
    "teal":(41,127,135),
    "yellow":(246,209,103),
    "light-yellow":(255,247,174),
    "red":(223,46,46)
}

oalInit()
SMASH_SOUND = oalOpen("sfx/smash.wav")
CLICK_SOUND = oalOpen("sfx/click.wav")