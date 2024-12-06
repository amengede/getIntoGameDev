from config import *
from constants import *

class SimpleComponent:


    def __init__(self, position, eulers, mesh_type, material_type):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.mesh_type = mesh_type
        self.material_type = material_type
    
    def update(self):
        
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self.eulers), dtype=np.float32
            )
        )
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )
        
class BillBoardComponent:

    def __init__(self, position, mesh_type, material_type):

        self.position = np.array(position, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.mesh_type = mesh_type
        self.material_type = material_type
    
    def update(self, playerPosition):
        
        directionFromPlayer = self.position - playerPosition
        angle1 = np.arctan2(-directionFromPlayer[1],directionFromPlayer[0])
        dist2d = math.sqrt(directionFromPlayer[0] ** 2 + directionFromPlayer[1] ** 2)
        angle2 = np.arctan2(directionFromPlayer[2],dist2d)

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_y_rotation(theta=angle2, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
           self.modelTransform,
            pyrr.matrix44.create_from_z_rotation(theta=angle1, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        )

class BrightBillboard:


    def __init__(self, position, color, strength, mesh_type, material_type):

        self.position = np.array(position, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength
        self.mesh_type = mesh_type
        self.material_type = material_type
    
    def update(self, playerPosition):
        
        directionFromPlayer = self.position - playerPosition
        angle1 = np.arctan2(-directionFromPlayer[1],directionFromPlayer[0])
        dist2d = math.sqrt(directionFromPlayer[0] ** 2 + directionFromPlayer[1] ** 2)
        angle2 = np.arctan2(directionFromPlayer[2],dist2d)

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_y_rotation(theta=angle2, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
           self.modelTransform,
            pyrr.matrix44.create_from_z_rotation(theta=angle1, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        )

class Player:


    def __init__(self, position, mesh_type, material_type):

        self.position = np.array(position, dtype = np.float32)
        self.theta = 0
        self.phi = 0
        self.update_vectors()
        self.mesh_type = mesh_type
        self.material_type = material_type
    
    def update_vectors(self):

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_x_rotation(
                theta=np.radians(self.phi), dtype=np.float32
            )
        )
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_z_rotation(
                theta=np.radians(270 - self.theta), dtype=np.float32
            )
        )
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.phi))
            ],
            dtype = np.float32
        )

        globalUp = np.array([0,0,1], dtype=np.float32)

        self.right = np.cross(self.forwards, globalUp)

        self.up = np.cross(self.right, self.forwards)

        self.viewTransform = pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up, 
            dtype = np.float32
        )

class Scene:


    def __init__(self):

        self.lit_objects = []
        self.unlit_objects = []

        self.cubes = [
            SimpleComponent(
                position = [-5,-6,1],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = WOOD_MATERIAL
            ),
            SimpleComponent(
                position = [-5,-4,1],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
            SimpleComponent(
                position = [-5,-2,1],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = HOTEL_WALL_MATERIAL
            ),
            SimpleComponent(
                position = [-5,0,1],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = GLASS_WALL_MATERIAL
            ),
            SimpleComponent(
                position = [-5,0,1],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = PLASTER_MATERIAL
            ),
            SimpleComponent(
                position = [-5,0,1],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_BRASS_MATERIAL
            ),
            SimpleComponent(
                position = [-5,0,1],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_COLD_MATERIAL
            ),
            SimpleComponent(
                position = [-3,-6,3],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = WOOD_MATERIAL
            ),
            SimpleComponent(
                position = [-3,-4,3],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
            SimpleComponent(
                position = [-3,-2,3],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = HOTEL_WALL_MATERIAL
            ),
            SimpleComponent(
                position = [-3,0,3],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = GLASS_WALL_MATERIAL
            ),
            SimpleComponent(
                position = [-3,0,3],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = PLASTER_MATERIAL
            ),
            SimpleComponent(
                position = [-3,0,3],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_BRASS_MATERIAL
            ),
            SimpleComponent(
                position = [-3,0,3],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_COLD_MATERIAL
            ),
            SimpleComponent(
                position = [-1,-6,5],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = WOOD_MATERIAL
            ),
            SimpleComponent(
                position = [-1,-4,5],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
            SimpleComponent(
                position = [-1,-2,5],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = HOTEL_WALL_MATERIAL
            ),
            SimpleComponent(
                position = [-1,0,5],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = GLASS_WALL_MATERIAL
            ),
            SimpleComponent(
                position = [-1,0,5],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = PLASTER_MATERIAL
            ),
            SimpleComponent(
                position = [-1,0,5],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_BRASS_MATERIAL
            ),
            SimpleComponent(
                position = [-1,0,5],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_COLD_MATERIAL
            ),
            SimpleComponent(
                position = [1,-6,7],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = WOOD_MATERIAL
            ),
            SimpleComponent(
                position = [1,-4,7],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
            SimpleComponent(
                position = [1,-2,7],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = HOTEL_WALL_MATERIAL
            ),
            SimpleComponent(
                position = [1,0,7],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = GLASS_WALL_MATERIAL
            ),
            SimpleComponent(
                position = [1,0,7],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = PLASTER_MATERIAL
            ),
            SimpleComponent(
                position = [1,0,7],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_BRASS_MATERIAL
            ),
            SimpleComponent(
                position = [1,0,7],
                eulers = [0,0,0],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_COLD_MATERIAL
            )
        ]

        self.medkits = [
            BillBoardComponent(
                position = [3,0,0.5],
                mesh_type = MEDKIT_MESH,
                material_type = MEDKIT_MATERIAL
            )
        ]

        self.smoke_clouds = []
        for _ in range(100):

            x = 10 * (1 - 2 * np.random.random())
            y = 10 * (1 - 2 * np.random.random())
            z = 2 * np.random.random()

        self.containers = [
            SimpleComponent(
                position = [0,0,0],
                eulers = [0,0,0],
                mesh_type = CONTAINER_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
        ]

        self.lights = [
            BrightBillboard(
                position = [
                    4.0, 
                    -4.0 + i, 
                    1.0
                ],
                color = [
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0)
                ],
                strength = 3,
                mesh_type = LIGHT_MESH,
                material_type = LIGHT_MATERIAL
            )
            for i in range(8)
        ]

        self.player = Player(
            position = [0,0,2],
            mesh_type = MONKEY_MESH,
            material_type = WOOD_MATERIAL
        )

        for obj in self.cubes:
            self.lit_objects.append(obj)
        
        for obj in self.containers:
            self.lit_objects.append(obj)
        
        for obj in self.lights:
            self.unlit_objects.append(obj)

        for obj in self.medkits:
            self.lit_objects.append(obj)

    def update(self, rate):

        for cube in self.cubes:
            cube.update()
        
        for medkit in self.medkits:
            medkit.update(self.player.position)

        for light in self.lights:
            light.update(self.player.position)

        for container in self.containers:
            container.update()
        
        self.player.update_vectors()
    
    def move_player(self, dPos):

        dPos = 0.4 * np.array(dPos, dtype = np.float32)
        self.player.position += dPos
    
    def spin_player(self, dTheta, dPhi):

        self.player.theta += 0.4 * dTheta
        if self.player.theta > 360:
            self.player.theta -= 360
        elif self.player.theta < 0:
            self.player.theta += 360
        
        self.player.phi = min(
            89, max(-89, self.player.phi + 0.4 * dPhi)
        )