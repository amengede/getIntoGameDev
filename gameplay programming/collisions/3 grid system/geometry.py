from config import *

class Box3D:

    
    def __init__(self, l, w, h, center):

        self.center = np.array(center, dtype=np.float32)
        self.l = l
        self.w = w
        self.h = h
        self.coords = []
    
    def overlaps_with(self, other):

        if (self.center[0] + self.l / 2) < (other.center[0] - other.l / 2):
            return False

        if (self.center[0] - self.l / 2) > (other.center[0] + other.l / 2):
            return False
        
        if (self.center[1] + self.w / 2) < (other.center[1] - other.w / 2):
            return False

        if (self.center[1] - self.w / 2) > (other.center[1] + other.w / 2):
            return False
        
        if (self.center[2] + self.h / 2) < (other.center[2] - other.h / 2):
            return False

        if (self.center[2] - self.h / 2) > (other.center[2] + other.h / 2):
            return False
        
        return True

class Grid:


    def __init__(self):

        self.length = 8
        self.width = 8
        self.height = 8

        self.items = {}
    
    def world_to_grid(self, coord):

        return (int(coord[0] // self.length), int(coord[1] // self.width), int(coord[2] // self.height))
    
    def grid_to_world(self, coord):

        return ((coord[0] + 0.5) * self.length, (coord[1] + 0.5) * self.width, (coord[2] + 0.5) * self.height)
    
    def remove_from(self, coord, obj):

        if coord not in self.items:
            return
        
        if obj not in self.items[coord]:
            return

        self.items[coord].remove(obj)

        if len(self.items[coord]) == 0:
            self.items.pop(coord)
    
    def add_at(self, coord, obj):

        if coord in self.items:
            
            if obj in self.items[coord]:
                return
            
            self.items[coord].append(obj)
        
        else:

            self.items[coord] = [obj,]

    def expand(self, coord, searched):

        result = []
        x = coord[0]
        y = coord[1]
        z = coord[2]
        #West
        if (x - 1, y, z) not in searched:
            result.append((x - 1, y, z))
        #East
        if (x + 1, y, z) not in searched:
            result.append((x + 1, y, z))
        #South
        if (x, y - 1, z) not in searched:
            result.append((x, y - 1, z))
        #North
        if (x, y + 1, z) not in searched:
            result.append((x, y + 1, z))
        #North West
        if (x - 1, y + 1, z) not in searched:
            result.append((x - 1, y + 1, z))
        #North East
        if (x + 1, y + 1, z) not in searched:
            result.append((x + 1, y + 1, z))
        #South East
        if (x + 1, y - 1, z) not in searched:
            result.append((x + 1, y - 1, z))
        #South West
        if (x - 1, y - 1, z) not in searched:
            result.append((x - 1, y - 1, z))
        
        #West Below
        if (x - 1, y, z - 1) not in searched:
            result.append((x - 1, y, z - 1))
        #East Below
        if (x + 1, y, z - 1) not in searched:
            result.append((x + 1, y, z - 1))
        #South Below
        if (x, y - 1, z - 1) not in searched:
            result.append((x, y - 1, z - 1))
        #North Below
        if (x, y + 1, z - 1) not in searched:
            result.append((x, y + 1, z - 1))
        #North West Below
        if (x - 1, y + 1, z - 1) not in searched:
            result.append((x - 1, y + 1, z - 1))
        #North East Below
        if (x + 1, y + 1, z - 1) not in searched:
            result.append((x + 1, y + 1, z - 1))
        #South East Below
        if (x + 1, y - 1, z - 1) not in searched:
            result.append((x + 1, y - 1, z - 1))
        #South West Below
        if (x - 1, y - 1, z - 1) not in searched:
            result.append((x - 1, y - 1, z - 1))
        
        #West Above
        if (x - 1, y, z + 1) not in searched:
            result.append((x - 1, y, z + 1))
        #East Above
        if (x + 1, y, z + 1) not in searched:
            result.append((x + 1, y, z + 1))
        #South Above
        if (x, y - 1, z + 1) not in searched:
            result.append((x, y - 1, z + 1))
        #North Above
        if (x, y + 1, z + 1) not in searched:
            result.append((x, y + 1, z + 1))
        #North West Above
        if (x - 1, y + 1, z + 1) not in searched:
            result.append((x - 1, y + 1, z + 1))
        #North East Above
        if (x + 1, y + 1, z + 1) not in searched:
            result.append((x + 1, y + 1, z + 1))
        #South East Above
        if (x + 1, y - 1, z + 1) not in searched:
            result.append((x + 1, y - 1, z + 1))
        #South West Above
        if (x - 1, y - 1, z + 1) not in searched:
            result.append((x - 1, y - 1, z + 1))
        
        return result
        
    def get_overlapping_coordinates(self, box):

        world_coord = box.center
        grid_coord = self.world_to_grid(world_coord)

        to_search = [grid_coord,]
        current = None
        searched = []
        overlapping_coords = []

        while len(to_search) > 0:

            current = to_search.pop(0)
            searched.append(current)
            world_coord = self.grid_to_world(current)
            temporary_box = Box3D(self.length, self.width, self.height, world_coord)

            if temporary_box.overlaps_with(box):
                overlapping_coords.append(current)
                for coord in self.expand(current, searched):
                    to_search.append(coord)
        
        return overlapping_coords
    
    def add(self, obj):

        covered_coordinates = self.get_overlapping_coordinates(obj.box)

        for coord in covered_coordinates:
            self.add_at(coord, obj)
        
        obj.box.coords = covered_coordinates
    
    def intersects_something(self, obj, tempBox, coord):

        if coord not in self.items:
            return False
        
        for obj2 in self.items[coord]:

            if obj == obj2:
                continue
        
            obj2.color = np.array([1, 0, 0], dtype=np.float32)
                
            if tempBox.overlaps_with(obj2.box):
                return True
        
        return False
    
    def can_move(self, obj, velocity):

        box = obj.box
        tempBox = Box3D(box.l, box.w, box.h, box.center + velocity)

        for coord in box.coords:

            if self.intersects_something(obj, tempBox, coord):
                return False
        
        return True
    
    def move(self, obj, dt):

        velocity = dt * obj.velocity
        box = obj.box

        test_velocity = np.array([velocity[0], 0, 0], dtype=np.float32)
        if self.can_move(obj, test_velocity):
            box.center += test_velocity
        
        test_velocity = np.array([0, velocity[1], 0], dtype=np.float32)
        if self.can_move(obj, test_velocity):
            box.center += test_velocity
        
        test_velocity = np.array([0, 0, velocity[2]], dtype=np.float32)
        if self.can_move(obj, test_velocity):
            box.center += test_velocity
        elif velocity[2] < 0:
            obj.velocity = 0 * obj.velocity
            obj.on_ground = True
        
        if box.center[2] <= 0.9:
            box.center[2] = 0.9
            obj.on_ground = True
        
        newCoords = self.get_overlapping_coordinates(box)
        for coord in newCoords:
            if coord not in box.coords:
                self.add_at(coord, obj)
        
        for coord in box.coords:
            if coord not in newCoords:
                self.remove_from(coord, obj)
        
        box.coords = newCoords

grid = Grid()