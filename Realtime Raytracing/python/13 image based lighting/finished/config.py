import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import time
import queue
from PIL import Image, ImageOps

np.random.seed(0)