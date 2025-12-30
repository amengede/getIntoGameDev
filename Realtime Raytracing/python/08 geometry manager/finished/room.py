from config import *

class Room:
    """
        Room object: holds a set of planes and doors
    """


    def __init__(self):

        self.planes = []
        self.spheres = []
        self.lights = []
        self.coordinates = []
        self.internalCoordinates = []
        self.doors = []
    
    def add_light(self, light):

        if light not in self.lights:
            self.lights.append(light)
    
    def add_sphere(self, sphere):

        if sphere not in self.spheres:
            self.spheres.append(sphere)