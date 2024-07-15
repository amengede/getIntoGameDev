import PyQt6
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import sys

MOUSE_MODE_SELECT = 0
MOUSE_MODE_EDIT = 1
MOUSE_MODE_NEW = 2

MAIN_WINDOW_WIDTH = 640
MAIN_WINDOW_HEIGHT = 480

OBJECT_TYPE_PLAYER = 0
OBJECT_TYPE_MONSTER = 1
OBJECT_TYPE_BLOCK = 2
OBJECT_TYPE_COIN = 3

OBJECT_SIZES: dict[int, tuple[float]] = {
    OBJECT_TYPE_PLAYER:     (  1,   2),
    OBJECT_TYPE_MONSTER:    (  1,   1),
    OBJECT_TYPE_BLOCK:      (  1,   1),
    OBJECT_TYPE_COIN:       (0.5, 0.5),
}

OBJECT_COLORS: dict[int, QColor] = {
    OBJECT_TYPE_PLAYER:     QColor(  0, 128, 16),
    OBJECT_TYPE_MONSTER:    QColor(128, 128,  0),
    OBJECT_TYPE_BLOCK:      QColor( 64,  64,  0),
    OBJECT_TYPE_COIN:       QColor(255, 255,  0),
}

OBJECT_NAMES: dict[int, str] = {
    OBJECT_TYPE_PLAYER:     "player",
    OBJECT_TYPE_MONSTER:    "monster",
    OBJECT_TYPE_BLOCK:      "block",
    OBJECT_TYPE_COIN:       "coin",
}

OBJECT_CODES: dict[int, QColor] = {
    "player":   OBJECT_TYPE_PLAYER,
    "monster":  OBJECT_TYPE_MONSTER,
    "block":    OBJECT_TYPE_BLOCK,
    "coin":     OBJECT_TYPE_COIN,
}

CAMERA_MOVE_LEFT = 0
CAMERA_MOVE_RIGHT = 1
CAMERA_MOVE_UP = 2
CAMERA_MOVE_DOWN = 3