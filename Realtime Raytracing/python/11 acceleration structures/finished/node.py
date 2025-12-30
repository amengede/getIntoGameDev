from config import *

class Node:


    def __init__(self):

        self.min_corner = None
        self.max_corner = None
        self.left_child = -1.0
        self.right_child = -1.0
        self.parent = -1.0
        self.first_sphere_index = 0
        self.sphere_count = 0
        self.index = 0
        self.hit_link = -1.0
        self.miss_link = -1.0
