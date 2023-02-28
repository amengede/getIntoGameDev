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
    
    def has_point(self, pos):

        if (self.center[0] + self.l / 2) < pos[0]:
            return False

        if (self.center[0] - self.l / 2) > pos[0]:
            return False
        
        if (self.center[1] + self.w / 2) < pos[1]:
            return False

        if (self.center[1] - self.w / 2) > pos[1]:
            return False
        
        if (self.center[2] + self.h / 2) < pos[2]:
            return False

        if (self.center[2] - self.h / 2) > pos[2]:
            return False
        
        return True

class Grid:


    def __init__(self):

        self.length = 10
        self.width = 10
        self.height = 10

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

    def expand(self, box, temporary_box, coord, searched):

        result = []
        x = coord[0]
        y = coord[1]
        z = coord[2]

        expand_north = (box.center[1] + box.w / 2) > (temporary_box.center[1] + temporary_box.w / 2)
        expand_east = (box.center[0] + box.l / 2) > (temporary_box.center[0] + temporary_box.l / 2)
        expand_south = (box.center[1] - box.w / 2) < (temporary_box.center[1] - temporary_box.w / 2)
        expand_west = (box.center[1] - box.l / 2) < (temporary_box.center[0] - temporary_box.l / 2)
        expand_above = (box.center[2] + box.h / 2) > (temporary_box.center[2] + temporary_box.h / 2)
        expand_below = (box.center[2] - box.h / 2) < (temporary_box.center[2] - temporary_box.h / 2)
        if expand_north:
            #North
            if (x, y + 1, z) not in searched:
                result.append((x, y + 1, z))
            
            if expand_east:
                #North East
                if (x + 1, y + 1, z) not in searched:
                    result.append((x + 1, y + 1, z))
                
                if expand_above:
                    #North East Above
                    if (x + 1, y + 1, z + 1) not in searched:
                        result.append((x + 1, y + 1, z + 1))
                
                if expand_below:
                    #North East Below
                    if (x + 1, y + 1, z - 1) not in searched:
                        result.append((x + 1, y + 1, z - 1))
            
            if expand_west:
                #North West
                if (x - 1, y + 1, z) not in searched:
                    result.append((x - 1, y + 1, z))

                if expand_above:
                    #North West Above
                    if (x - 1, y + 1, z + 1) not in searched:
                        result.append((x - 1, y + 1, z + 1))
                
                if expand_below:
                    #North West Below
                    if (x - 1, y + 1, z - 1) not in searched:
                        result.append((x - 1, y + 1, z - 1))
            
            if expand_above:
                #North Above
                if (x, y + 1, z + 1) not in searched:
                    result.append((x, y + 1, z + 1))
            
            if expand_below:
                #North Below
                if (x, y + 1, z - 1) not in searched:
                    result.append((x, y + 1, z - 1))
        
        if expand_south:
            #South
            if (x, y - 1, z) not in searched:
                result.append((x, y - 1, z))
            
            if expand_east:
                #South East
                if (x + 1, y - 1, z) not in searched:
                    result.append((x + 1, y - 1, z))
                
                if expand_above:
                    #South East Above
                    if (x + 1, y - 1, z + 1) not in searched:
                        result.append((x + 1, y - 1, z + 1))
                
                if expand_below:
                    #South East Below
                    if (x + 1, y - 1, z - 1) not in searched:
                        result.append((x + 1, y - 1, z - 1))
            
            if expand_west:
                #South West
                if (x - 1, y - 1, z) not in searched:
                    result.append((x - 1, y - 1, z))
                
                if expand_above:
                    #South West Above
                    if (x - 1, y - 1, z + 1) not in searched:
                        result.append((x - 1, y - 1, z + 1))
                
                if expand_below:
                    #South West Below
                    if (x - 1, y - 1, z - 1) not in searched:
                        result.append((x - 1, y - 1, z - 1))
            
            if expand_above:
                #South Above
                if (x, y - 1, z + 1) not in searched:
                    result.append((x, y - 1, z + 1))
            
            if expand_below:
                #South Below
                if (x, y - 1, z - 1) not in searched:
                    result.append((x, y - 1, z - 1))
        
        if expand_east:
            #East
            if (x + 1, y, z) not in searched:
                result.append((x + 1, y, z))
            
            if expand_above:
                #East Above
                if (x + 1, y, z + 1) not in searched:
                    result.append((x + 1, y, z + 1))
            
            if expand_below:
                #East Below
                if (x + 1, y, z - 1) not in searched:
                    result.append((x + 1, y, z - 1))

        if expand_west:
            #West
            if (x - 1, y, z) not in searched:
                result.append((x - 1, y, z))
            
            if expand_below:
                #West Below
                if (x - 1, y, z - 1) not in searched:
                    result.append((x - 1, y, z - 1))
            
            if expand_above:
                #West Above
                if (x - 1, y, z + 1) not in searched:
                    result.append((x - 1, y, z + 1))
        
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
                for coord in self.expand(box, temporary_box, current, searched):
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
    
    def intersects_anything(self, obj, coords):

        for coord in coords:

            if coord not in self.items:
                return False
        
            for obj2 in self.items[coord]:

                if obj == obj2:
                    continue
                
                if obj.box.overlaps_with(obj2.box):
                    return True
        
        return False
    
    def can_move(self, obj, velocity):

        box = obj.box
        tempBox = Box3D(box.l, box.w, box.h, box.center + velocity)

        for coord in box.coords:

            if self.intersects_something(obj, tempBox, coord):
                return False
        
        return True
    
    def get_overlapping_objects(self, obj):

        box = obj.box
        overlapping_objects = []

        for coord in box.coords:
            
            if coord not in self.items:
                continue
                
            for obj2 in self.items[coord]:
                if obj == obj2:
                    continue

                if box.overlaps_with(obj2.box):
                    overlapping_objects.append(obj2)
        
        return overlapping_objects
    
    def expand_quick(self, box, direction):

        test_coords = box.coords.copy()
        for coord in box.coords:
            test_coord = (coord[0] + direction[0], coord[1] + direction[1], coord[2] + direction[2])
            if test_coord not in test_coords:
                test_coords.append(test_coord)
        return test_coords

    def move(self, obj, dt):

        velocity = dt * obj.velocity
        box = obj.box

        box.coords = self.expand_quick(box, (np.sign(velocity[0]), 0, 0))
        test_velocity = np.array([velocity[0], 0, 0], dtype=np.float32)
        if self.can_move(obj, test_velocity):
            box.center += test_velocity
        
        box.coords = self.expand_quick(box, (0, np.sign(velocity[1]), 0))
        test_velocity = np.array([0, velocity[1], 0], dtype=np.float32)
        if self.can_move(obj, test_velocity):
            box.center += test_velocity
        
        box.coords = self.expand_quick(box, (0, 0, np.sign(velocity[2])))
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

        overlapping_objects = self.get_overlapping_objects(obj)
        if len(overlapping_objects) > 0:
            box2 = overlapping_objects[0].box
            box.center[2] = box2.center[2] + box2.h / 2 + box.h / 2
            obj.on_ground = True

    def get_length_to_hit(self, pos, direction, length_min, length_max):

        length = length_min / 2
        length_increment = length_min / 2

        while length < length_max:

            length += length_increment
            test_pos = pos + length * direction

            grid_pos = self.world_to_grid(test_pos)

            if test_pos[2] <= 0.9:
                return length

            if grid_pos not in self.items:
                continue

            for obj in self.items[grid_pos]:
                if obj.box.has_point(test_pos):
                    return length
        
        return length_max

grid = Grid()