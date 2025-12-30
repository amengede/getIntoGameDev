import numpy as np
import pygame as pg
from numba import (njit, int32, float32)

MESSAGE_TYPE_PLAYER_WALKING = 0
MESSAGE_TYPE_PLAYER_STOP = 1
MESSAGE_TYPE_PLAYER_SHOOT = 2
MESSAGE_TYPE_PLAYER_RELOAD = 3

@njit()
def rotate(x: float, y: float, theta: float) -> tuple[float]:
    
    t = np.radians(theta)
    c = np.cos(t)
    s = np.sin(t)

    x_new =  x * c + y * s
    y_new = -x * s + y * c
    
    return (x_new, y_new)

def publish(message: int, observers: list[list[int]]) -> None:

    for observer in observers:
        observer.append(message)