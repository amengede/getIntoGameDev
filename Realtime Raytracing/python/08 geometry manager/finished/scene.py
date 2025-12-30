from config import *
import sphere
import camera
import light
import geometry
import room
import plane

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """

        """
            Map data
        """
        self.wall_geometry = [
            [6, 6, 6, 6,  6,  6, 1, 1],
            [6, 0, 0, 0,  0,  6, 1, 1],
            [6, 6, 6, 6, "d", 6, 1, 1],
            [1, 1, 1, 9,  0,  9, 1, 1],
            [9, 9, 1, 1, "d", 1, 1, 3],
            [9, 0, 0, 0,  0,  0, 0, 3],
            [9, 0, 0, 0,  0,  0, 0, 3],
            [9, 9, 3, 1,  1,  1, 3, 3]
        ]
        self.floor_geometry = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 4, 4, 4, 4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 9, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 5, 5, 5, 5, 5, 0],
            [0, 5, 5, 5, 5, 5, 5, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.ceiling_geometry = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 2, 2, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 9, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 7, 7, 7, 7, 7, 7, 0],
            [0, 7, 7, 7, 7, 7, 7, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        self.spheres = [
            sphere.Sphere(
                center = (2.5, 1.5, 0.3),
                radius = 0.1,
                color = (0.5, 1, 0.3),
                roughness = 0.2,
                axis = (0,0,1),
                radius_of_motion= 0.2,
                velocity=0.1
            ),
            sphere.Sphere(
                center = (3.35, 6.5, 0.1),
                radius = 0.1,
                color = (1, 0, 0),
                roughness = 0.2,
                axis = (0,0,1),
                radius_of_motion= 0,
                velocity=0
            ),
            sphere.Sphere(
                center = (3.5, 6.35, 0.1),
                radius = 0.1,
                color = (0, 1, 0),
                roughness = 0.2,
                axis = (0,0,1),
                radius_of_motion= 0,
                velocity=0
            ),
            sphere.Sphere(
                center = (3.65, 6.5, 0.1),
                radius = 0.1,
                color = (0, 0, 1),
                roughness = 0.2,
                axis = (0,0,1),
                radius_of_motion= 0,
                velocity=0
            ),
            sphere.Sphere(
                center = (3.5, 6.65, 0.1),
                radius = 0.1,
                color = (1, 0, 1),
                roughness = 0.2,
                axis = (0,0,1),
                radius_of_motion= 0,
                velocity=0
            ),
            sphere.Sphere(
                center = (3.5, 6.5, 0.225),
                radius = 0.1,
                color = (1, 1, 0),
                roughness = 0.2,
                axis = (0,0,1),
                radius_of_motion= 0,
                velocity=0
            )
        ]

        self.lights = [
            light.Light(
                position = (3.5, 1.5, 0.7),
                color = (0, 0.75, 1),
                strength = 1,
                axis = (1, 0, 0.1),
                radius = 1,
                velocity = 0.05
            ),
            light.Light(
                position = (4.5, 3.5, 0.1),
                color = (1, 0, 0),
                strength = 1,
                axis = (1, 0, 0.1),
                radius = 0,
                velocity = 0
            ),
            light.Light(
                position = (2, 6, 0.5),
                color = (0, 0, 1),
                strength = 1,
                axis = (0, 0, 0.3),
                radius = 1,
                velocity = 0.025
            ),
            light.Light(
                position = (5, 6, 0.5),
                color = (1, 0, 0),
                strength = 1,
                axis = (0, 0, 0.3),
                radius = 1,
                velocity = 0.05
            )
        ]

        self.rooms = []

        self.doors = []

        self.planes = []

        self.room_lookup = {}
        
        self.camera = camera.Camera(
            position = [1.5, 1.5, 0.5]
        )

        self.outDated = True

        self.make_level()

        self.send_objects_to_rooms()
    
    def make_level(self):

        geometry.make_rooms(
            walls = self.wall_geometry, doors = self.doors, rooms = self.rooms
        )

        wall_mask = geometry.get_lumped_geometry_from(self.wall_geometry)

        for _room in self.rooms:

            for coordinate in _room.coordinates:

                row,col = coordinate

                geometry.get_geometry_at_point(
                    row, col, _room, wall_mask, 
                    self.wall_geometry, self.floor_geometry, self.ceiling_geometry
                )
            
            for coordinate in _room.internalCoordinates:

                row,col = coordinate
                self.room_lookup[coordinate] = _room

                geometry.get_geometry_at_point(
                    row, col, _room, wall_mask, 
                    self.wall_geometry, self.floor_geometry, self.ceiling_geometry
                )
        
        self.active_rooms = [self.rooms[0],]

    def send_objects_to_rooms(self):

        while len(self.lights) > 0:

            _light = self.lights.pop()
            coordinate = (int(_light.position[1]), int(_light.position[0]))
            _room = self.room_lookup[coordinate]
            _room.add_light(_light)
        
        while len(self.spheres) > 0:

            _sphere = self.spheres.pop()
            coordinate = (int(_sphere.center[1]), int(_sphere.center[0]))
            _room = self.room_lookup[coordinate]
            _room.add_sphere(_sphere)
    
    def move_player(self, forwardsSpeed, rightSpeed):
        """
        attempt to move the player with the given speed
        """
        
        empty_blocks = (0, "d")
        dPos = forwardsSpeed * self.camera.forwards + rightSpeed * self.camera.right
        dx,dy = (dPos[0], dPos[1])

        row = int(self.camera.position[1] + 1.1 * dy)
        col = int(self.camera.position[0])
        if (self.wall_geometry[row][col] in empty_blocks):
            self.camera.position[1] += dy
        
        row = int(self.camera.position[1])
        col = int(self.camera.position[0] + 1.1 * dx)
        if (self.wall_geometry[row][col] in empty_blocks):
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

    def update(self, rate):

        row = int(self.camera.position[1])
        col = int(self.camera.position[0])
        coordinate = (row,col)
        
        self.active_rooms = []

        for room in self.rooms:
            if coordinate in room.internalCoordinates:
                self.active_rooms.append(room)
            
                for _light in room.lights:
                    _light.update(rate)
                
                for _sphere in room.spheres:
                    _sphere.update(rate)
        
        self.outDated = True