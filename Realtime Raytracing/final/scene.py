from config import *
import material
import door
import room
import plane
import sphere
import camera

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """

        self.materials = []
        for r in [0.3, 0.6, 0.9]:
            for g in [0.3, 0.6, 0.9]:
                for b in [0.3, 0.6, 0.9]:
                    self.materials.append(
                        material.Material(
                            color = [r, g, b],
                            reflectance = np.random.uniform(),
                            fuzz = np.random.uniform()
                        )
                    )
        
        self.spheres = [
            sphere.Sphere(
                center = [5.5, 1.5, 1],
                radius = 0.25,
                material=9
            ),
            sphere.Sphere(
                center = [5.75, 1.5, 0.25],
                radius = 0.5,
                material=4
            ),
        ]
        self.camera = camera.Camera(
            position = [1.5, 1.5, 0.5]
        )

        self.map = [
            [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,7,7,7,7,7,7,7,7],
            [4,0,"d",0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
            [4,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
            [4,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,"d",0,0,0,0,0,0,7],
            [4,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
            [4,0,4,0,0,0,0,5,5,5,5,5,5,5,5,5,7,7,"d",7,7,7,7,7],
            [4,0,5,0,0,0,0,5,0,5,0,5,0,5,0,5,7,0,0,0,7,7,7,1],
            [4,0,6,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,8],
            [4,0,7,0,0,0,0,"d",0,0,0,0,0,0,0,"d",0,0,0,0,7,7,7,1],
            [4,0,8,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,8],
            [4,0,"d",0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,7,7,7,1],
            [4,0,6,0,0,0,0,5,5,5,5,"d",5,5,5,5,7,7,7,7,7,7,7,1],
            [6,6,6,6,6,6,6,6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6],
            [8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4],
            [6,6,6,6,6,6,"d",6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6],
            [4,4,4,4,4,4,0,4,4,4,6,0,6,2,2,2,2,2,2,2,3,3,3,3],
            [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2],
            [4,0,0,0,0,0,0,0,0,0,"d",0,6,2,0,0,5,0,0,2,0,0,0,2],
            [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2],
            [4,0,6,0,6,0,0,0,0,4,6,0,"d",0,0,0,5,0,0,"d",0,0,0,2],
            [4,0,0,5,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2],
            [4,0,6,0,6,0,0,0,0,4,6,0,6,2,0,0,5,0,0,2,0,0,0,2],
            [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2],
            [4,4,4,4,4,4,4,4,4,4,1,1,1,2,2,2,2,2,2,3,3,3,3,3]
        ]

        self.rows = len(self.map)
        self.cols = len(self.map[0])

        self.geometry = get_lumped_geometry_from(self.map)

        self.planes = [
            plane.Plane(
                normal = [0, 0, 1],
                tangent = [-1, 0, 0],
                bitangent = [0, -1, 0],
                uMin = -(self.cols - 2)/2,
                uMax = (self.cols - 2)/2,
                vMin = -(self.rows - 2)/2,
                vMax = (self.rows - 2)/2,
                center = [self.cols/2,self.rows/2,0],
                material = 0
            ),
            plane.Plane(
                normal = [0, 0, -1],
                tangent = [1, 0, 0],
                bitangent = [0, -1, 0],
                uMin = -(self.cols - 2)/2,
                uMax = (self.cols - 2)/2,
                vMin = -(self.rows - 2)/2,
                vMax = (self.rows - 2)/2,
                center = [self.cols/2,self.rows/2,1],
                material = 10
            )
        ]

        self.rooms = []
        self.doors = []

        self.make_rooms()

        for _room in self.rooms:

            for coordinate in _room.coordinates:

                row,col = coordinate
                
                for _plane in self.get_geometry_at_point(row, col, self.rows):
                    _room.planes.append(_plane)
        
        self.active_rooms = [self.rooms[0],]
        self.outdated = True
        self.update()
                
    def get_geometry_at_point(self, row, col, rows):

        result = []

        if self.geometry[row][col] & 1:
            result.append(self.make_north_wall(row, col, self.map[row][col]))
                
        if self.geometry[row][col] & 2:
            result.append(self.make_east_wall(row, col, self.map[row][col]))
                
        if self.geometry[row][col] & 4:
            result.append(self.make_south_wall(row, col, self.map[row][col]))

        if self.geometry[row][col] & 8:
            result.append(self.make_west_wall(row, col, self.map[row][col]))
        
        return result

    def make_rooms(self):

        coordinates_to_expand = []
        expanded_coordinates = []
        empty_blocks = (0, "d")

        #get the first open block to search from
        starting_coordinate = self.get_new_room(expanded_coordinates)
        while starting_coordinate is not None:
            coordinates_to_expand.append(starting_coordinate)
            #doors can be expanded on both sides
            for i,coordinate in enumerate(expanded_coordinates):
                row, col = coordinate
                if self.map[row][col] == "d":
                    expanded_coordinates.pop(i)
            newRoom = room.Room()
        
            #expand each coordinate
            while len(coordinates_to_expand) > 0:

                searched_coordinate = coordinates_to_expand.pop(0)
                if searched_coordinate in expanded_coordinates:
                    continue
                expanded_coordinates.append(searched_coordinate)
                neighbors = self.expand(searched_coordinate, expanded_coordinates)
                
                for coordinate in neighbors:
                    row,col = coordinate
                    if self.map[row][col] in empty_blocks:
                        if coordinate not in expanded_coordinates:
                            coordinates_to_expand.append(coordinate)
                        if self.map[row][col] == "d":
                            alreadyExists = False
                            for _door in self.doors:
                                if coordinate == _door.coordinate:
                                    alreadyExists = True
                            if not alreadyExists:
                                newDoor = door.Door(coordinate)
                                newDoor.planes.append(self.make_north_wall(row, col, 9))
                                newDoor.planes.append(self.make_east_wall(row, col, 9))
                                newDoor.planes.append(self.make_south_wall(row, col, 9))
                                newDoor.planes.append(self.make_west_wall(row, col, 9))
                                if self.map[row+1][col] not in empty_blocks:
                                    #horizontal, add top and bottom
                                    newDoor.planes.append(self.make_north_wall(row + 1, col, 9))
                                    newDoor.planes.append(self.make_south_wall(row - 1, col, 9))
                                else:
                                    #vertical, add left and right
                                    newDoor.planes.append(self.make_east_wall(row, col - 1, 9))
                                    newDoor.planes.append(self.make_west_wall(row, col + 1, 9))
                                self.doors.append(newDoor)
                                newRoom.doors.append(newDoor)
                            else:
                                newDoor = self.get_door_by_coordinate(coordinate)
                                newRoom.doors.append(newDoor)

                        if coordinate not in newRoom.internalCoordinates:
                            newRoom.internalCoordinates.append(coordinate)

                    elif coordinate not in newRoom.coordinates:
                        newRoom.coordinates.append(coordinate)

            self.rooms.append(newRoom)
            starting_coordinate = self.get_new_room(expanded_coordinates)
    
    def get_door_by_coordinate(self, coordinate):

        for _door in self.doors:
            if _door.coordinate == coordinate:
                return _door
    
    def get_new_room(self, expanded_coordinates):

        #get dimensions of map
        rows = len(self.map)
        cols = len(self.map[0])

        for row in range(rows):
            for col in range(cols):
                if self.map[row][col] == 0:
                    possible_solution = (row,col)
                    if possible_solution not in expanded_coordinates:
                        return possible_solution
        return None
    
    def expand(self, coordinate, expanded_coordinates):

        coordinates = []

        rows = len(self.map)
        cols = len(self.map[0])
        
        row,col = coordinate

        onDoor = self.map[row][col] == "d"

        if row > 0:
            if (not onDoor) \
                or (onDoor and self.map[row - 1][col] != 0) \
                and coordinate not in expanded_coordinates:
                coordinates.append((row - 1, col))
        if row < rows - 1:
            if (not onDoor) \
                or (onDoor and self.map[row + 1][col] != 0) \
                and coordinate not in expanded_coordinates:
                coordinates.append((row + 1, col))
        if col > 0:
            if (not onDoor) \
                or (onDoor and self.map[row][col - 1] != 0) \
                and coordinate not in expanded_coordinates:
                coordinates.append((row, col - 1))
        if col < cols - 1:
            if (not onDoor) \
                or (onDoor and self.map[row][col + 1] != 0) \
                and coordinate not in expanded_coordinates:
                coordinates.append((row, col + 1))
        
        return coordinates

    def make_north_wall(self, row, col, material):

        return plane.Plane(
                normal = [0, -1, 0],
                tangent = [-1, 0, 0],
                bitangent = [0, 0, -1],
                uMin = -0.5,
                uMax = 0.5,
                vMin = -0.5,
                vMax = 0.5,
                center = [col + 0.5, row, 0.5],
                material = material
        )
    
    def make_east_wall(self, row, col, material):

        return plane.Plane(
            normal = [1, 0, 0],
            tangent = [0, 1, 0],
            bitangent = [0, 0, 1],
            uMin = -0.5,
            uMax = 0.5,
            vMin = -0.5,
            vMax = 0.5,
            center = [col + 1, row + 0.5, 0.5],
            material = material
        )
    
    def make_south_wall(self, row, col, material):

        return plane.Plane(
            normal = [0, 1, 0],
            tangent = [-1, 0, 0],
            bitangent = [0, 0, 1],
            uMin = -0.5,
            uMax = 0.5,
            vMin = -0.5,
            vMax = 0.5,
            center = [col + 0.5, row + 1, 0.5],
            material = material
        )
    
    def make_west_wall(self, row, col, material):

        return plane.Plane(
            normal = [-1, 0, 0],
            tangent = [0, 1, 0],
            bitangent = [0, 0, -1],
            uMin = -0.5,
            uMax = 0.5,
            vMin = -0.5,
            vMax = 0.5,
            center = [col, row + 0.5, 0.5],
            material = material
        )
    
    def move_player(self, forwardsSpeed, rightSpeed):
        """
        attempt to move the player with the given speed
        """
        empty_blocks = (0, "d")
        dPos = forwardsSpeed * self.camera.forwards + rightSpeed * self.camera.right
        dx,dy = (dPos[0], dPos[1])

        row = int(self.camera.position[1] + dy)
        col = int(self.camera.position[0])
        if (self.map[row][col] in empty_blocks):
            self.camera.position[1] += dy
        
        row = int(self.camera.position[1])
        col = int(self.camera.position[0] + dx)
        if (self.map[row][col] in empty_blocks):
            self.camera.position[0] += dx
        
    def spin_player(self, dAngle):
        """
            shift the player's direction by the given amount, in degrees
        """
        self.camera.theta += dAngle[0]
        if (self.camera.theta < 0):
            self.camera.theta += 360
        elif (self.camera.theta > 360):
            self.camera.theta -= 360
        
        self.camera.phi += dAngle[1]
        if (self.camera.phi < -89):
            self.camera.phi = -89
        elif (self.camera.phi > 89):
            self.camera.phi = 89
        
        self.camera.recalculateVectors()

    def update(self):

        row = int(self.camera.position[1])
        col = int(self.camera.position[0])
        coordinate = (row,col)

        oldRooms = []
        for room in self.active_rooms:
            oldRooms.append(room)
        
        self.active_rooms = []

        for room in self.rooms:
            if coordinate in room.internalCoordinates:
                self.active_rooms.append(room)
                if room not in oldRooms:
                    #addition of new room
                    self.outdated = True
        
        if not self.outdated:
            for room in oldRooms:
                if room not in self.active_rooms:
                    #removal of old room
                    self.outdated = True