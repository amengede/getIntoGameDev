import numpy as np
from numba import njit
import time
from matplotlib import pyplot

#constants
SPHERE_RADIUS = 0.025
TABLE_LENGTH = 3.6
TABLE_WIDTH = 1.8
TABLE_FRICTION_MULTIPLIER = 0.8
COLLISION_BOX_SIZE = 0.2