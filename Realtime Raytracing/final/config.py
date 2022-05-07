import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

################################## Helper Functions ###########################

def randomInUnitSphere():

    theta = np.random.uniform(low=0, high=2*np.pi)
    phi = np.random.uniform(low=0, high=np.pi)
    radius = np.random.uniform()

    vector = np.array(
        [
            radius * np.cos(theta) * np.sin(phi),
            radius * np.sin(theta) * np.sin(phi),
            radius * np.cos(phi)
        ], dtype=np.float32
    )
    return vector

def get_lumped_geometry_from(array):

        rows = len(array)
        cols = len(array[0])

        empty_blocks = (0, "d")

        result = [[0 for col in range(cols)] for row in range(rows)]

        for row in range(rows):
            for col in range(cols):

                #block
                if array[row][col] not in empty_blocks:
                    result[row][col] = 15

                    #north
                    if row == 0 or array[row - 1][col] not in empty_blocks:
                        result[row][col] -= 1
                    
                    #east
                    if col == (cols - 1) or array[row][col + 1] not in empty_blocks:
                        result[row][col] -= 2
                    
                    #south
                    if row == (rows - 1) or array[row + 1][col] not in empty_blocks:
                        result[row][col] -= 4
                    
                    #west
                    if col == 0 or array[row][col - 1] not in empty_blocks:
                        result[row][col] -= 8
            

        return result

###############################################################################