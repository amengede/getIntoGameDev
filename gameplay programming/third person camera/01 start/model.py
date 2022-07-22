from config import *

class Player:

    def __init__(self, position):

        self.position = np.array(position,dtype=np.float32)
        self.theta = 0
        self.modelTransform = pyrr.matrix44.create_from_translation(vec = self.position, dtype = np.float32)

    def move(self, direction, amount):

        walkDirection = (direction + self.theta) % 360
        self.position[0] += amount * np.cos(np.radians(walkDirection),dtype=np.float32)
        self.position[1] += amount * np.sin(np.radians(walkDirection),dtype=np.float32)

        self.modelTransform = pyrr.matrix44.create_from_translation(vec = self.position, dtype = np.float32)

class Camera:

    def __init__(self, position):

        self.position = np.array(position,dtype=np.float32)
        self.forward = np.array([0, 0, 0],dtype=np.float32)
        self.right = np.array([0, 0, 0],dtype=np.float32)
        self.up = np.array([0, 0, 0],dtype=np.float32)
        self.global_up = np.array([0, 0, 1], dtype=np.float32)

    def update(self):
        
        self.forward = pyrr.vector.normalize(-self.position)
        self.right = pyrr.vector.normalize(pyrr.vector3.cross(self.global_up,self.forward))
        self.up = pyrr.vector.normalize(pyrr.vector3.cross(self.forward,self.right))

        self.viewTransform = pyrr.matrix44.create_look_at(
            eye = self.position, target = self.position + self.forward, 
            up = self.up, dtype=np.float32
        )

class Ground:

    def __init__(self, z):

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)

        self.z = z

    def update(self, playerPos):

        position = np.array([playerPos[0], playerPos[1], self.z], dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_from_translation(
            vec = position, dtype = np.float32
        )

class Scene:

    def __init__(self):

        self.create_objects()

    def create_objects(self):
        
        self.player = Player(position = [0,0,0.9])
        self.camera = Camera(position = [-7.2,0,3.6])
        self.ground = Ground(z = 0)

    def update(self):

        self.ground.update(playerPos=self.player.position)
        self.camera.update()

    def move_player(self, direction, amount):

        self.player.move(direction, amount)