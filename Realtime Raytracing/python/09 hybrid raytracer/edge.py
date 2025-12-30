NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

class Edge:

    def __init__(self, id):

        self.id = id
        self.point_a = None
        self.point_b = None
        self.convex = None
        self.type = None
        self.edge_a = None
        self.edge_b = None
